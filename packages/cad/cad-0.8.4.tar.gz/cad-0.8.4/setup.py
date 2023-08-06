# encoding: utf-8
"""
##基于redis的AES加解密工具包

2/4/2020   Bruce  0.8.2   初始版本<br/>
2/5/2020   Bruce  0.8.3   补充调用及配置说明，更新引用方式<br/>

###使用方法：
####1、配置全局变量<br/>
变量名|类型|用途|示例
REDIS_ADDRESS|字符串|redis服务器地址,需要带上ip、端口、库号|127.0.0.1:6379/1
COMMON_SALT|字符串|解密密钥|0648ea5562efffee
APPLICATION_NAME|字符串|cad应用名|mms
APP_CONFIG_PREFIX|字符串|cad配置前缀|app-config

####2、引入模块<br/>
from cad.cad_util import CadUtil

####3、使用<br/>
`util = CadUtil()`<br/>
`res = util.get(ak)`<br/>

ak为应用对应的ak键<br/>
res 即得到的解析结果<br/>
结果格式如下<br/>
`{
    "ak": "0648ea5562efffee",
    "sk": "1e058d312eb61448",
    "permissions": {
        "app_1": ["auth_1", "auth_2"],
        "app_2': ["auth_3", "auth_4"]
    }
}`
"""
import sys
from setuptools import setup, find_packages
import cad

SHORT = 'cache aes decrypter'

if sys.platform == 'win32':
    setup(
        name='cad',
        version=cad.__version__,
        packages=find_packages(),
        install_requires=[
            'requests', 'redis', 'dynaconf', 'pycryptodome'
        ],
        long_description_content_type="text/markdown",
        url='',
        author=cad.__author__,
        author_email=cad.__email__,
        classifiers=[
            'Programming Language :: Python :: 3',
        ],
        include_package_data=True,
        package_data={'': ['*.py', '*.pyc']},
        zip_safe=False,
        platforms='any',

        description=SHORT,
        long_description=__doc__,
    )
else:
    setup(
        name='cad',
        version=cad.__version__,
        packages=find_packages(),
        install_requires=[
            'requests', 'redis', 'dynaconf', 'pycrypto'
        ],
        long_description_content_type="text/markdown",
        url='',
        author=cad.__author__,
        author_email=cad.__email__,
        classifiers=[
            'Programming Language :: Python :: 3',
        ],
        include_package_data=True,
        package_data={'': ['*.py', '*.pyc']},
        zip_safe=False,
        platforms='any',

        description=SHORT,
        long_description=__doc__,
    )
