# coding: utf-8
from django.http import HttpRequest


def get_real_ip(request: HttpRequest):
    """
    获取用户真实 IP

    :param request:
    :return:
    """
    real_ip = request.META.get('HTTP_X_REAL_IP', None) or request.META['REMOTE_ADDR']
    return real_ip
