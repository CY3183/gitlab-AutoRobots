import logging
from datetime import datetime
from AutoRobot import settings
from apis import apis
from ApiApplication import ApiApplication
from AutoRobot.celery import app


def feishu(workFormNo,dispatch_date1=None,updated_at=None):
    minutes_difference = None
    # 记录调用接口的时间
    start_time = datetime.now()
    # 格式化日期时间字符串，只包含年、月、日、时和分
    start_time = start_time.strftime("%Y-%m-%d %H:%M")
    start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
    logging.info("调用接口的时间：%s" % start_time)
    logging.info("派单日期：%s" % dispatch_date1)
    logging.info("流程已完成时间：%s" % updated_at)
    if dispatch_date1:
        time_diff = start_time - dispatch_date1
        # 将时间差转换为分钟数
        minutes_difference = time_diff.total_seconds() / 60
    elif updated_at:
        time_diff = start_time - updated_at
        # 将时间差转换为分钟数
        minutes_difference = time_diff.total_seconds() / 60
    else:
        pass
    workFormNo_list = []
    # 检查时间差是否大于等于5分钟
    if minutes_difference >= 5:
        # 飞书提醒到运维报警群话题里
        workFormNo_list.append(workFormNo)
        feishu_url = settings.feishu + settings.secret
        feishu = apis.feishu_robot(feishu_url, work_list=workFormNo_list)  # 飞书提醒
    else:
        logging.info("时间差小于5分钟，不提醒")


