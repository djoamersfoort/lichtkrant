#!/usr/bin/env python

import importlib.util
import argparse
import random
import mqtt
import time

from os import path
from time import sleep
from glob import glob
from multiprocessing import Process


class LichtKrant:

    def __init__(self, args):
        self.module_context = {}
        self.args = args
        mqtt.connect(not args.offline)

    def import_module(self, loc):
        name = path.basename(loc).replace('.mod.py', '', -1)
        spec = importlib.util.spec_from_file_location(name, loc)

        module = spec.loader.load_module()
        if hasattr(module, 'init'):
            context = module.init()
            self.module_context[module.name] = context
        return module

    def read_dir(self, location):
        # loading state modules
        return [self.import_module(file) for file in glob(location, recursive=self.args.recursive)]

    def get_state(self, states, space_state):
        # getting highest indexed state
        if self.args.module is not None:
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

    def run_state(self, state):
        # running states
        if self.args.dry:
            print(f"state: {state.name}")
            return None

        states = mqtt.get_states()
        context = self.module_context[state.name] if state.name in self.module_context else None
        if context is not None:
            process = Process(target=state.run, args=(states, context))
        else:
            process = Process(target=state.run, args=(states,))
        process.start()

        return process

    def state_loop(self):
        # read all modules
        state_modules = self.read_dir(self.args.state_dir + '**/**/*.mod.py')

        # the state update loop
        current_state = None
        current_process = None

        while True:
            space_state = mqtt.get_states()
            new_state = self.get_state(state_modules, space_state)

            if new_state != current_state:
                current_state = new_state

                if current_process is not None:
                    current_process.terminate()
                    sleep(1)  # sleep to reset outlining

                if current_state is not None:
                    current_process = self.run_state(current_state)

            # delay or force update if necessary
            end_time = time.time() + new_state.delay

            while True:
                if time.time() >= end_time:
                    break

                diff_state = self.get_state(state_modules, space_state)

                if diff_state.index > new_state.index:
                    break

                sleep(4)

    def start(self):
        try:
            self.state_loop()
        except KeyboardInterrupt:
            pass  # no ugly error message


if __name__ == '__main__':
    # parsing command-line arguments
    parser = argparse.ArgumentParser(description='A driver for the DJO Lichtkrant project.')

    parser.add_argument('-m', '--module', default=None, help='load a specific module by name')
    parser.add_argument('-s', '--state-dir', default='./states', help='path to the states directory')
    parser.add_argument('-r', '--recursive', type=bool, default=True, help='whether to search recursively')
    parser.add_argument('-d', '--dry', action='store_true', default=False, help='do not spew out pixel data')
    parser.add_argument('-o', '--offline', action='store_true', default=False, help='disable MQTT connectivity')

    args = parser.parse_args()

    lichtkrant = LichtKrant(args)
    lichtkrant.start()
