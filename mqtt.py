# get the bitlair mqtt state

import paho.mqtt.client as mqtt
from time import sleep

topics = {
    'bitlair/state': 'bitlair',
    'bitlair/state/djo': 'djo',
    'bitlair/climate/temperature-ceiling': 'temperature'
}

states = {}


def get_states():
    while [a for a in states.values() if not a]:
        sleep(1)

    return states


def on_message(_client, _userdata, message):
    topic = topics[message.topic]
    states[topic] = message.payload.decode('utf-8')


client = mqtt.Client()
client.connect('mqtt.bitlair.nl')  # no mqtt:// protocol needed

client.loop_start()

for topic, name in topics.items():
    states[name] = None
    client.subscribe(topic)

client.on_message = on_message
