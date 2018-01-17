# -*- coding:utf-8 -*-

import os
from django.core.exceptions import ImproperlyConfigured

os.environ["SECRET_KEY"]='jj1w37z7hgy*#&j)1(g@i=&l=o@e!5a4bx7+8kz6@bw!1z6$o2'
os.environ["LINE_CHANNEL_ACCESS_TOKEN"]='jUzO3UN2EQz2yQORB5xoGst3O0Plcep0gIy2ueKRIqb66u4yUvu7+m13W7zb61aUXifd8jQBthHm8CrvwTbYaACfKD+1V6SVPBHPbIRO3QWrm+KAjL1EsMMtreFjU8j2lwZZ5c7wYemiS6mFuV83PAdB04t89/1O/w1cDnyilFU='
os.environ["LINE_CHANNEL_SECRET"]='e9c595d4041e3a73a592157169cfb75c'
os.environ["CWB_API_KEY"]='CWB-6BD841A3-7C6C-4728-B2BE-EB212F54D25A'


def get_env_variable(var_name):
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = 'Set the {} environment variable'.format(var_name)
        raise ImproperlyConfigured(error_msg)
