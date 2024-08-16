import os
from dotenv import load_dotenv
load_dotenv()
import asyncio
import time

from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions
from viam.components.board import Board
from viam.components.servo import Servo

async def connect():
    opts = RobotClient.Options.with_api_key( 
        api_key=os.getenv('api_key'),
        api_key_id=os.getenv('api_key_id')
    )
    return await RobotClient.at_address('lunch-gong-main.ldnf5a9i14.viam.cloud', opts)

async def main():
    machine = await connect()

    print('Resources:')
    print(machine.resource_names)
    
    # Note that the pin supplied is a placeholder. Please change this to a valid pin you are using.
    # board-1
    board_1 = Board.from_robot(machine, "board-1")
    board_1_return_value = await board_1.gpio_pin_by_name("16")
    print(f"board-1 gpio_pin_by_name return value: {board_1_return_value}")
  
    # servo-1
    servo_1 = Servo.from_robot(machine, "servo-1")
    servo_1_return_value = await servo_1.get_position()
    print(f"servo-1 get_position return value: {servo_1_return_value}")
    await servo_1.move(0)
    time.sleep(1)
    await servo_1.move(180)
    # Don't forget to close the machine when you're done!
    await machine.close()

if __name__ == '__main__':
    asyncio.run(main())
