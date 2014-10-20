#coding:utf8
from django.db import models
from django.utils.translation import ugettext_lazy as _

import logging
_logger = logging.getLogger(__name__)

BACKEND_WEIXIN = 1
BACKEND_ALIPAY = 2

BACKEND_CHOICES = (
    (BACKEND_WEIXIN, _("Weixin")),
    (BACKEND_ALIPAY, _("Alipay")),
)

TRANSACTION_READY = 1
TRANSACTION_SUCCEED = 2
TRANSACTION_CLOSED = 3

TRANSACTION_CHOICES = (
    (TRANSACTION_READY, _("Ready")),
    (TRANSACTION_SUCCEED, _("Succeed")),
    (TRANSACTION_CLOSED, _("Closed")),
)

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


class UserOrder(models.Model):
    "peony db"
    trade_no = models.CharField(_("Trade No"), max_length=32)
    user_id = models.IntegerField(_("User Id"))
    username = models.CharField(_("User Name"), max_length=255, blank=True, null=True)
    wares_id = models.IntegerField(_("Wares Id"))
    wares_type = models.CharField(_("Wares Type"), max_length=32)
    valid = models.BooleanField(_("Valid"), default=True)
    state = models.IntegerField(_("State"), choices=ORDER_STATE, default=UNPAYMENT)
    total_fee = models.DecimalField(_("Total Fee"), max_digits=7, decimal_places=2)
    purchase_date = models.DateTimeField(_("Purchased at"), blank=True, null=True)
    duration = models.IntegerField(_("Duration"), blank=True, null=True)
    #start_date = models.DateTimeField(_("Starts on"), blank=True, null=True)
    expiry_date = models.DateTimeField(_("Expires on"), blank=True, null=True)
    payment_expiry_date = models.DateTimeField(_("Payment Expires on"), blank=True, null=True)
    source = models.CharField(_("Source"), max_length=16, blank=True, null=True)
    device_id = models.CharField(_("Device ID"), max_length=32, blank=True, null=True)
    create_date = models.DateTimeField(_("Created at"), auto_now_add=True)
    update_date = models.DateTimeField(_("Updated at"), auto_now=True)
    subject = models.CharField(_("Subject"), max_length=200, blank=True, null=True)
    extra = models.CharField(_("Extra"), max_length=200, blank=True, null=True)
    exchange_info = models.CharField(_("Exchange Info"), max_length=200, blank=True, null=True)

    def __unicode__(self):
        return u'%s:%s' % (self.username, self.subject)

    class Meta:
        verbose_name = _('UserOrder')
        verbose_name_plural = _('UserOrders')
        ordering = ('-update_date',)
        #for crm
        managed = False
        app_label = 'order'


class Order(models.Model):
    "deprecated"
    """
    source = models.CharField(_("Source"), max_length=32)
    code = models.CharField(_("Code"), max_length=64, unique=True)
    trade_no = models.CharField(_("Trade No"), max_length=32)

    body = models.CharField(_("Body"), max_length=128)
    attach = models.CharField(_("Attach"), max_length=128, null=True,
                              blank=True)
    total_fee = models.IntegerField(_("Total fee"))
    spbill_create_ip = models.CharField(_("Spbill create ip"), max_length=32)
    input_charset = models.CharField(_("Input Charset"), max_length=8)

    attrs = models.CharField(_("Attributes"), max_length=4096, null=True,
                             blank=True)

    status = models.IntegerField(_("Status"), choices=TRANSACTION_CHOICES,
                                 default=TRANSACTION_READY)

    expiry_date = models.DateTimeField(_("Expired at"))
    sn = models.CharField(_("SN"), max_length=128, null=True, blank=True)
    purchase_date = models.DateTimeField(_("Purchased at"), null=True,
                                         blank=True)
    create_date = models.DateTimeField(_("Created at"), auto_now_add=True)
    update_date = models.DateTimeField(_("Updated at"), auto_now=True)

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')
        ordering = ('-update_date', )

    def __unicode__(self):
        return self.code
    """








