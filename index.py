#!/usr/bin/env python

import importlib.util
import threading
import argparse
import random

from time import sleep
from glob import glob
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


def import_module(path):
    spec = importlib.util.spec_from_file_location('', path)
    return spec.loader.load_module()


def read_dir(location):
    # loading state modules
    return [import_module(file) for file in glob(
        location, recursive=args.recursive)]


def get_state(states, space_state):
    # getting highest indexed state
    if args.module is not None:
        try:
            return [s for s in states if s.name == args.module][0]
        except IndexError:
            raise Exception('The module passed does not exist.')

    # filter states
    filtered_states = [s for s in states if s.check(space_state)]

    # return random with highest index
    random.shuffle(filtered_states)

    if not filtered_states:
        return None

    return sorted(filtered_states, key=lambda s: s.index, reverse=True)[0]


def run_state(state):
    # running states
    if args.dry:
        print(f"state: {state.name}")
        return None

    thread = threading.Thread(target=state.run)
    thread.start()

    return thread


def state_loop():
    # read all modules
    state_modules = read_dir(args.state_dir + '**/**/*.mod.py')

    # the state update loop
    current_state = None
    current_thread = None

    while True:
        space_state = get_states()
        new_state = get_state(state_modules, space_state)

        if new_state != current_state:
            current_state = new_state

            if current_thread is not None:
                current_thread.stop()

            if current_state is not None:
                current_thread = run_state(current_state)

        # delay
        sleep(current_state.delay if current_state is not None else 1)


try:
    state_loop()
except KeyboardInterrupt:
    pass  # no ugly error message
