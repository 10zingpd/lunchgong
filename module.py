#!/usr/bin/env python3

import asyncio
import time
import os
import re
import logging
from typing import Mapping
from gtts import gTTS

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
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
        # Extract subteam from protobuf Value and convert to string
        subteam_value = config.attributes.fields.get('subteam')
        if subteam_value:
            # Handle protobuf Value type - extract string_value
            if hasattr(subteam_value, 'string_value'):
                self.subteam = subteam_value.string_value
            else:
                self.subteam = str(subteam_value)
        else:
            self.subteam = ''
        logger.info(f"subteam configured as: {self.subteam}")
        logger.info(f"DEPS: {dependencies}")
        dependencies_list = list(dependencies.values())
        
        # Find servo, board, and audioout components
        for dep in dependencies_list:
            if isinstance(dep, Servo):
                self.servo = dep
            elif isinstance(dep, Board):
                self.board = dep
            elif isinstance(dep, AudioOut):
                self.audioout = dep
        
        logger.info(f'isInstance (servo): {isinstance(self.servo, Servo)}')
        logger.info(f'isInstance (board): {isinstance(self.board, Board)}')
        logger.info(f'isInstance (audioout): {isinstance(self.audioout, AudioOut)}')
        logger.info("Reconfiguration done")

    async def do_command(self, command: dict, **kwargs):
        should_trigger = False
        try:
            text = command.get('text')
            # Convert to string if it's not already
            if text is not None and not isinstance(text, str):
                text = str(text)
            logger.info(f'Received command with text: {text}')
            logger.info(f'Text type: {type(text)}, Text repr: {repr(text)}')
            # ids for @nyc-lunch (S050ABF8T4Y) and Slack group S0A52MERWTY
            slack_group_ids = ['S0A52MERWTY', 'S050ABF8T4Y']
            
            # Check each condition separately
            text_is_none = text is None
            subteam_match = False
            if text and self.subteam:
                # Ensure subteam is a string
                subteam_str = str(self.subteam) if not isinstance(self.subteam, str) else self.subteam
                subteam_match = subteam_str in text
            group_id_matches = []
            if text:
                for group_id in slack_group_ids:
                    found = group_id in text
                    group_id_matches.append(found)
                    logger.info(f'Checking group_id {group_id} in text: {found}')
            
            should_trigger = text_is_none or subteam_match or any(group_id_matches)
            logger.info(f'should_trigger: {should_trigger}')
            logger.info(f'  - text is None: {text_is_none}')
            logger.info(f'  - subteam match: {subteam_match} (subteam={self.subteam})')
            logger.info(f'  - group_id matches: {group_id_matches}')
        except Exception as e:
            logger.error(f"Error in do_command condition check: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {"ran": False, "error": str(e)}
        
        if should_trigger:
            try:
                logger.info("Triggering gong sequence...")
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

                if self.audioout:
                    # Generate speech: "Lunch from [slack message] is here"
                    speech_text = "Lunch is here"
                    if text:
                        # Remove Slack mention format like <!subteam^S0A52MERWTY>
                        cleaned_text = re.sub(r'<!subteam\^[^>]+>', '', text).strip()
                        if cleaned_text:
                            speech_text = f"Lunch from {cleaned_text} is here"
                    temp_mp3 = "/tmp/tts.mp3"
                    gTTS(text=speech_text, lang='en').save(temp_mp3)

                    with open(temp_mp3, 'rb') as f:
                        mp3_data = f.read()
                    os.remove(temp_mp3)

                    audio_info = AudioInfo(codec=AudioCodec.MP3, sample_rate_hz=24000, num_channels=1)
                    await self.audioout.play(mp3_data, audio_info)

                logger.info("Gong sequence completed successfully")
                return {"ran": True}
            except Exception as e:
                logger.error(f"Error in gong sequence: {e}")
                import traceback
                logger.error(traceback.format_exc())
                return {"ran": False, "error": str(e)}
        else:
            logger.info("Condition not met, not triggering gong")
        return {"ran":False}
    
    async def _speak(self, text: str):
        """Text to speech."""
        if not self.audioout:
            logger.warning("AudioOut component not available, skipping audio playback")
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
