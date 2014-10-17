from django.contrib.contenttypes.generic import GenericRelation, GenericForeignKey
from django.db import models, router
from django.db.models import IntegerField, CharField, FloatField
from django.db.models.signals import post_save, post_delete
from django.db.models.loading import get_model


class BaseGenericRelation(GenericRelation):
    """
    Extends ``GenericRelation`` to:

    - Add a consistent default value for ``object_id_field`` and
      check for a ``related_model`` attribute which can be defined
      on subclasses as a default for the ``to`` argument.

    - Add one or more custom fields to the model that the relation
      field is applied to, and then call a ``related_items_changed``
      method each time related items are saved or deleted, so that a
      calculated value can be stored against the custom fields since
      aggregates aren't available for GenericRelation instances.

    """

    # Mapping of field names to model fields that will be added.
    fields = {}

    def __init__(self, *args, **kwargs):
        """
        Set up some defaults and check for a ``related_model``
        attribute for the ``to`` argument.
        """
        kwargs.setdefault("object_id_field", "object_pk")
        to = getattr(self, "related_model", None)
        if to:
            kwargs.setdefault("to", to)
        super(BaseGenericRelation, self).__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name):
        """
        Add each of the names and fields in the ``fields`` attribute
        to the model the relationship field is applied to, and set up
        the related item save and delete signals for calling
        ``related_items_changed``.
        """
        super(BaseGenericRelation, self).contribute_to_class(cls, name)
        self.related_field_name = name
        # Not applicable to abstract classes, and in fact will break.
        if not cls._meta.abstract:
            for (name_string, field) in self.fields.items():
                if "%s" in name_string:
                    name_string = name_string % name
                if not field.verbose_name:
                    field.verbose_name = self.verbose_name
                cls.add_to_class(name_string, field)
            # For some unknown reason the signal won't be triggered
            # if given a sender arg, particularly when running
            # Cartridge with the field RichTextPage.keywords - so
            # instead of specifying self.rel.to as the sender, we
            # check for it inside the signal itself.
            post_save.connect(self._related_items_changed)
            post_delete.connect(self._related_items_changed)

    def _related_items_changed(self, **kwargs):
        """
        Ensure that the given related item is actually for the model
        this field applies to, and pass the instance to the real
        ``related_items_changed`` handler.
        """
        # Manually check that the instance matches the relation,
        # since we don't specify a sender for the signal.
        if not isinstance(kwargs["instance"], self.rel.to):
            return
        for_model = kwargs["instance"].content_type.model_class()
        if issubclass(for_model, self.model):
            instance = self.model.objects.get(id=kwargs["instance"].object_pk)
            #if hasattr(instance, "get_content_model"):
            #    instance = instance.get_content_model()
            related_manager = getattr(instance, self.related_field_name)
            self.related_items_changed(instance, related_manager)

    def related_items_changed(self, instance, related_manager):
        """
        Can be implemented by subclasses - called whenever the
        state of related items change, eg they're saved or deleted.
        The instance for this field and the related manager for the
        field are passed as arguments.
        """
        pass


