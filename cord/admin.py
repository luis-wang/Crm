#coding:utf8
from django.http import HttpResponse
from django.core import serializers
from django.contrib import admin
from django.conf import settings
from django.contrib.admin import helpers
from django.template.response import TemplateResponse
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.contrib import messages


from auth_models import User
from trust_models import *
from accounts_models import *
from peony.order_models import UserOrder


class DeviceAdmin(admin.ModelAdmin):
    list_per_page = settings.ADMIN_LIST_PER_PAGE
    list_max_show_all = settings.ADMIN_LIST_MAX_SHOW_ALL

    actions_on_top = True
    actions_on_bottom = True
    actions_selection_counter = True

    list_display = ('id', 'sn', 'manufacture', 'kind', 'ip', 'version', 'update_date')
    search_fields = ('sn', 'ip')
    #过滤器，显示出这样的分类
    list_filter = ('kind',)
    actions = ['query_user', 'query_sn_payhistory']

    def query_user(self, request, queryset):
        '查询登录过的用户'
        try:
            query_device = queryset[0]
            loginHistorys = LoginHistory.objects.filter(device_id=query_device.pk)
            logined_users = [i.user for i in loginHistorys]

            c = RequestContext(request, {'query_device': query_device,
                                         'logined_users': logined_users})
            self.message_user(request, u"查询成功", messages.SUCCESS)
        except Exception, e:
            self.message_user(request, 'Error: %s' % str(e), messages.ERROR)
            return
        t = loader.get_template('admin/show_logined_users.html')
        return HttpResponse(t.render(c),)
    query_user.short_description = u'查询登录过的用户'

    def query_sn_payhistory(self, request, queryset):
        "由设备SN查询付费信息"
        try:
            query_device = queryset[0]
            '''
            loginHistorys = LoginHistory.objects.filter(device_id=query_device.pk)
            #找到在这台机器上登录过的所有用户
            logined_users = [i.user for i in loginHistorys]
            #这些用户的所有订单中，过虑出sn为此设备sn的
            for u in logined_users:
                orders = Order.objects.filter(user=u)
                pass
            '''

            #单片
            userorders = UserOrder.objects.filter(device_id=query_device.pk)

            c = RequestContext(request, {'query_device': query_device,
                                         'userorders': userorders})
            self.message_user(request, u"查询付费信息成功", messages.SUCCESS)
        except Exception, e:
            self.message_user(request, 'Error: %s' % str(e), messages.ERROR)
            return
        t = loader.get_template('admin/show_device_sn_orders.html')
        return HttpResponse(t.render(c),)

    query_sn_payhistory.short_description = u"由设备SN查询付费信息"



class CordUserAdmin(admin.ModelAdmin):
    list_per_page = settings.ADMIN_LIST_PER_PAGE
    list_max_show_all = settings.ADMIN_LIST_MAX_SHOW_ALL

    actions_on_top = True
    actions_on_bottom = True
    actions_selection_counter = True

    list_display = ('id', 'username', 'email', 'last_login', 'date_joined')
    search_fields = ('username', )

    actions = ['query_sn', 'query_user_payhistory']

    def query_sn(self, request, queryset):
        try:
            query_user = queryset[0]
            loginHistorys = LoginHistory.objects.filter(user=query_user)
            sn_list = []
            for i in loginHistorys:
                device = Device.objects.filter(pk=i.device_id)
                if device:
                    sn_list.append(device[0].sn)
            c = RequestContext(request, {'sn_list': sn_list, 'query_user': query_user})
            self.message_user(request, u"查询成功", messages.SUCCESS)
        except Exception,e:
            self.message_user(request, 'Error: %s' % str(e), messages.ERROR)
            return
        t = loader.get_template('admin/show_user_sn.html')
        return HttpResponse(t.render(c),)

    query_sn.short_description = u"查询登录过的电视SN号"

    def admin_action(self, request, queryset):
        if request.POST.get('post'):
            # process the queryset here
            pass
        else:
            context = {
                'title': _("Are you sure?"),
                'queryset': queryset,
                'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
            }
            return TemplateResponse(request, 'path/to/template.html',
                context, current_app=self.admin_site.name)
    admin_action.short_description = u"admin_action1"

    def query_user_payhistory(self, request, queryset):
        try:
            query_user = queryset[0]
            #account balance
            user_account = Account.objects.filter(user=query_user)
            if user_account:
                user_account = user_account[0]
            else:
                user_account = None

            #pay history
            orders = Order.objects.filter(user=query_user)
            c = RequestContext(request, {'orders':      orders,
                                         'query_user':  query_user,
                                         'user_account':user_account})

            self.message_user(request, u"查询成功", messages.SUCCESS)
        except Exception, e:
            self.message_user(request, 'Error: %s' % str(e), messages.ERROR)
            return
        t = loader.get_template('admin/show_user_orders.html')
        return HttpResponse(t.render(c),)

    query_user_payhistory.short_description = u"查询用户的付费信息"


class LoginHistoryAdmin(admin.ModelAdmin):
    list_per_page = settings.ADMIN_LIST_PER_PAGE
    list_max_show_all = settings.ADMIN_LIST_MAX_SHOW_ALL

    actions_on_top = True
    actions_on_bottom = True
    actions_selection_counter = True

    list_display = ['user', 'device_id', 'ip', 'login_date']
    search_fields = ['device_id', 'user']


class OrderAdmin(admin.ModelAdmin):
    list_per_page = settings.ADMIN_LIST_PER_PAGE
    list_max_show_all = settings.ADMIN_LIST_MAX_SHOW_ALL

    actions_on_top = True
    actions_on_bottom = True
    actions_selection_counter = True

    list_display = ['id', 'sn', 'username', 'valid', 'state', 'price','duration','source','create_date','update_date']
    search_fields = ['sn', 'username']



admin.site.unregister(User)
admin.site.register(User, CordUserAdmin)
admin.site.register(Device, DeviceAdmin)

admin.site.register(LoginHistory, LoginHistoryAdmin)
admin.site.register(Order, OrderAdmin)

admin.site.disable_action('delete_selected')




