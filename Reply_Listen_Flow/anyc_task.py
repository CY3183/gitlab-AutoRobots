from datetime import datetime
from django.http import JsonResponse
from apis import apis
from .models import FlowInfo
from .task import ccc
from AutoRobot import settings
import logging
from AutoRobot.celery import app


@app.task
def task(header, data):
    logging.info("现在开始执行任务")
    # 1、获取表单结构信息中的field_id ，修改表单记录的时候要用
    forminfo_url = f"%s/api/v4/forms/%d" % (settings.FORM_URL, settings.form_id)
    (status_field_id,
     response_field_id,
     flow_recod_field_id,
     date_field_id,
     depart_field_id,
     request_field_id,
     order_status_field_id
     ) = apis.forminfo(forminfo_url, header)
    if data['assignment']['journey']['status'] == 'finished':
        # 存入数据库
        event = FlowInfo()
        event.flow_id = settings.flow_id
        event.data = data
        event.save()
        # 查询表单记录并修改表单记录
        journey_id = data['assignment']['journey_id']  # 流程记录“journey_id”，也就是流程记录的id
        logging.info("流程记录的journey_id:%s" % journey_id)
        form_url = f"%s/api/v4/forms/%d/responses" % (settings.FORM_URL, settings.form_id)
        form_info = apis.formdata('GET', form_url, header)  # 获取表单数据
        desired_id = None
        for item in form_info:
            mapped_values = item.get('mapped_values', {})
            journey_ids_value = mapped_values.get('journey_ids', {'value': [None]})['value'][0]
            if journey_ids_value is not None and int(journey_ids_value) == int(journey_id):
                desired_id = item.get('id')  # 对应表单的记录id
                break
        logging.info("对应表单记录的id:%s" % desired_id)
        field_ids = [order_status_field_id, response_field_id, depart_field_id, request_field_id, status_field_id]
        logging.info("field_ids:%s" % field_ids)
        forms_url = f"%s/api/v4/forms/%d/responses" % (settings.FORM_URL, settings.form_id)
        forms_info = apis.formdata('GET', forms_url, header)  # 表单数据（记录）
        field_target_id = []
        for item in forms_info:
            # 找到id的值为record_id的字典
            if item["id"] == desired_id:
                # 遍历这个字典中的entries下的元素（字典）
                for entry in item["entries"]:
                    # 如果entry中的field_id在field_ids中
                    if entry["field_id"] in field_ids:
                        # 将entry的field_id和id值加入到列表中
                        field_target_id.append({'field_id': entry["field_id"], 'target_entry_id': entry["id"]})
        logging.info("target_entry_id:%s" % field_target_id)
        # 获取流程记录id，拿着流程记录id去调用接口：获取某条流程任务的所有 Moment(处理情况)，才能拿到流程回传字段
        flow_recod_id = data['assignment']['journey']['id']
        print("流程记录id：%s" % flow_recod_id)
        logging.info("流程记录id：%s" % flow_recod_id)
        # 调用接口：获取某条流程任务的所有 Moment(处理情况)
        url = f"%s/api/v4/yaw/journeys/%d/moments" % (settings.FORM_URL, flow_recod_id)
        result_value = apis.flow_recod_moment(url, header)
        logging.info("流程回复内容:%s" % result_value)
        # 获取表单记录id为desired_id的记录，也就是查询单条数据
        # 查询单条数据
        if desired_id:
            ccc.delay(desired_id, header, result_value, request_field_id, status_field_id, response_field_id,
                      field_target_id)
        else:
            logging.info("没有找到对应的表单记录")

        # # 调用机器人接口进行回复
        # # 筛选表单字段“状态（12345系统）”（robot_status）为“未回调”记录进行调用机器人接口
        # field_id = status_field_id
        # result_ids = []
        # forms_url = f"%s/api/v4/forms/%d/responses" % (settings.FORM_URL, settings.form_id)
        # forms_info = apis.formdata('GET', forms_url, header)  # 表单数据（记录）
        # # 记录id
        # for item in forms_info:
        #     for entry in item["entries"]:
        #         if entry["field_id"] == field_id and entry["value"] == '未回调':
        #             result_ids.append(item["id"])
        # logging.info(" 状态（12345系统）为“未回调”的记录的记录id们:%s" % result_ids)
        # # 调用接口：获取某条流程任务的流程已完成时间
        # url = f"%s/api/v4/yaw/journeys/%d/moments" % (settings.FORM_URL, flow_recod_id)
        # updated_at = apis.flow_recod_moment(url, header, datatime=True)
        # # 将时间戳转换为 datetime 对象
        # updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
        # updated_at = updated_at.strftime("%Y-%m-%d %H:%M")
        # updated_at = datetime.strptime(updated_at, "%Y-%m-%d %H:%M")
        # for id in result_ids:
        #     # 查询单条数据
        #     single_url = f"%s/api/v4/responses/%d" % (settings.FORM_URL, id)
        #     single_data = apis.single_record(single_url, header)
        #     mapped_values = single_data['mapped_values']
        #     order_id = mapped_values['workFormNo']['value'][0]  # 工单号
        #     creat_time = mapped_values['iptTime']['value'][0]  # 创建时间
        #     appeal_type = mapped_values['event_source']['value'][0]  # 诉求来源
        #
        #     form_data = {
        #         "order_id": order_id,
        #         "creat_time": creat_time,
        #         "status": 'reply',
        #         "reply": result_value,
        #         "appeal_type": appeal_type
        #     }
        #     workFormNo_list = []  # 工单号列表
        #     # 记录调用接口的时间
        #     start_time = datetime.now()
        #     formatted_time = start_time.strftime("%Y-%m-%d %H:%M")
        #     formatted_time = datetime.strptime(formatted_time, "%Y-%m-%d %H:%M")
        #     # 计算时间差
        #     time_diff = formatted_time - updated_at
        #     # 将时间差转换为分钟数
        #     minutes_difference = time_diff.total_seconds() / 60
        #     # 检查时间差是否大于等于5分钟
        #     if minutes_difference >= 5:
        #         logging.info("大于5分钟，飞书提醒！")
        #         # 飞书提醒到运维报警群话题里
        #         workFormNo_list.append(order_id)
        #         logging.info("工单列表")
        #         feishu_url = settings.feishu + settings.secret
        #         feishu = apis.feishu_robot(feishu_url, work_list=workFormNo_list)  # 飞书提醒
        #
        #     response_info = None
        #     while not response_info:
        #         # 调用机器人接口
        #         robot_url = settings.ROBOT_URL
        #         method = settings.method
        #         content_type = settings.Content_Type
        #         robot_header = {
        #             'Content-Type': content_type
        #         }
        #         response_info = apis.robot(method, robot_url, robot_header, form_data,
        #                                    callback=True)  # 请求机器人接口返回的信息
        #         logging.info("机器人接口返回的信息：%s" % response_info)
        #         status_value = response_info["result"]["status"]
        #         logging.info("机器人返回信息中的状态:%s" % status_value)
        #         status_target_id = None
        #         response_target_id = None
        #         order_status_target_id = None
        #         # 遍历 field_target_id 列表
        #         for item in field_target_id:
        #             # 检查当前字典的 field_id 是否等于给定的 field_id
        #             if item['field_id'] == status_field_id:
        #                 # 如果匹配，取出对应的 target_entry_id 的值
        #                 status_target_id = item['target_entry_id']
        #                 # 找到了对应的值，可以退出循环
        #             elif item['field_id'] == response_field_id:
        #                 response_target_id = item['target_entry_id']
        #             elif item['field_id'] == order_status_field_id:
        #                 order_status_target_id = item['target_entry_id']
        #             else:
        #                 pass
        #         if status_value == 0:
        #             params = {
        #                 "response": {
        #                     "entries_attributes": [
        #                         {
        #                             "field_id": status_field_id,
        #                             "value": "回调成功",
        #                             "id": status_target_id
        #                         },
        #                         {
        #                             "field_id": response_field_id,
        #                             "value": str(response_info),
        #                             "id": response_target_id
        #                         },
        #                         {
        #                             "field_id": order_status_field_id,
        #                             "value": '已回复',
        #                             "id": order_status_target_id
        #                         }
        #                     ]
        #                 },
        #                 "user_id": settings.form_user_id,
        #             }
        #             modify_form_url = f"%s/api/v4/forms/%d/responses/%d" % (
        #                 settings.FORM_URL, settings.form_id, desired_id)
        #             # 修改状态为”回调成功“
        #             modify_fourth = apis.modifify_form(modify_form_url, header, params)
        #             logging.info("回调成功，已回复")
        #         else:
        #             params = {
        #                 "response": {
        #                     "entries_attributes": [
        #                         {
        #                             "field_id": response_field_id,
        #                             "value": str(response_info),
        #                             "id": response_target_id
        #                         }
        #                     ]
        #                 },
        #                 "user_id": settings.form_user_id
        #             }
        #             modify_form_url = f"%s/api/v4/forms/%d/responses/%d" % (
        #                 settings.FORM_URL, settings.form_id, desired_id)
        #             modify_fifth = apis.modifify_form(modify_form_url, header, params)
    else:
        logging.info("流程状态不是finished")