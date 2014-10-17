# coding:utf8
import logging

from datetime import datetime, timedelta

from django.db import models
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.auth.admin import User
from django.utils.translation import ugettext, ugettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType


_logger = logging.getLogger(__name__)


COMMON_USER = 'common_user'
MONTHLY_USER = 'monthly_user'
HISTORY_LIMIT = 50
BOOKMARK_LIMIT = 50
SECTIONMARK_LIMIT = 50
RESERVATION_LIMIT = 50

USER_TYPE = ((COMMON_USER, _('COMMON USER')),
             (MONTHLY_USER, _('MONTHYLY USER')),
             )

TRADE_TYPE = (('recharge', _('Recharge')),
              ('consume', _('Consume')),
              )

PAY_TYPE = ((0, _('Cash')),
            (1, _('Balance')),
            )



class Profile(models.Model):
    user = models.OneToOneField(User, verbose_name=_('User'))
    voucher = models.PositiveIntegerField(_("Voucher"), default=0)
    user_type = models.CharField(_("USER TYPE"), max_length=100, choices=USER_TYPE, default="common_user")
    device_id = models.CharField(_("Device ID"), max_length=100)
    ip = models.CharField(_("IP"), max_length=32)
    register_date = models.DateTimeField(_("Register at"), auto_now=True)
    profile = models.TextField(_("Profile"))
    source = models.PositiveIntegerField(verbose_name=_('Source'), null=True)

    class Meta:
        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')
        app_label = 'accounts'

    def __unicode__(self):
        return unicode(self.user)


