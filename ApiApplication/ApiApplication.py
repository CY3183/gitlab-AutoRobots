import time
import jwt
from django.http import JsonResponse


def ApiApplication(app_id,app_secret,id):
    assert app_id, 40001
    assert app_secret, 40001
    assert id, 40001
    timestamp = int(time.time())   #当前时间戳
    if app_id and app_secret and id:
        headers = {
          "alg": "HS256",
          "typ": "JWT"
        }
        payload = {
            "namespace_id":id,
            "exp":timestamp+10080   # 过期时间：1周
        }
        print(payload)
        encoded_data = jwt.encode(payload=payload,key=app_secret,headers=headers)
        # authorization = "%s:%s" % (app_id, encoded_data.decode())
        authorization = "%s:%s" % (app_id, encoded_data)
        print(authorization)
        headers = {
            'Authorization':authorization,
            'Content-Type':"application/json"
        }
        print(headers)
        return headers
    else:
        return JsonResponse(40001)