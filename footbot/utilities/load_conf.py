# -*- coding: utf-8 -*-
import os
from django.conf import settings


def load_conf(conf_name, conf_item=None):
    config_file = os.path.join(settings.CONF, conf_name)
    config = {}

    try:
        exec(open(config_file).read())

        if conf_item:
            config = config[conf_item]
    except:
        pass

    return config


def write_conf(conf_name, conf_item, val):
    config_file = os.path.join(settings.CONF, conf_name)

    try:
        data = str(conf_item) + " = " + str(val)

        with open(config_file, 'w') as file_write:
            file_write.write(data)
    except:
        pass

