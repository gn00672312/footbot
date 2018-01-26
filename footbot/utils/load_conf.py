# -*- coding: utf-8 -*-
import os
from django.conf import settings


def load_conf(conf_name, conf_item=None):
    config_file = os.path.join(settings.CONF, conf_name)
    config = {}

    try:
        with open(config_file) as f:
            exec(f.read(), {}, config)

        if conf_item:
            config = config[conf_item]

    except Exception as e:
        print('error', e)

    return config


def write_conf(conf_name, conf_item, val):
    config_file = os.path.join(settings.CONF, conf_name)

    try:
        data = str(conf_item) + " = " + str(val)

        with open(config_file, 'w') as file_write:
            file_write.write(data)
    except:
        pass

