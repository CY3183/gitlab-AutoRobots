import json
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from AutoRobot import settings
from ApiApplication import ApiApplication
from django.core.cache import cache
from .anyc_task import task

# 自动回复---监听流程


class FlowDataView(APIView):
    @csrf_exempt
    def post(self,request):
        # 认证
        app_id = settings.APPID
        app_secret = settings.APPSECRET
        id = settings.ID
        header = ApiApplication.ApiApplication(app_id, app_secret, id)
        logging.info("header:%s" % header)
        # Webhook监听流程记录状态为已完成
        # 拿到推送过来的数据
        data = request.body
        data = json.loads(data)
        if data:
            # 从缓存中获取 response_id
            response_id = cache.get('response_id')
            if response_id == data['assignment']['response']['id']:
                cache.clear()
                return JsonResponse({'code': 200, 'response_id': data['assignment']['response']['id']})
            else:
                cache.set('response_id', data['assignment']['response']['id'])
                task.delay(header, data)
                return JsonResponse({'code': 200, 'response_id': data['assignment']['response']['id']})


