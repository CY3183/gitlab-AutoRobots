import logging

from AutoRobot import settings
from apis import apis

from AutoRobot.celery import app
@app.task
def ccc(desired_id,header,result_value,request_field_id,status_field_id,response_field_id,target_entry_id):
    logging.info("异步任务收到的target_entry_id：%s" % target_entry_id)
    single_url = f"%s/api/v4/responses/%f" % (settings.FORM_URL, desired_id)
    single_data = apis.single_record(single_url, header)
    mapped_values = single_data['mapped_values']
    workFormNo = mapped_values['workFormNo']['value'][0]  # 工单号（机器人参数）
    created_time = mapped_values['iptTime']['value'][0]  # 创建时间（机器人参数）
    event_source = mapped_values['event_source']['value'][0]['value']  # 诉求来源（机器人参数）

    # 监听表单记录的数据，拿调用机器人接口需要用的
    form_data1 = {
        "order_id": workFormNo,
        "creat_time": created_time,
        "status": "reply",
        "reply": result_value,  # 流程回传字段
        "appeal_type": event_source
    }
    # 调用机器人接口
    robot_url = settings.ROBOT_URL
    method = settings.method
    content_type = settings.Content_Type
    robot_header = {
        'Content-Type': content_type
    }
    request_info = apis.robot(method, robot_url, robot_header, form_data1)  # 请求机器人接口构成的对象信息
    # 修改表单记录
    params = {
        "response": {
            "entries_attributes": [
                {
                    "field_id": request_field_id,
                    "value": str(request_info),
                    "id": target_entry_id[3]
                },
                {
                    "field_id": status_field_id,
                    "value": '未回调',
                    "id": target_entry_id[4]
                },
                {
                    "field_id": response_field_id,
                    "value": ' ',  # 这里需求就是填空值
                    "id": target_entry_id[1]
                }
            ]
        },
        "user_id": settings.form_user_id
    }
    modify_form_url = f"%s/api/v4/forms/%d/responses/%d" % (settings.FORM_URL, settings.form_id, desired_id)
    modify_seventh = apis.modifify_form(modify_form_url, header, params)
