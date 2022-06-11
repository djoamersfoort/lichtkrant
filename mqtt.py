# get the bitlair mqtt state

import paho.mqtt.client as mqtt

topics = {
    'bitlair/state': 'bitlair',
    'bitlair/state/djo': 'djo',
    'bitlair/climate/temperature-ceiling': 'temperature'
}

states = {}


def get_states() -> dict:
    return states


def on_message(_client, _userdata, message):
    topic = topics[message.topic]
    states[topic] = message.payload.decode('utf-8')


def connect(online: bool):
    if online:
        client = mqtt.Client()
        client.connect('mqtt.bitlair.nl')  # no mqtt:// protocol needed

        client.loop_start()
        client.on_message = on_message

    for topic, name in topics.items():
        states[name] = None

        if online:
            client.subscribe(topic)
