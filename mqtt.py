# get the bitlair mqtt state

import paho.mqtt.client as mqtt

states = {
    'djo': None,
    'bitlair': None
}


def get_states():
    return states


def on_message(_client, _userdata, message):
    topic = 'bitlair' if message.topic == 'bitlair/state' else 'djo'
    states[topic] = message.payload.decode('utf-8') == 'open'


client = mqtt.Client()
client.connect('bitlair.nl')  # no mqtt:// protocol needed

client.loop_start()

client.subscribe('bitlair/state')
client.subscribe('bitlair/state/djo')

client.on_message = on_message
