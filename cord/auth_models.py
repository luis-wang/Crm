# coding:utf8
#coding:utf8
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User as authuser
from django.utils.translation import ugettext_lazy as _


class User(authuser):
    """
    cord user model
    """
    username = models.CharField(_('username'), max_length=30, unique=True)
    email = models.EmailField(_('email address'), blank=True)
    last_login = models.DateTimeField(_('last login'), default=timezone.now)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    class Meta:
        managed = False
        app_label = 'auth'