#coding:utf8
from django.contrib import admin
from django.conf import settings

from models import *
# Register your models here.

class PostAdmin(admin.ModelAdmin):
    list_per_page = settings.ADMIN_LIST_PER_PAGE
    list_max_show_all = settings.ADMIN_LIST_MAX_SHOW_ALL

    actions_on_top = True
    actions_on_bottom = True
    actions_selection_counter = True

    list_display = ['title', 'content']
    def query_username_by_sn(self, request, queryset):
        rows_updated = queryset.update(status='Published')
        self.message_user(request, "成功发布 %d 条数据." % rows_updated)
        print '======', rows_updated
    query_username_by_sn.short_description = u"查询sn号11"

    actions = ['query_username_by_sn', ]


admin.site.register(Post, PostAdmin)