class VipUser(models.Model):
    user = models.OneToOneField(User, verbose_name=_('User'))
    sn = models.CharField(_('SN'), max_length=32, blank=True, null=True)
    locked = models.BooleanField(_('Locked'), default=False)
    create_date = models.DateTimeField(_('Created at'), auto_now_add=True)
    update_date = models.DateTimeField(_('Updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Vip user')
        verbose_name_plural = _('Vip users')
        ordering = ('-update_date', )
        unique_together = ('user', 'sn')
        app_label = 'accounts'

    def __unicode__(self):
        return unicode('%s-%s' % (self.user, self.sn))


from cord_core_fields import CrossDBForeignKey, CrossDBGenericForeignKey
from expenses_models import PRICE_DURATION_CHOICES
#from cord.assets.models import Item

TRADING_SUCCESS = 1
UNPAYMENT = 2
PAYMENT_FAILURE = 3
TRADING_EXPIRE = 4
SERVICE_END = 5

ORDER_STATE =((UNPAYMENT, _('UNPAYMENT')),
              (TRADING_SUCCESS, _('TRADING SUCCESS')),
              (PAYMENT_FAILURE, _('PAYMENT FAILURE')),
              (SERVICE_END, _('SERVICE END')),
              (TRADING_EXPIRE, _('TRADING EXPIRE')),
              )

class Order(models.Model):
    sn = models.CharField(_(u'订单号'), max_length=100, unique=True)
    user = CrossDBForeignKey(User, verbose_name=_('User'))
    username = models.CharField(max_length=255, blank=True, null=True)
    content_type = CrossDBForeignKey(ContentType)
    object_pk = models.IntegerField()
    content_object = CrossDBGenericForeignKey('default', "content_type", "object_pk")
    valid = models.BooleanField(_("Valid"), default=True)
    state = models.IntegerField(_("State"), choices=ORDER_STATE, default=UNPAYMENT)
    price = models.DecimalField(_("Price"),max_digits=6,decimal_places=1)
    purchase_date = models.DateTimeField(_("Purchased at"),
        blank=True, null=True)
    duration = models.CharField(_("Duration"), max_length=20,choices=PRICE_DURATION_CHOICES)
    expiry_date = models.DateTimeField(_("Expires on"),
        blank=True, null=True)
    source = models.CharField(_("Source"), max_length=16, blank=True, null=True)
    device_id = models.CharField(_("Device ID"), max_length=32, blank=True, null=True)
    create_date = models.DateTimeField(_("Created at"), auto_now_add=True)
    update_date = models.DateTimeField(_("Updated at"), auto_now=True)
    subject = models.CharField(_("Subject"), max_length=200, blank=True, null=True)

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')
        ordering = ('-update_date',)
        app_label = 'accounts'

class Purchase(models.Model):
    order = models.ForeignKey(Order)
    user = CrossDBForeignKey(User, verbose_name=_('User'))
    model_name = models.CharField(_('Model name'), max_length=100, null=True,
                                  blank=True)
    content_type = CrossDBForeignKey(ContentType, null=True, blank=True)
    object_pk = models.IntegerField()
    content_object = CrossDBGenericForeignKey('default', "content_type", "object_pk")
    state = models.IntegerField(_("State"), choices=ORDER_STATE, default=UNPAYMENT)
    create_date = models.DateTimeField(_("Created at"), auto_now_add=True)
    expiry_date = models.DateTimeField(_("Expires on"),
        blank=True, null=True)
    price = models.DecimalField(_("Price"),max_digits=6,decimal_places=1)
    duration = models.CharField(_("Duration"), max_length=20,choices=PRICE_DURATION_CHOICES)
    purchase_date = models.DateTimeField(_("Purchased at"),
        blank=True, null=True)
    update_date = models.DateTimeField(_("Updated at"), auto_now=True)

    class Meta:
        verbose_name = _('Purchase')
        verbose_name_plural = _('Purchases')
        ordering = ('-update_date',)
        app_label = 'accounts'


class LoginHistory(models.Model):
    user = models.ForeignKey(User, verbose_name=_('User'))
    device_id = models.CharField(_("Device ID"), max_length=100, null=True, blank=True)
    ip = models.CharField(_("IP"), max_length=64)
    login_date = models.DateTimeField(_("Logins on"), auto_now=True)

    class Meta:
        verbose_name = _("Login History")
        verbose_name_plural = _("Login Histories")
        ordering = ("-login_date", )
        app_label = 'accounts'

class Account(models.Model):
    user = models.OneToOneField(User, verbose_name=_('User'))
    balance = models.DecimalField(_("Balance"), max_digits=12, decimal_places=2, default=0.0)

    class Meta:
        verbose_name = _('Account')
        verbose_name_plural = _('Accounts')
        app_label = 'accounts'

class TradeHistory(models.Model):
    user = CrossDBForeignKey(User, verbose_name=_('User'))
    amount = models.DecimalField(_("Amount"), max_digits=12, decimal_places=2)
    client_id = models.CharField(_("Client ID"), max_length=32)
    device_id = models.CharField(_('Device ID'), max_length=100)
    order_id = models.IntegerField(_("Order ID"), unique=True)
    pay_type = models.IntegerField(_('Pay type'), choices=PAY_TYPE, default=0)
    trade_type = models.CharField(_('Trade type'), max_length=10, choices=TRADE_TYPE)
    trade_date = models.DateTimeField(_("Recharged at"))
    create_date = models.DateTimeField(_("Created at"), auto_now=True)

    class Meta:
        verbose_name = _("Trade History")
        verbose_name_plural = _("Trade Histories")
        ordering = ('-trade_date', )
        app_label = 'accounts'

class Follow(models.Model):
    sn = models.CharField(_('SN'), max_length=60, null=True)
    user = models.ForeignKey(User, verbose_name=_('User'), null=True)

    ###item = models.ForeignKey(Item, verbose_name=_('Item'))
    position = models.IntegerField(_('Position'))

    update_date = models.DateTimeField(_("Update Date"), auto_now=True)

    def __unicode__(self):
        return "Follow(sn=%s, user=%s, item=%s)" % (self.sn, self.user, self.item)

    class Meta:
        app_label = 'accounts'


PENDING_STATUS_READY = 0
PENDING_STATUS_SUCCEED = 1
PENDING_STATUS_FAILURE = 2
PENDING_STATUS_REVOKED = 3
PENDING_STATUS_EXPIRED = 4
PENDING_STATUS_CLOSED = 5
PENDING_STATUS_CONFIRMED = 6

PENDING_STATUS_CHOICES = (
    (PENDING_STATUS_READY, _('Ready')),
    (PENDING_STATUS_SUCCEED, _('Succeed')),
    (PENDING_STATUS_FAILURE, _('Failure')),
    (PENDING_STATUS_REVOKED, _('Revoked')),
    (PENDING_STATUS_EXPIRED, _('Expired')),
    (PENDING_STATUS_CLOSED, _('Closed')),
    (PENDING_STATUS_CONFIRMED, _('Confirmed')),
)


class PendingPurchase(models.Model):
    uuid = models.CharField(_('UUID'), max_length=36, unique=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    username = models.CharField(_('Username'), max_length=64)
    card_no = models.CharField(_('Card NO'), max_length=32, default='')
    package_pk = models.IntegerField(_('Package PK'))
    status = models.IntegerField(_('Status'), choices=PENDING_STATUS_CHOICES, default=PENDING_STATUS_READY)
    code = models.IntegerField(_('code'), blank=True, null=True)
    order_sn = models.CharField(_('Order SN'), max_length=32, blank=True, null=True)
    purchase_pk = models.CharField(_('Purchase PK'), max_length=32, blank=True, null=True)
    create_date = models.DateTimeField(_("Created at"), auto_now_add=True)
    update_date = models.DateTimeField(_("Updated at"), auto_now=True)

    class Meta:
        verbose_name = _('Pending Purchase')
        verbose_name_plural = _('Pending Purchases')
        ordering = ('-update_date', )
        app_label = 'accounts'


class PendingOrder(models.Model):
    outer_order = models.CharField(_("Outer Order"), max_length=128,
                                   unique=True)
    order_sn = models.CharField(_('Order SN'), max_length=128, blank=True,
                                null=True)
    status = models.IntegerField(_('Status'), choices=PENDING_STATUS_CHOICES,
                                 default=PENDING_STATUS_READY)
    create_date = models.DateTimeField(_("Created at"), auto_now_add=True)
    update_date = models.DateTimeField(_("Updated at"), auto_now=True)

    class Meta:
        verbose_name = _('Pending Order')
        verbose_name_plural = _('Pending Order')
        ordering = ('-update_date', )
        app_label = 'accounts'


