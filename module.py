#!/usr/bin/env python3

import asyncio
import time
from typing import Mapping
from viam.components.generic import Generic
from viam.components.servo import Servo
from viam.components.board import Board
from viam.resource.easy_resource import EasyResource
from viam.module.module import Module
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName
from viam.resource.base import ResourceBase


class MyGeneric(Generic, EasyResource):
    MODEL = "10zing:generic:gong"
    servo = None
    board = None
    subteam = ''


    def reconfigure(self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]):
        self.subteam = config.attributes.fields['subteam']
        global servo
        global board
        print("DEPS", deps)
        deps = iter(deps.values())
        fst = next(deps)
        snd = next(deps)
        if isinstance(fst, Servo):
            servo = fst
            board = snd
        else:
            servo = snd
            board = fst
        print('isInstance (servo)', isinstance(servo, Servo))
        print('isInstance (board)', isinstance(board, Board))
        print("done")


    async def do_command(self, command: dict, **kwargs):
        global servo
        global board
        text = command.get('text')
        print('text', text)
        # id for @nyc-lunch
        if text==None or self.subteam in text:
            pin = await board.gpio_pin_by_name(name="11")
            await pin.set(high=True)
            time.sleep(0.1)
            await servo.move(110)
            time.sleep(0.5)
            await servo.move(90)
            time.sleep(0.2)
            await servo.move(110)
            time.sleep(0.5)
            await pin.set(high=False)

            return {"ran": True}
        return {"ran":False}


if __name__ == '__main__':
    asyncio.run(Module.run_from_registry())