@app.task
def mytask():
    # 认证
    app_id = settings.APPID
    app_secret = settings.APPSECRET
    id = settings.ID
    header = ApiApplication.ApiApplication(app_id, app_secret, id)
    logging.info('header为：%s' % header)
    # 表单结构信息
    forminfo_url = f"%s/api/v4/forms/%d" % (settings.FORM_URL, settings.form_id)
    (status_field_id,
     response_field_id,
     flow_recod_field_id,
     date_field_id,
     depart_field_id,
     request_field_id,
     order_status_field_id
     ) = apis.forminfo(forminfo_url, header)

    field_ids = [status_field_id,response_field_id,flow_recod_field_id,date_field_id,depart_field_id,request_field_id,order_status_field_id]
    forms_url = f"%s/api/v4/forms/%d/responses" % (settings.FORM_URL, settings.form_id)
    forms_info = apis.formdata('GET', forms_url, header)  # 表单数据（记录）
    result_ids = []
    flow_recod_id = []
    logging.info('开始吧')
    for item in forms_info:
        for entry in item["entries"]:
            if entry["field_id"] == status_field_id and entry["value"] == '未回调':
                for next_entry in item["entries"]:
                    if next_entry["field_id"] == flow_recod_field_id and next_entry["value"]:
                        flow_recod_id.append(int(next_entry["value"]))
                        result_ids.append(item["id"])

    logging.info(" 状态（12345系统）为“未回调”的记录的表单记录id们:%s" % result_ids)
    logging.info(" 状态（12345系统）为“未回调”的记录的记录对应的流程记录id们:%s" % flow_recod_id)

    for form_id, flow_id in zip(result_ids, flow_recod_id):
        logging.info("正在处理表单记录id:%s" % form_id)
        logging.info("正在处理流程记录id:%s" % flow_id)

        # 查询单条数据，拿派单日期
        single_url = f"%s/api/v4/responses/%d" % (settings.FORM_URL, form_id)
        single_data = apis.single_record(single_url, header)
        mapped_values = single_data['mapped_values']
        response_infos = mapped_values['response_info']['value'][0] if 'response_info' in mapped_values else None   # 返回信息，用于是填写还是修改
        workFormNo = mapped_values['workFormNo']['value'][0]  # 工单号（调用机器人）
        iptTime = mapped_values['iptTime']['value'][0]  # 创建时间（调用机器人）
        event_source = mapped_values['event_source']['value'][0]['value']  # 诉求来源（调用机器人）
        dispatch_date = mapped_values['dispatch_date']['value'][0]  # 派单日期
        dispatch_date1 = datetime.strptime(dispatch_date, "%Y-%m-%d %H:%M")  # 派单日期
        logging.info("派单日期:%s" % dispatch_date1)

        # 获取某条流程任务的所有 Moment(处理情况)，拿流程完成时间
        url = f"%s/api/v4/yaw/journeys/%d/moments" % (settings.FORM_URL, flow_id)
        updated_at = apis.flow_recod_moment(url, header, datatime=True)
        # 将时间戳转换为 datetime 对象
        if updated_at:
            updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            updated_at = updated_at.strftime("%Y-%m-%d %H:%M")
            updated_at = datetime.strptime(updated_at, "%Y-%m-%d %H:%M")
            logging.info("流程已完成时间:%s" % updated_at)

        if dispatch_date1 and not updated_at:
            form_data1 = {
                "order_id": workFormNo,
                "creat_time": iptTime,
                "status": "receipt",
                "appeal_type": event_source,
            }

            response_info = None
            while not response_info:
                # 调用机器人接口
                robot_url = settings.ROBOT_URL
                method = settings.method
                content_type = settings.Content_Type
                robot_header = {
                    'Content-Type': content_type
                }
                # 判断当前时间和派单日期是否相差5分钟，如果是，则飞书提醒，如果否，则不提醒
                feishu(workFormNo, dispatch_date1)
                response_info = apis.robot(method, robot_url, robot_header, form_data1,
                                           callback=True)  # 调用机器人接口返回的信息
                logging.info("调用机器人接口返回的信息：%s" % response_info)
                # status_value = response_info["result"]["status"]
                status_value = response_info.get("result", {}).get("status")

                field_target_id = []
                for item in forms_info:
                    # 找到id的值为record_id的字典
                    if item["id"] == form_id:
                        # 遍历这个字典中的entries下的元素（字典）
                        for entry in item["entries"]:
                            # 如果entry中的field_id在field_ids中
                            if entry["field_id"] in field_ids:
                                # 将entry的field_id和id值加入到列表中
                                field_target_id.append({'field_id': entry["field_id"], 'target_entry_id': entry["id"]})
                logging.info("target_entry_id:%s" % field_target_id)

                status_target_id = None
                response_target_id = None
                order_status_target_id = None
                # 遍历 field_target_id 列表
                for item in field_target_id:
                    # 检查当前字典的 field_id 是否等于给定的 field_id
                    if item['field_id'] == status_field_id:
                        # 如果匹配，取出对应的 target_entry_id 的值
                        status_target_id = item['target_entry_id']
                        # 找到了对应的值，可以退出循环
                    elif item['field_id'] == response_field_id:
                        response_target_id = item['target_entry_id']
                    elif item['field_id'] == order_status_field_id:
                        order_status_target_id = item['target_entry_id']
                    else:
                        pass
                logging.info("order_status_target_id：%s" % order_status_target_id)
                logging.info("status_target_id：%s" % status_target_id)
                logging.info('order_status_target_id：%s' % order_status_target_id)
                params = None
                if status_value == 0:
                    if response_infos:
                        params = {
                            "response": {
                                "entries_attributes": [
                                    {
                                        "field_id": status_field_id,
                                        "value": "回调成功",
                                        "id": status_target_id
                                    },
                                    {
                                        "field_id": response_field_id,
                                        "value": str(response_info),
                                        "id": response_target_id
                                    }
                                ]
                            },
                            "user_id": settings.form_user_id,
                        }
                    else:
                        params = {
                            "response": {
                                "entries_attributes": [
                                    {
                                        "field_id": status_field_id,
                                        "value": "回调成功",
                                        "id": status_target_id
                                    },
                                    {
                                        "field_id": response_field_id,
                                        "value": str(response_info),
                                    }
                                ]
                            },
                            "user_id": settings.form_user_id,
                        }
                    logging.info("params:%s" % params)
                    modify_form_url = f"%s/api/v4/forms/%d/responses/%d" % (
                        settings.FORM_URL, settings.form_id, form_id)
                    # 修改状态为”回调成功“
                    modify_fourth = apis.modifify_form(modify_form_url, header, params)
                else:
                    if response_infos:
                        params = {
                            "response": {
                                "entries_attributes": [
                                    {
                                        "field_id": response_field_id,
                                        "value": str(response_info),
                                        "id": response_target_id
                                    }
                                ]
                            },
                            "user_id": settings.form_user_id
                        }
                    else:
                        params = {
                            "response": {
                                "entries_attributes": [
                                    {
                                        "field_id": response_field_id,
                                        "value": str(response_info)
                                    }
                                ]
                            },
                            "user_id": settings.form_user_id
                        }
                    modify_form_url = f"%s/api/v4/forms/%d/responses/%d" % (
                        settings.FORM_URL, settings.form_id, form_id)
                    modify_fifth = apis.modifify_form(modify_form_url, header, params)
            logging.info("已修改表单状态（自动签收）")

        elif updated_at:
            # 调用接口：获取某条流程任务的所有 Moment(处理情况)
            url = f"%s/api/v4/yaw/journeys/%d/moments" % (settings.FORM_URL, flow_id)
            result_value = apis.flow_recod_moment(url, header)
            logging.info("流程回复内容:%s" % result_value)
            form_data2 = {
                "order_id": workFormNo,
                "creat_time": iptTime,
                "status": "reply",
                "reply": result_value,
                "appeal_type": event_source,
            }
            response_info = None
            while not response_info:
                # 调用机器人接口
                robot_url = settings.ROBOT_URL
                method = settings.method
                content_type = settings.Content_Type
                robot_header = {
                    'Content-Type': content_type
                }
                # 判断当前时间和流程完成时间是否相差5分钟，如果是，则飞书提醒，如果否，则不提醒
                feishu(workFormNo, updated_at)
                response_info = apis.robot(method, robot_url, robot_header, form_data2,
                                           callback=True)  # 调用机器人接口返回的信息
                logging.info("调用机器人接口返回的信息：%s" % response_info)
                # status_value = response_info["result"]["status"]
                status_value = response_info.get("result", {}).get("status")

                field_target_id = []
                for item in forms_info:
                    # 找到id的值为record_id的字典
                    if item["id"] == form_id:
                        # 遍历这个字典中的entries下的元素（字典）
                        for entry in item["entries"]:
                            # 如果entry中的field_id在field_ids中
                            if entry["field_id"] in field_ids:
                                # 将entry的field_id和id值加入到列表中
                                field_target_id.append({'field_id': entry["field_id"], 'target_entry_id': entry["id"]})
                logging.info("target_entry_id:%s" % field_target_id)

                status_target_id = None
                response_target_id = None
                order_status_target_id = None
                # 遍历 field_target_id 列表
                for item in field_target_id:
                    # 检查当前字典的 field_id 是否等于给定的 field_id
                    if item['field_id'] == status_field_id:
                        # 如果匹配，取出对应的 target_entry_id 的值
                        status_target_id = item['target_entry_id']
                        # 找到了对应的值，可以退出循环
                    elif item['field_id'] == response_field_id:
                        response_target_id = item['target_entry_id']
                    elif item['field_id'] == order_status_field_id:
                        order_status_target_id = item['target_entry_id']
                    else:
                        pass
                logging.info("order_status_target_id：%s" % order_status_target_id)
                logging.info("status_target_id：%s" % status_target_id)
                logging.info('order_status_target_id：%s' % order_status_target_id)
                params = None
                if status_value == 0:
                    if response_infos:
                        params = {
                            "response": {
                                "entries_attributes": [
                                    {
                                        "field_id": status_field_id,
                                        "value": "回调成功",
                                        "id": status_target_id
                                    },
                                    {
                                        "field_id": response_field_id,
                                        "value": str(response_info),
                                        "id": response_target_id
                                    },
                                    {
                                        "field_id": order_status_field_id,
                                        "value": '已回复',
                                        "id": order_status_target_id
                                    }
                                ]
                            },
                            "user_id": settings.form_user_id,
                        }
                    else:
                        params = {
                            "response": {
                                "entries_attributes": [
                                    {
                                        "field_id": status_field_id,
                                        "value": "回调成功",
                                        "id": status_target_id
                                    },
                                    {
                                        "field_id": response_field_id,
                                        "value": str(response_info)
                                    },
                                    {
                                        "field_id": order_status_field_id,
                                        "value": '已回复',
                                        "id": order_status_target_id
                                    }
                                ]
                            },
                            "user_id": settings.form_user_id,
                        }
                    modify_form_url = f"%s/api/v4/forms/%d/responses/%d" % (
                        settings.FORM_URL, settings.form_id, form_id)
                    # 修改状态为”回调成功“
                    modify_fourth = apis.modifify_form(modify_form_url, header, params)
                    logging.info("回调成功，已回复")
                else:
                    if response_infos:
                        params = {
                            "response": {
                                "entries_attributes": [
                                    {
                                        "field_id": response_field_id,
                                        "value": str(response_info),
                                        "id": response_target_id
                                    }
                                ]
                            },
                            "user_id": settings.form_user_id
                        }
                    else:
                        params = {
                            "response": {
                                "entries_attributes": [
                                    {
                                        "field_id": response_field_id,
                                        "value": str(response_info)
                                    }
                                ]
                            },
                            "user_id": settings.form_user_id
                        }
                    modify_form_url = f"%s/api/v4/forms/%d/responses/%d" % (
                        settings.FORM_URL, settings.form_id, form_id)
                    modify_fifth = apis.modifify_form(modify_form_url, header, params)
            logging.info("已修改表单状态（自动回复）")
        else:
            pass