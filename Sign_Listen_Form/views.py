import json
import logging
import re
from django.http import JsonResponse
from .task import ccc
from rest_framework.views import APIView
from AutoRobot import settings
from ApiApplication import ApiApplication
from apis import apis
from .models import FormInfo
from django.views.decorators.csrf import csrf_exempt


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
        record_id = data['response']['id']   # 表单记录id
        if data['response']['mapped_values']['order_status']['value'][0] == '待派单':
            # 存入数据库
            obj = FormInfo(form_id=settings.form_id, data=data)
            obj.save()
            # 一、修改字段，需要4步，调用获取表单结构信息接口，获取表单数据，调用机器人接口，调用修改表单记录接口
            # 1、获取表单结构信息中的field_id
            forminfo_url = f"%s/api/v4/forms/%d" % (settings.FORM_URL, settings.form_id)
            (status_field_id,   # 状态field_id
             response_field_id,    # 返回信息field_id
             flow_recod_field_id,   # 流程记录field_id
             date_field_id,         # 派单日期field_id
             depart_field_id,       # 派单管家建议派单部门field_id
             request_field_id,       # 请求信息field_id
             order_status_field_id
             ) = apis.forminfo(forminfo_url, header)

            order_id = data['response']['mapped_values']['workFormNo']['value'][0]  # 监听到的表单的工单号

            # 监听表单记录的数据，拿调用机器人接口需要用的
            form_data1 = {
                "order_id": order_id,
                "creat_time": data['response']['mapped_values']['iptTime']['value'][0],
                "status": "receipt",
                "appeal_type": data['response']['mapped_values']['event_source']['value'][0]['value'],
            }

            # 3、调用机器人接口
            robot_url = settings.ROBOT_URL
            method = settings.method
            content_type = settings.Content_Type
            robot_header = {
                'Content-Type': content_type
            }
            field_ids = [order_status_field_id, flow_recod_field_id, date_field_id, depart_field_id, status_field_id]
            logging.info("field_ids:: %s" % field_ids)
            forms_url = f"%s/api/v4/forms/%d/responses" % (settings.FORM_URL, settings.form_id)
            forms_info = apis.formdata('GET', forms_url, header)  # 表单数据（记录）
            target_entry_id1 = []
            for item in forms_info:
                # 找到id的值为record_id的字典
                if item["id"] == record_id:
                    # 遍历这个字典中的entries下的元素（字典）
                    for entry in item["entries"]:
                        # 如果entry中的field_id在field_ids中
                        if entry["field_id"] in field_ids:
                            # 将entry的id值加入到ids列表中
                            target_entry_id1.append(entry["id"])
            logging.info("target_entry_id1:: %s" % target_entry_id1)
            request_info = apis.robot(method, robot_url, robot_header, form_data1)   # 测试过，返回的是一个字典
            logging.info("request_info:: %s" % request_info)
            if request_info:
                # 4、调用修改表单记录接口
                params = {
                    "response": {
                        "entries_attributes": [
                            {
                                "field_id": status_field_id,
                                "value": "未回调",
                            },
                            {
                                "field_id": request_field_id,
                                "value": str(request_info)
                            }
                        ]
                    },
                    "user_id": settings.form_user_id
                }
                modify_form_url = f"%s/api/v4/forms/%d/responses/%d" % (settings.FORM_URL, settings.form_id, record_id)
                modify_first = apis.modifify_form(modify_form_url, header, params)
                logging.info("record_id:: %s" % record_id)

                # 二、发起skylark流程，需要3步，查询单条数据，获取流程结构信息，发起流程
                # 1、数据
                content_category1 = data['response']['mapped_values']['content_category1']['value'][0]
                content_category2 = data['response']['mapped_values']['content_category2']['value'][0]
                fmContent = data['response']['mapped_values']['fmContent']['value'][0]
                wsTopic = str(data['response']['mapped_values']['wsTopic']['value'][0])

                # 判断字符串中是否包含 "[" 符号
                if "[" in wsTopic:
                    # 如果包含 "[" 符号，则去掉该符号前面的内容，并去掉所有字母和数字
                    # result = re.sub(r'.*\[|[\w\d]', '', wsTopic)
                    result = wsTopic[wsTopic.index("["):]
                else:
                    # 如果不包含 "[" 符号，则判断是否包含字母和数字，如果有则去掉，如果没有则使用原值
                    if re.search(r'[a-zA-Z0-9]', wsTopic):
                        result = re.sub(r'[a-zA-Z0-9]', '', wsTopic)
                    else:
                        result = wsTopic
                # 将所有变量用逗号连接起来，这是智能派单接口需要的参数
                text = f"{content_category1},{content_category2},{result},{fmContent}"
                max_score_label = apis.auto_dispatch(text)   # 调用派单管家接口

                # 2、获取流程结构信息
                url = '%s/api/v4/yaw/flows/%d' % (settings.SKY_URL, settings.flow_id)
                struc_info = apis.struc_info(url, header)
                # 构建数据（用于发起流程）
                infodata = []
                mapped_values = data['response']['mapped_values']
                for field in struc_info['fields']:
                    if field['identity_key'] == 'handle_unit':
                        infodata.append({
                            "field_id": field['id'],
                            "value": max_score_label,
                            "option_id": 2415
                        })
                    if field['identity_key'] in mapped_values:
                        value = mapped_values[field['identity_key']]['value'][0]['value'][0] if 'value' in mapped_values[
                            field['identity_key']]['value'][0] else mapped_values[field['identity_key']]['value'][0]
                        infodata.append({
                            "field_id": field['id'],
                            "value": value
                        })
                # infodata就是最终构建出来的数据
                logging.info("infodata:: %s" % infodata)
                ccc.delay(header,infodata,order_status_field_id,flow_recod_field_id,date_field_id,depart_field_id,target_entry_id1,
                    max_score_label,status_field_id,form_data1,record_id,response_field_id,order_id)
                return JsonResponse({'code': 200, 'msg': '成功'})

        else:
            return JsonResponse({'code': 200, 'msg': '表单状态不是待派单'})