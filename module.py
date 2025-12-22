#!/home/tenzingdoleck/.cargo/bin/uv run

import asyncio
import time
from viam.components.generic import Generic
from viam.components.servo import Servo
from viam.components.board import Board
from viam.resource.easy_resource import EasyResource
from viam.module.module import Module
import asyncio


class MyGeneric(Generic, EasyResource):
    MODEL = "tenzing:generic:gong"
    servo = None
    board = None


    def reconfigure(self, config, deps):
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
        if text==None or CONFIG.SUBTEAM in text:
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
