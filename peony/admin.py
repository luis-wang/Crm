#coding:utf8
from django.contrib import admin
from models import UserOrder
from django.conf import settings
# Register your models here.


class UserOrderAdmin(admin.ModelAdmin):
    list_per_page = settings.ADMIN_LIST_PER_PAGE
    list_max_show_all = settings.ADMIN_LIST_MAX_SHOW_ALL

    actions_on_top = True
    actions_on_bottom = True
    actions_selection_counter = True

    list_display = ['trade_no', 'user_id', 'username']
    search_fields = ['trade_no', 'username']
    list_filter = ['state', 'valid', 'source']

    def query_username_by_sn(self, request, queryset):
        pass
    query_username_by_sn.short_description = u"UserOrderAdmin_action"

    actions = ['query_username_by_sn', ]






admin.site.register(UserOrder, UserOrderAdmin)