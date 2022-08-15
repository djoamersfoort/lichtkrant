#!/usr/bin/env python

import argparse
import importlib.util
import random
import time
from glob import glob
from os import path
from time import sleep
from typing import Optional, Any, List

import mqtt
from states.base import BaseState
from states.socket import Socket


class LichtKrant:

    def __init__(self, cmd_args):
        self.args = cmd_args
        mqtt.connect(not cmd_args.offline)
        self.modules = None
        self.states = {}
        self.socket = Socket(self)
        self.socket.start()

    def import_module(self, loc: str) -> (Optional[Any], str):
        name = path.basename(loc).replace('.mod.py', '', -1)
        spec = importlib.util.spec_from_file_location(name, loc)
        module = spec.loader.load_module()
        return module, name

    def add_player(self, game, player):
        self.read_states()
        if game not in self.states:
            return
        state = self.states[game]
        if not state.is_game:
            return
        state.add_player(player)

    def read_modules(self, location: str) -> List[Any]:
        # loading state modules
        return [self.import_module(file) for file in glob(location, recursive=self.args.recursive)]

    def read_states(self) -> None:
        if self.modules is None:
            self.modules = self.read_modules(self.args.state_dir + '**/**/*.mod.py')

        for module, name in self.modules:
            # Re-create any missing states (killed threads)
            if name not in self.states:
                try:
                    state = module.State()
                except Exception:
                    continue
                state.name = name
                self.states[name] = state

    def kill_state(self, state: BaseState) -> None:
        state.kill()
        state.join()
        # Remove the state, because Thread's can only be start()ed once
        del self.states[state.name]

    def get_state(self, space_state: dict) -> Optional[BaseState]:
        self.read_states()

        # getting highest indexed state
        if self.args.module is not None:
            state = self.states.get(args.module)
            if state is None:
                raise Exception('The module passed does not exist.')
            return state

        # filter states
        filtered_states = []
        for name, state in self.states.items():
            try:
                if state.check(space_state):
                    filtered_states.append(state)
            except Exception as e:
                # The state's check() method crashed -> ignore it
                if self.args.dry:
                    print(f"State module {name} check method crashed: {e}")

        # return a random state with the highest index
        random.shuffle(filtered_states)

        if len(filtered_states) == 0:
            return None

        return sorted(filtered_states, key=lambda s: s.index, reverse=True)[0]

    def run_state(self, state: BaseState) -> Optional[BaseState]:
        # running states
        if self.args.dry:
            print(f"state: {state.name}")
            return None

        state.start()
        return state

    def state_loop(self) -> None:
        # the state update loop
        current_state = None
        current_thread = None

        while True:
            space_state = mqtt.get_states()
            new_state = self.get_state(space_state)

            if new_state != current_state:
                current_state = new_state

                if current_thread is not None:
                    self.kill_state(current_thread)

                if current_state is not None:
                    current_thread = self.run_state(current_state)

            # delay or force update if necessary
            end_time = time.time() + new_state.delay

            while True:
                if time.time() >= end_time:
                    break

                # Check if current state wants to disable itself
                if not new_state.check(space_state):
                    break

                diff_state = self.get_state(space_state)

                if diff_state.index > new_state.index:
                    break

                sleep(4)

    def start(self) -> None:
        self.state_loop()


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
