from django.forms import Textarea
from .models import FlowInfo
from django.contrib import admin
from django.db import models


@admin.register(FlowInfo)    ## 监听流程
class EventsRawModeAdmin(admin.ModelAdmin):
    list_display = ('flow_id', 'data', 'created_at', 'updated_at')
    search_fields = ('flow_id','data')
    list_filter = ('flow_id', 'created_at')
