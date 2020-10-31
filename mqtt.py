# get the bitlair mqtt state

import paho.mqtt.client as mqtt

states = {
    'djo': False,
    'bitlair': False
}

def get_states():
    return states

def on_message(client, userdata, message):
    states['bitlair' if message.topic == 'bitlair/state' else 'djo'] = message.payload.decode('utf-8') == 'open'

client = mqtt.Client()
client.connect('mqtt.bitlair.nl') # no mqtt:// protocol needed

client.loop_start()

client.subscribe('bitlair/state')
client.subscribe('bitlair/state/djo')

client.on_message = on_message
