#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
from hermes_python.hermes import Hermes
from hermes_python.ontology import *
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import io
import time
CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"

MQTT_SERVER = "localhost"
MQTT_PATH_SS = "lifidea/controlBoost/response"

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(MQTT_PATH_SS)

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_SERVER, 1883, 60)

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
    """ Write the body of the function that will be executed once the intent is recognized. 
    In your scope, you have the following objects : 
    - intentMessage : an object that represents the recognized intent
    - hermes : an object with methods to communicate with the MQTT bus following the hermes protocol. 
    - conf : a dictionary that holds the skills parameters you defined. 
      To access global parameters use conf['global']['parameterName']. For end-user parameters use conf['secret']['parameterName'] 
     
    Refer to the documentation for further details. 
    """
    current_session_id = intentMessage.session_id
    
    if intentMessage.slots.direction:
        direction = intentMessage.slots.direction.first().value.encode("utf-8")
        print(direction)
    else:
        hermes.publish_continue_session(current_session_id, "No direction!", ['lifidea:Move'])
        return
    try:
        if direction in [b'L', b'left']:
            publish.single("lifidea/boost/request", "move left", hostname=MQTT_SERVER)
        elif direction in [b'R', b'right']:
            publish.single("lifidea/boost/request", "move right", hostname=MQTT_SERVER)
        elif direction in [b'front', b'forward']:
            publish.single("lifidea/boost/request", "move front", hostname=MQTT_SERVER)
        elif direction in [b'back', b'backward']:
            publish.single("lifidea/boost/request", "move back", hostname=MQTT_SERVER)
        elif direction in [b'around', b'circle']:
            publish.single("lifidea/boost/request", "move around", hostname=MQTT_SERVER)
        elif direction in [b'random', b'drunken']:
            publish.single("lifidea/boost/request", "move random", hostname=MQTT_SERVER)
        else:
            hermes.publish_continue_session(current_session_id, "Unknown direction", ['lifidea:Move'])
            return
        
        hermes.publish_continue_session(current_session_id, "Done!", ['lifidea:Move'])
    finally:
        #time.sleep(1)
        pass
        # mymovehub.stop()


if __name__ == "__main__":
    with Hermes("localhost:1883") as h:
        h.subscribe_intent("lifidea:Move", subscribe_intent_callback) \
         .start()
