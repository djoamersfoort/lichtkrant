#!/usr/bin/env python

import argparse
import random
import sys
from datetime import datetime
from subprocess import Popen
from time import sleep
from glob import glob
import yaml
from mqtt import get_states

# parsing command-line arguments
parser = argparse.ArgumentParser(
    description='A driver for the DJO Lichtkrant project.')

parser.add_argument('-m', '--module', default=None,
                    help='load a specific module by name')
parser.add_argument('-s', '--state-dir', default='./states',
                    help='path to the states directory')
parser.add_argument('-r', '--recursive', type=bool,
                    default=True, help='whether to search recursively')
parser.add_argument('-d', '--dry', action='store_true',
                    default=False, help='do not spew out pixel data')

args = parser.parse_args()


def read_dir(location):
    # loading state modules
    return [yaml.safe_load(open(file, 'r')) for file in glob(
        location, recursive=args.recursive)]


def get_state(states, space_state):
    # getting highest indexed state
    if args.module is not None:
        try:
            return [s for s in states if s['name'] == args.module][0]
        except IndexError:
            raise Exception('The module passed does not exist.')

    # filter states
    filtered_states = [s for s in states if (eval(s['check'], space_state) if isinstance(s['check'], str) else s['check'])]

    # return random with highest index
    random.shuffle(filtered_states)
    if not filtered_states:
        return None
    return sorted(filtered_states, key=lambda s: s['index'], reverse=True)[0]


def run_state(state):
    # running states
    if args.dry:
        print(f"state: {state['name']}")
        return None
    if 'module' in state:
        return Popen([sys.executable, state['module']])
    if 'command' in state:
        return Popen(state['command'], shell=True)
    return None


def state_loop():
    # read all modules
    state_modules = read_dir(args.state_dir + '**/**/*.yaml')

    # the state update loop
    current_state = None
    current_process = None

    while True:
        space_state = get_states()

        new_state = get_state(state_modules, {
            'states': space_state,
            'now': datetime.now()
        })

        if new_state != current_state:
            current_state = new_state

            if current_process is not None:
                current_process.kill()

            if current_state is not None:
                current_process = run_state(current_state)

        if 'delay' in current_state:
            sleep(current_state['delay'])
        else:
            raise Exception('The module does not contain a delay.')


try:
    state_loop()
except KeyboardInterrupt:
    pass  # no ugly error message
