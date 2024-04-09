import datetime
import requests
import json
from django.http import JsonResponse
from AutoRobot import settings
import logging
# 配置日志记录器
# logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('apis')


def forminfo(url,header):
    '''表单结构信息'''
    logger.info("url:%s,header:%s" %(url,header))
    response_info = requests.request('get', url=url, headers=header, verify=False)
    logger.info("response_info:%s" % response_info)
    if response_info.status_code == 200:
        form_info = response_info.text
        form_info = json.loads(form_info)
        status_field_id = None
        response_field_id = None
        flow_recod_field_id = None
        date_field_id = None
        depart_field_id = None
        request_field_id = None
        order_status_field_id = None      # 自动回复会用到
        for field in form_info['fields']:
            if field['title'] == '状态（12345系统）':
                status_field_id = field['id']
            elif field['title'] == '返回信息':
                response_field_id = field['id']
            elif field['title'] == '流程记录':
                flow_recod_field_id = field['id']
            elif field['title'] == '派单日期':
                date_field_id = field['id']
            elif field['title'] == '派单管家建议派单部门':
                depart_field_id = field['id']
            elif field['title'] == '请求信息':
                request_field_id = field['id']
            elif field['title'] == '工单状态':
                order_status_field_id = field['id']
        data = {
            'status_field_id': status_field_id,
            'response_field_id': response_field_id,
            'flow_recod_field_id': flow_recod_field_id,
            'date_field_id': date_field_id,
            'depart_field_id': depart_field_id,
            'request_field_id': request_field_id,
            'order_status_field_id': order_status_field_id
        }
        logger.info("field_id:%s" % data)
        return status_field_id,response_field_id,flow_recod_field_id,date_field_id,depart_field_id,request_field_id,order_status_field_id
    else:
        print('失败了')
        return JsonResponse(status=response_info.status_code, data=response_info.text)


def formdata(method, url, header):
    '''表单数据'''
    response_info = requests.request(method, url=url, headers=header, verify=False)
    if response_info.status_code == 200:
        form_info = response_info.text
        # 将响应数据转换为python对象字典
        form_info = json.loads(form_info)
        return form_info
    else:
        return JsonResponse(status=response_info.status_code, data=response_info.text)

def single_record(url,header):
    '''查询单条数据'''
    response_info = requests.request('get', url=url, headers=header, verify=False)
    if response_info.status_code == 200:
        sinle_info = response_info.text
        # 将响应数据转换为python对象字典
        sinle_data = json.loads(sinle_info)
        return sinle_data
    else:
        return JsonResponse(status=response_info.status_code, data=response_info.text)


def robot(method,url,header,payload,callback=None):
    '''机器人，这里要判断，是返回响应信息还是返回请求信息'''
    response_info = requests.request(method, url=url, headers=header, params=payload, verify=False)
    if response_info.status_code == 200:
        if callback:
            info = response_info.text
            info_dict = json.loads(info)
            return info_dict
        else:
            # 获取请求信息
            request_info = {
                'url': url,
                'method': method,
                'header': header,
                'body': payload
            }
            return request_info  # 请求机器人接口构成的对象信息

    else:
        return False


def modifify_form(url, header, params):
    '''修改表单记录'''
    modify = requests.request('put', url=url, json=params, headers=header, verify=False)


def auto_dispatch(text):
    '''派单管家'''
    url = settings.DISPATCH
    text = {
        "text": text
    }
    responseinfo = requests.request('post', url=url,json=text, verify=False)
    info = responseinfo.text
    info_dict = json.loads(info)
    predictions = info_dict["result"][0]["predictions"]
    max_score_prediction = max(predictions, key=lambda x: x["score"])
    max_score_label = max_score_prediction["label"]
    print(max_score_label)
    return max_score_label


def struc_info(url, header):
    # 调用获取流程结构信息的接口
    return_info = requests.request('get', url=url, headers=header, verify=False)
    info = return_info.text
    # 将响应数据转换为python对象字典
    info = json.loads(info)
    return info


