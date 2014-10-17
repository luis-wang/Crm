#coding:utf8
from django.db import models

# Create your models here.

class Post(models.Model):
    title = models.CharField(max_length=100, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)