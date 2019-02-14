#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
from hermes_python.hermes import Hermes
from hermes_python.ontology import *
import io
import time
import boost_utils as bu
CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"

class SnipsConfigParser(configparser.SafeConfigParser):
    def to_dict(self):
        return {section : {option_name : option for option_name, option in self.items(section)} for section in self.sections()}

def read_configuration_file(configuration_file):
    try:
        with io.open(configuration_file, encoding=CONFIGURATION_ENCODING_FORMAT) as f:
            conf_parser = SnipsConfigParser()
            conf_parser.readfp(f)
            return conf_parser.to_dict()
    except (IOError, configparser.Error) as e:
        return dict()

def subscribe_intent_callback(hermes, intentMessage):
    conf = read_configuration_file(CONFIG_INI)
    action_wrapper(hermes, intentMessage, conf)

def action_wrapper(hermes, intentMessage, conf):
    current_session_id = intentMessage.session_id

    if intentMessage.slots.direction:
        direction = intentMessage.slots.direction.first().value.encode("utf-8")
        print(direction)
    else:
        hermes.publish_continue_session(current_session_id, "No direction!", ['lifidea:Move'])
        return
    try:
        if direction in [b'L', b'left']:
            bu.send_cmd('left')
        elif direction in [b'R', b'right']:
            bu.send_cmd('right')
        elif direction in [b'front', b'forward']:
            bu.send_cmd('front')
        elif direction in [b'back', b'backward']:
            bu.send_cmd('back')
        elif direction in [b'around', b'circle']:
            bu.send_cmd('circle')
        elif direction in [b'random', b'drunken']:
            bu.send_cmd('random')
        else:
            hermes.publish_continue_session(current_session_id, "Unknown direction", ['lifidea:Move'])
            return

        hermes.publish_continue_session(current_session_id, "Done!", ['lifidea:Move'])
    finally:
        pass

if __name__ == "__main__":
    with Hermes("localhost:1883") as h:
        h.subscribe_intent("lifidea:Move", subscribe_intent_callback) \
         .start()
