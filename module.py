#!/usr/bin/env python3

import asyncio
import time
import os
from typing import Mapping
from gtts import gTTS
from viam.components.generic import Generic
from viam.components.servo import Servo
from viam.components.board import Board
from viam.components.audio_out import AudioOut, AudioInfo, AudioCodec
from viam.resource.easy_resource import EasyResource
from viam.module.module import Module
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName
from viam.resource.base import ResourceBase


class MyGeneric(Generic, EasyResource):
    MODEL = "10zing:generic:gong"
    servo = None
    board = None
    audioout = None
    subteam = ''

    @classmethod
    def new(cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]):
        self = super().new(config, dependencies)
        self.reconfigure(config, dependencies)
        return self

    def reconfigure(self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]):
        self.subteam = config.attributes.fields['subteam']
        print("DEPS", dependencies)
        dependencies_list = list(dependencies.values())
        
        # Find servo, board, and audioout components
        for dep in dependencies_list:
            if isinstance(dep, Servo):
                self.servo = dep
            elif isinstance(dep, Board):
                self.board = dep
            elif isinstance(dep, AudioOut):
                self.audioout = dep
        
        print('isInstance (servo)', isinstance(self.servo, Servo))
        print('isInstance (board)', isinstance(self.board, Board))
        print('isInstance (audioout)', isinstance(self.audioout, AudioOut))
        print("done")

    async def do_command(self, command: dict, **kwargs):
        text = command.get('text')
        print('text', text)
        # id for @nyc-lunch
        if text is None or self.subteam in text:
            # Generate and play text-to-speech announcement
            if text:
                try:
                    # Play audio in a non-blocking way
                    asyncio.create_task(self._speak(text))
                except Exception as e:
                    print(f"Error with text-to-speech: {e}")
            
            pin = await self.board.gpio_pin_by_name(name="11")
            await pin.set(high=True)
            time.sleep(0.1)
            await self.servo.move(110)
            time.sleep(0.5)
            await self.servo.move(90)
            time.sleep(0.2)
            await self.servo.move(110)
            time.sleep(0.5)
            await pin.set(high=False)

            temp_mp3 = "/tmp/tts.mp3"
            gTTS(text="Hello World", lang='en').save(temp_mp3)

            with open(temp_mp3, 'rb') as f:
                mp3_data = f.read()
            os.remove(temp_mp3)

            audio_info = AudioInfo(codec=AudioCodec.MP3, sample_rate_hz=24000, num_channels=1)
            await self.audioout.play(mp3_data, audio_info)
            
            return {"ran": True}
        return {"ran":False}
    
    async def _speak(self, text: str):
        """Text to speech."""
        if not self.audioout:
            print("AudioOut component not available, skipping audio playback")
            return
        
        temp_mp3 = "/tmp/tts.mp3"
        gTTS(text=text, lang='en').save(temp_mp3)

        with open(temp_mp3, 'rb') as f:
            mp3_data = f.read()
        os.remove(temp_mp3)

        audio_info = AudioInfo(codec=AudioCodec.MP3, sample_rate_hz=24000, num_channels=1)
        await self.audioout.play(mp3_data, audio_info)


if __name__ == '__main__':
    asyncio.run(Module.run_from_registry())
