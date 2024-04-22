import json
import logging
from datetime import datetime
from django.http import JsonResponse
from AutoRobot import settings
from apis import apis
from AutoRobot.celery import app


@app.task
def ccc(header, infodata, order_status_field_id, flow_recod_field_id,
        date_field_id, depart_field_id, field_target_id, max_score_label,
        status_field_id, form_data1, record_id, response_field_id, order_id):
    logging.info("异步任务接收到的target_entry_id1：%s" % field_target_id)
    # order_status_target_id = None
    # status_target_id = None
    # # 遍历 field_target_id 列表
    # for item in field_target_id:
    #     # 检查当前字典的 field_id 是否等于给定的 field_id
    #     if item['field_id'] == order_status_field_id:
    #         # 如果匹配，取出对应的 target_entry_id 的值
    #         order_status_target_id = item['target_entry_id']
    #         # 找到了对应的值，可以退出循环
    #     elif item['field_id'] == status_field_id:
    #         status_target_id = item['target_entry_id']
    #     else:
    #         pass
    # logging.info("order_status_target_id：%s" % order_status_target_id)
    # logging.info("status_target_id：%s" % status_target_id)
    # # 如果流程发起成功，则修改表单记录字段
    # # 第一次调用 route
    # result = apis.new_flows_journeys_route(header, settings.flow_id, settings.user_id,
    #                                        entries_attributes=infodata)
    # data = json.loads(result)
    # next_vertices = data.get("next_vertices", [])
    # first_vertex_id = next_vertices[0].get("id") if next_vertices else None
    # print(first_vertex_id)
    # logging.info("第一次发起流程返回的first_vertex_id：%s" %first_vertex_id)
    # # 第二次调用 propose
    # result2 = apis.new_flows_journeys_propose(header, settings.flow_id, settings.user_id,
    #                                           next_vertex_id=first_vertex_id)
    # data = json.loads(result2)
    #
    # if data:   # 发起流程成功
    #     logging.info("发起流程成功")
    #     # 修改表单记录需要的参数
    #     journey = data.get("journey", [])
    #     journey_id = journey['id'] if journey else None
    #     created_at = data.get('created_at', [])
    #     # 将字符串解析为datetime对象
    #     date_time_obj = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S.%f%z")
    #     # 去掉时区信息，并转换为字符串
    #     new_datetime_str = date_time_obj.replace(tzinfo=None).strftime("%Y-%m-%d %H:%M")
    #     logging.info("发起流程的时间：%s" % new_datetime_str)
    #     params = {
    #         "response": {
    #             "entries_attributes": [
    #                 {
    #                     "field_id": order_status_field_id,
    #                     "value": "待回复",
    #                     "id": order_status_target_id
    #                 },
    #                 {
    #                     "field_id": flow_recod_field_id,
    #                     "value": journey_id,
    #                 },
    #                 {
    #                     "field_id": date_field_id,
    #                     "value": new_datetime_str,
    #                 },
    #                 {
    #                     "field_id": depart_field_id,
    #                     "value": max_score_label,
    #                 }
    #             ]
    #         },
    #         "user_id": settings.form_user_id
    #     }
    #     modify_form_url = f"%s/api/v4/forms/%d/responses/%d" % (settings.FORM_URL, settings.form_id, record_id)
    #     modify_second = apis.modifify_form(modify_form_url, header, params)
    #
    #     # 表单记录执行调用机器人接口进行签收
    #     # 筛选表单字段“状态（12345系统）”（robot_status）为“未回调”记录
    #     # 先拿到表单信息中的“状态（12345系统）”的field_id
    #     # 然后拿着field_id去表单数据中筛选出记录（拿到筛选条件的记录的记录id），然后再获取单条记录数据
    #     # field_id = status_field_id
    #     # result_ids = []
    #     # forms_url = f"%s/api/v4/forms/%d/responses" % (settings.FORM_URL, settings.form_id)
    #     # forms_info = apis.formdata('GET', forms_url, header)  # 表单数据（记录）
    #     # # 记录id
    #     # for item in forms_info:
    #     #     for entry in item["entries"]:
    #     #         if entry["field_id"] == field_id and entry["value"] == '未回调':
    #     #             result_ids.append(item["id"])
    #     # logging.info("状态为未回调的记录的id们：%s" % result_ids)
    #     # for id in result_ids:
    #     #     # 查询单条数据
    #     #     single_url = f"%s/api/v4/responses/%d" % (settings.FORM_URL, id)
    #     #     single_data = apis.single_record(single_url, header)
    #     #     mapped_values = single_data['mapped_values']
    #     #     workFormNo = mapped_values['workFormNo']['value'][0]  # 工单号
    #     #     dispatch_date = mapped_values['dispatch_date']['value'][0]  # 派单日期
    #     #     dispatch_date = datetime.strptime(dispatch_date, "%Y-%m-%d %H:%M")
    #     #     # 记录调用接口的时间
    #     #     start_time = datetime.now()
    #     #     # 格式化日期时间字符串，只包含年、月、日、时和分
    #     #     formatted_time = start_time.strftime("%Y-%m-%d %H:%M")
    #     #     formatted_time = datetime.strptime(formatted_time, "%Y-%m-%d %H:%M")
    #     #     # 计算时间差
    #     #     logging.info("调用接口的时间：%s" % formatted_time)
    #     #     logging.info("派单日期：%s" % dispatch_date)
    #     #     time_diff = formatted_time - dispatch_date
    #     #     # 将时间差转换为分钟数
    #     #     minutes_difference = time_diff.total_seconds() / 60
    #     #     workFormNo_list = []
    #     #     # 检查时间差是否大于等于5分钟
    #     #     if minutes_difference >= 5:
    #     #         # 飞书提醒到运维报警群话题里
    #     #         workFormNo_list.append(workFormNo)
    #     #         feishu_url = settings.feishu + settings.secret
    #     #         feishu = apis.feishu_robot(feishu_url, work_list=workFormNo_list)  # 飞书提醒
    #     #     else:
    #     #         logging.info("时间差小于5分钟，不提醒")
    #     #
    #     #     # max_retries = 3  # 最大重试次数 (为什么不需要，因为飞书提醒后，产品会手动去干预)
    #     #     # retry_count = 0
    #     #     response_info = None
    #     #     while not response_info:
    #     #         # 调用机器人接口
    #     #         robot_url = settings.ROBOT_URL
    #     #         method = settings.method
    #     #         content_type = settings.Content_Type
    #     #         robot_header = {
    #     #             'Content-Type': content_type
    #     #         }
    #     #         response_info = apis.robot(method, robot_url, robot_header, form_data1,
    #     #                                    callback=True)  # 调用机器人接口返回的信息
    #     #         logging.info("调用机器人接口返回的信息：%s" % response_info)
    #     #         # response_info = json.loads(response_info)
    #     #         status_value = response_info["result"]["status"]
    #     #         field_ids = [order_status_field_id, flow_recod_field_id, date_field_id, depart_field_id,
    #     #                      status_field_id]
    #     #         logging.info("异步任务接收到的field_ids：%s" % field_ids)
    #     #         forms_url = f"%s/api/v4/forms/%d/responses" % (settings.FORM_URL, settings.form_id)
    #     #         forms_info = apis.formdata('GET', forms_url, header)  # 表单数据（记录）
    #     #         # target_entry_id = []
    #     #         # for item in forms_info:
    #     #         #     # 找到id的值为record_id的字典
    #     #         #     if item["id"] == record_id:
    #     #         #         # 遍历这个字典中的entries下的元素（字典）
    #     #         #         for entry in item["entries"]:
    #     #         #             # 如果entry中的field_id在field_ids中
    #     #         #             if entry["field_id"] in field_ids:
    #     #         #                 # 将entry的id值加入到ids列表中
    #     #         #                 target_entry_id.append(entry["id"])
    #     #         # print(target_entry_id)
    #     #         if status_value == 0:
    #     #             params = {
    #     #                 "response": {
    #     #                     "entries_attributes": [
    #     #                         {
    #     #                             "field_id": status_field_id,
    #     #                             "value": "回调成功",
    #     #                             "id": status_target_id
    #     #                         },
    #     #                         {
    #     #                             "field_id": response_field_id,
    #     #                             "value": str(response_info)
    #     #                         }
    #     #                     ]
    #     #                 },
    #     #                 "user_id": settings.form_user_id,
    #     #             }
    #     #             logging.info("params:%s" % params)
    #     #             modify_form_url = f"%s/api/v4/forms/%d/responses/%d" % (
    #     #                 settings.FORM_URL, settings.form_id, id)
    #     #             # 修改状态为”回调成功“
    #     #             modify_fourth = apis.modifify_form(modify_form_url, header, params)
    #     #         else:
    #     #             params = {
    #     #                 "response": {
    #     #                     "entries_attributes": [
    #     #                         {
    #     #                             "field_id": response_field_id,
    #     #                             "value": str(response_info)
    #     #                         }
    #     #                     ]
    #     #                 },
    #     #                 "user_id": settings.form_user_id
    #     #             }
    #     #             modify_form_url = f"%s/api/v4/forms/%d/responses/%d" % (
    #     #                 settings.FORM_URL, settings.form_id, id)
    #     #             modify_fifth = apis.modifify_form(modify_form_url, header, params)
    #
    # else:
    #     # 如果流程发起失败（异常），则修改表单记录字段并飞书提醒到运维报警群话题里
    #     logging.info("发起流程失败")
    #     params = {
    #         "response": {
    #             "entries_attributes": [
    #                 {
    #                     "field_id": status_field_id,
    #                     "value": "流程异常",
    #                     "id": status_target_id
    #                 }
    #             ]
    #         },
    #         "user_id": settings.form_user_id
    #     }
    #     modify_form_url = f"%s/api/v4/forms/%d/responses/%d" % (settings.FORM_URL, settings.form_id, record_id)
    #     modify_third = apis.modifify_form(modify_form_url, header, params)  # 修改表单记录
    #     feishu_url = settings.feishu + settings.secret
    #     feishu = apis.feishu_robot(feishu_url, order_id=order_id)  # 飞书提醒
    #     return JsonResponse({'code': 200, 'msg': '发起流程失败，已修改表单和报警'})

