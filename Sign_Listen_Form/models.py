from django.db import models


class FormInfo(models.Model):
    '''监听表单记录工单状态（order_status）为“待派单”的数据'''
    form_id = models.CharField(max_length=64, null=True,blank=True, verbose_name="表单id")
    data = models.JSONField(null=True, blank=True, verbose_name="data")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')