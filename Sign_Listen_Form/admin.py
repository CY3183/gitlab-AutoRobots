from django.contrib import admin
from .models import FormInfo


@admin.register(FormInfo)    ## 监听表单
class EventsRawModeAdmin(admin.ModelAdmin):
    list_display = ('form_id', "data", 'created_at', 'updated_at')
    search_fields = ('form_id', 'data')
    list_filter = ('form_id', 'created_at')