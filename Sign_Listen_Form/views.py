import json

from django.http import JsonResponse
from rest_framework.views import APIView
from AutoRobot import settings
from ApiApplication import ApiApplication
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from .anyc_task import task


# 自动签收----监听表单
class FormDataView(APIView):
    @csrf_exempt
    def post(self,request):
        # 认证
        app_id = settings.APPID
        app_secret = settings.APPSECRET
        id = settings.ID
        header = ApiApplication.ApiApplication(app_id, app_secret, id)
        print(header)
        # 自动签收
        # 拿到监听到的记录数据
        data = request.body
        data = json.loads(data)
        if data['action'] == 'created':
            # 从缓存中获取 response_id
            response_id = cache.get('response_id')
            if response_id == data['response']['id']:
                print('缓存中有id')
                cache.clear()
                return JsonResponse({'code': 200, 'response_id': data['response']['id']})
            else:
                print('缓存中没有id')
                cache.set('response_id', data['response']['id'])
                task.delay(header, data)
                return JsonResponse({'code': 200, 'response_id': data['response']['id']})
        return JsonResponse({'code': 200, 'msg':"表单状态不是created，拒绝接收"})