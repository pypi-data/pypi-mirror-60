#!/usr/bin/env python
# -*- coding:utf-8 _*-  
"""
@author  : Lin Luo / Bruce Liu
@time    : 2020/1/20 14:09
@contact : 15869300264@163.com
"""
from .cad_util import CadUtil


class AppConfigUtil(object):
    def __init__(self):
        self._cad_client = CadUtil()

    def get_sk(self, ak, dict_obj: dict = None) -> str or None:
        """
        根据ak获取sk
        :param ak:
        :param dict_obj: redis中的用户信息，如果没有传入，则从redis中读取
        :return: 如果后去失败，则返回None
        """
        if dict_obj is None:
            dict_obj = self._cad_client.get(ak)
            if dict_obj is None:
                return None
        else:
            return dict_obj.get('sk')

    def check(self, ak: str, sk: str, app: str, auth_code: str = None, dict_obj: dict = None) -> bool:
        """
        校验ak权限
        :param ak:
        :param sk: 允许sk传入None，则跳过sk判断过程
        :param app: 应用名称
        :param auth_code: 权限code ，如果没有传入，则只判断是否存在应用名称
        :param dict_obj: redis中的用户信息，如果没有传入，则从redis中读取
        :return:
        """
        # 判断是否传入用户信息
        if dict_obj is None:
            # 如果没有传入，则从redis中读取
            dict_obj = self._cad_client.get(ak)
            # 判断读取的数据是否为None
            if dict_obj is None:
                # 如果为None，则返回False
                return False
        # 如果sk不为None，判断aksk是否有效
        if sk is not None and dict_obj.get('sk') != sk:
            return False
        permissions = dict_obj.get('permissions', {})
        # 判断auth_code是否为None
        if auth_code is None:
            # 如果为None，则判断是否存在对应应用
            if permissions.get(app) is None:
                # 如果不存在，则返回False
                return False
            else:
                # 如果存在则返回True
                return True
        else:
            # 如果不为None，则判断对应应用中是否存在对应auth_code
            if auth_code not in permissions.get(app, {}):
                # 如果不存在，则返回False
                return False
            else:
                # 如果存在，则返回True
                return True
