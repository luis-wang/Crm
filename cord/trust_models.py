#coding:utf8
from django.db import models
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _


class Device(models.Model):
    """
    cord device model
    """
    sn = models.CharField(_(u'设备SN'), max_length=100)
    manufacture = models.CharField(_('MANUFACTURE'), max_length=20, null=True, blank=True)
    kind = models.CharField(_('DEVICE TYPE'), max_length=20, null=True, blank=True)
    version = models.CharField(_('VERSION'), max_length=20, null=True, blank=True)
    ip = models.CharField(_('IP'), max_length=64, null=True, blank=True)
    site = models.ForeignKey(Site, null=True, blank=True)
    ad_site = models.ForeignKey(Site, null=True, blank=True, related_name='as_ad_site')
    #partner = models.ForeignKey(Partner, null=True, blank=True)
    create_date = models.DateTimeField(_("Created at"), auto_now_add=True)
    update_date = models.DateTimeField(_("Updated at"), auto_now=True)

    class Meta:
        verbose_name = _("Device")
        verbose_name_plural = _("Devices")
        unique_together = (('sn', 'manufacture', 'kind'),)
        ordering = ("-update_date", )
        managed = False
        app_label = 'trust'

