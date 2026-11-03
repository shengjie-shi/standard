"""
Description: 

@Author: ssjie

Created on: 2021/8/9
"""


def success(ai_custome, **kwargs):
    """
    请求成功返回结果
    :param ai_custome:自定义内容
    :return:
    """
    ai_status = {'code': '0', 'error_msg': ''}
    response = {'status': ai_status, 'result': ai_custome}

    response.update(kwargs)

    return response


def fail(error_msg):
    """
    请求失败返回结果
    :param error_msg:错误消息
    :return:
    """
    ai_status = {'code': '1', 'error_msg': error_msg}
    response = {'status': ai_status, 'result': {}}
    return response