class TagsField(BaseGenericRelation):
    """
    Stores the tags as a single string into the ``TAGS_FIELD_string``
    field for convenient access when searching.
    """

    related_model = "core.AssignedTag"
    fields = {"%s_string": CharField(blank=True, max_length=500)}

    def __init__(self, *args, **kwargs):
        """
        Mark the field as editable so that it can be specified in
        admin class fieldsets and pass validation, and also so that
        it shows up in the admin form.
        """
        super(TagsField, self).__init__(*args, **kwargs)
        self.editable = True

    def formfield(self, **kwargs):
        """
        Provide the custom form widget for the admin, since there
        isn't a form field mapped to ``GenericRelation`` model fields.
        """
        from cord.core.forms import TagsWidget
        kwargs["widget"] = TagsWidget()
        return super(TagsField, self).formfield(**kwargs)

    def save_form_data(self, instance, data):
        """
        The ``TagsWidget`` field will return data as a string of
        comma separated IDs for the ``Keyword`` model - convert these
        into actual ``AssignedKeyword`` instances.
        """
        from cord.core.models import AssignedTag
        # Remove current assigned keywords.
        related_manager = getattr(instance, self.name)
        related_manager.all().delete()
        if data:
            data = [AssignedTag(tag_id=i) for i in data.split(",")]
        super(TagsField, self).save_form_data(instance, data)


    def related_items_changed(self, instance, related_manager):
        """
        Stores the tags as a single string for searching.
        """
        if hasattr(instance, "get_content_model"):
            instance = instance.get_content_model()
            related_manager = getattr(instance, self.related_field_name)
        assigned = related_manager.select_related("tag")
        tags = " ".join([unicode(a.tag) for a in assigned])
        string_field_name = self.fields.keys()[0] % self.related_field_name
        if getattr(instance, string_field_name) != tags:
            setattr(instance, string_field_name, tags)
            instance.save()


class RatingField(BaseGenericRelation):
    """
    Stores the average rating against the ``RATING_FIELD_average``
    field when a rating is saved or deleted.
    """

    related_model = "core.Rating"
    fields = {"%s_count": IntegerField(default=0),
              "%s_average": FloatField(default=0),}

    def related_items_changed(self, instance, related_manager):
        """
        Calculates and saves the average rating.
        """
        ratings = [r.value for r in related_manager.all()]
        count = len(ratings)
        average = sum(ratings) / float(count) if count > 0 else 0
        setattr(instance, "%s_count" % self.related_field_name, count)
        setattr(instance, "%s_average" % self.related_field_name, average)
        instance.save()


class CountingField(BaseGenericRelation):
    """
    Stores the counting against the ``COUNTING_FIELD_count`` field.
    """

    related_model = "core.Counting"
    fields = {"%s_count": IntegerField(default=0)}

    def related_items_changed(self, instance, related_manager):
        """
        Calculates and saves the counting.
        """
        counts = [r.count for r in related_manager.all()]
        count = sum(counts)
        setattr(instance, "%s_count" % self.related_field_name, count)
        instance.save()


class CrossDBForeignKey(models.ForeignKey):

    def validate(self, value, model_instance):
        if self.rel.parent_link:
            return
        super(models.ForeignKey, self).validate(value, model_instance)
        if value is None:
            return

        using = router.db_for_read(self.rel.to, instance=model_instance)
        qs = self.rel.to._default_manager.using(using).filter(
                **{self.rel.field_name: value}
             )
        qs = qs.complex_filter(self.rel.limit_choices_to)
        if not qs.exists():
            raise exceptions.ValidationError(self.error_messages['invalid'] % {
                'model': self.rel.to._meta.verbose_name, 'pk': value})


class CrossDBGenericForeignKey(GenericForeignKey):

    def __init__(self, using, ct_field='content_type', fk_field='object_ik'):
        self.using = using
        super(CrossDBGenericForeignKey, self).__init__(ct_field, fk_field)

    def get_content_type(self, obj=None, id=None, using=None):
        ContentType = get_model('contenttypes', 'contenttype')
        if obj:
            return ContentType.objects.db_manager(self.using).get_for_model(obj)
        elif id:
            return ContentType.objects.db_manager(self.using).get_for_id(id)
        else:
            # This should never happen. I love comments like this, don't you?
            raise Exception("Impossible arguments to GFK.get_content_type!")


from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ['^cord\.core\.fields\.CrossDBForeignKey'])
add_introspection_rules([], ['^cord\.core\.fields\.CrossDBGenericForeignKey'])
add_introspection_rules([], ['^cord\.core\.fields\.TagsField'])
add_introspection_rules([], ['^cord\.core\.fields\.RatingField'])
add_introspection_rules([], ['^cord\.core\.fields\.CountingField'])