def new_flows_journeys_route(header,flow_id, user_id, payload_url=None, entries_attributes=None):
    '''发起流程---route'''
    params = {
        "assignment": {
            "operation": "route",
            "response_attributes": {
                "entries_attributes": entries_attributes
            }
        },
        "user_id": user_id,
        "webhook": {
            "payload_url": payload_url,
            "subscribed_events": [
                "JourneyStatusEvent"
            ]
        },
    }
    url = settings.SKY_URL
    url = '%s/api/v4/yaw/flows/%d/journeys' % (url, flow_id)
    first = requests.request('POST', url=url, json=params, headers=header, verify=False)
    return first.text


# 发起新流程 步骤2 propose
def new_flows_journeys_propose(header,flow_id, user_id, next_vertex_id, entries_attributes=None,
                               next_reviewer_ids=None, duration_thresholds=None):
    '''发起流程---propose'''
    params = {
        "assignment": {
            "operation": "propose",
            "next_vertex_id": next_vertex_id,
        },
        "user_id": user_id,
    }
    if next_reviewer_ids:
        params['assignment']['next_reviewer_ids'] = next_reviewer_ids

    if duration_thresholds:
        params['assignment']['duration_thresholds'] = duration_thresholds

    if entries_attributes:
        params['assignment']['response_attributes']['entries_attributes'] = entries_attributes
    url = settings.SKY_URL
    url = '%s/api/v4/yaw/flows/%d/journeys' % (url, flow_id)
    second = requests.request('POST', url=url, json=params, headers=header, verify=False)
    return second.text


def feishu_robot(url, order_id=None, work_list=None):
    '''飞机机器人'''
    # 请求头
    header = {
        "Content-Type":"application/json"
    }
    # 请求体
    print(order_id)
    if order_id:
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        text_content = """
        ########################
        ### 所属: 武侯-簇桥街道-网络理政机器人
        ### 业务: 网络理政机器人流程发起失败
        ### 标题: 流程发起异常
        ### 描述: 工单号 {}
        ### 业务负责人: <at user_id="ou_d167780ffc1b48ee25c0f4ec692425c6">苏凯</at>
        ### 开发负责人: 陈银
        ### 时间: {}
        ########################
        """.format(order_id, current_time)
        params = {
            "msg_type": "text",
            "content": {
                "text": text_content
            }
        }
    else:
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        text_content = """
                ########################
                ### 所属: 武侯-簇桥街道-网络理政机器人
                ### 业务: 网络理政机器人回调程序
                ### 标题: 回调失败提醒
                ### 描述: 超过5分钟未回调成功的请求有{}个，工单号列表{}
                ### 业务负责人: <at user_id="ou_d167780ffc1b48ee25c0f4ec692425c6">苏凯</at>
                ### 开发负责人: <at user_id="ou_3f656bf45a45bc2a7a13fb9c898c23db">彭渲港</at>
                ### 时间: {}
                ########################
                """.format(len(work_list), work_list, current_time)
        params = {
            "msg_type": "text",
            "content": {
                "text": text_content
            }
        }
    response = requests.request('POST', url=url, json=params, headers=header,verify=False)


def flow_recod_moment(url,header,datatime=None):
    response = requests.request('get', url=url, headers=header, verify=False)
    response.encoding = 'utf-8'  # 设置响应内容的编码为UTF-8
    info = response.text
    info = json.loads(info)
    if datatime:
        for dict in info:
            assignment = dict.get("assignment")
            if assignment:
                updated_at = assignment.get("updated_at")
                return updated_at
    else:
        for dict in info:
            assignment = dict.get("assignment")
            if assignment:
                response = assignment.get("response")
                if response:
                    mapped_values = response.get("mapped_values")
                    if mapped_values and "result" in mapped_values:
                        result_value = mapped_values["result"]["value"][0]
                        return result_value
                else:
                    pass
            else:
                pass



