"""Fish Audio TTS Action for MaiBot

This action provides text-to-speech functionality using Fish Audio API.
Supports random triggering and proxy access.
"""

import asyncio
import json
import random
import time
from typing import Optional, Dict, Any
import aiohttp
import msgpack
from pathlib import Path

from src.chat.focus_chat.planners.actions.base_action import BaseAction
from src.chat.message_receive.message import MaimMessage
from src.common.logger import logger


class FishAudioAction(BaseAction):
    """Fish Audio TTS Action
    
    Randomly triggers TTS synthesis using Fish Audio API.
    Supports proxy configuration for regions where Fish Audio is not directly accessible.
    """
    
    def __init__(self):
        super().__init__()
        self.name = "fish_audio_tts"
        self.description = "Fish Audio TTS synthesis with random triggering"
        self.trigger_probability = 0.1  # 10% chance to trigger
        self.api_base_url = "https://api.fish.audio/v1"
        self.proxy_url = None
        self.api_key = None
        self.model_id = None
        self.max_retries = 3
        self.timeout = 30
        
    async def can_execute(self, message: MaimMessage, **kwargs) -> bool:
        """Check if the action should be executed"""
        # Random trigger based on probability
        if random.random() > self.trigger_probability:
            return False
            
        # Only trigger on text messages
        if not message.content or not isinstance(message.content, str):
            return False
            
        # Skip very short messages
        if len(message.content.strip()) < 5:
            return False
            
        # Load configuration
        await self._load_config()
        
        # Check if we have required configuration
        if not self.api_key or not self.model_id:
            logger.warning("Fish Audio TTS: Missing API key or model ID")
            return False
            
        return True
        
    async def execute(self, message: MaimMessage, **kwargs) -> Optional[str]:
        """Execute the Fish Audio TTS action"""
        try:
            # Get the text to synthesize
            text = message.content.strip()
            
            # Generate speech
            audio_data = await self._generate_speech(text)
            
            if audio_data:
                # Save audio file
                audio_path = await self._save_audio(audio_data, message)
                
                # Send audio message
                await self._send_audio_message(audio_path, message)
                
                return f"🎵 已生成语音: {text[:50]}..."
            else:
                logger.error("Fish Audio TTS: Failed to generate speech")
                return None
                
        except Exception as e:
            logger.error(f"Fish Audio TTS action error: {e}")
            return None
            
    async def _load_config(self):
        """Load configuration from environment or config file"""
        import os
        from src.config.config import get_config
        
        config = get_config()
        
        # Load API key
        self.api_key = os.getenv("FISH_AUDIO_API_KEY")
        if not self.api_key:
            logger.warning("Fish Audio TTS: FISH_AUDIO_API_KEY not found in environment")
            
        # Load model ID
        self.model_id = os.getenv("FISH_AUDIO_MODEL_ID")
        if not self.model_id:
            logger.warning("Fish Audio TTS: FISH_AUDIO_MODEL_ID not found in environment")
            
        # Load proxy configuration
        self.proxy_url = os.getenv("FISH_AUDIO_PROXY_URL")
        
        # Load trigger probability from config
        if hasattr(config, 'fish_audio_tts'):
            tts_config = config.fish_audio_tts
            self.trigger_probability = getattr(tts_config, 'trigger_probability', 0.1)
            self.max_retries = getattr(tts_config, 'max_retries', 3)
            self.timeout = getattr(tts_config, 'timeout', 30)
            
    async def _generate_speech(self, text: str) -> Optional[bytes]:
        """Generate speech using Fish Audio API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/msgpack"
        }
        
        # Prepare request data
        request_data = {
            "model_id": self.model_id,
            "text": text,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        
        # Pack data using MessagePack
        packed_data = msgpack.packb(request_data)
        
        # Configure session with proxy if needed
        connector_kwargs = {}
        if self.proxy_url:
            connector_kwargs['proxy'] = self.proxy_url
            
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        
        for attempt in range(self.max_retries):
            try:
                async with aiohttp.ClientSession(
                    timeout=timeout,
                    connector=aiohttp.TCPConnector(**connector_kwargs) if connector_kwargs else None
                ) as session:
                    async with session.post(
                        f"{self.api_base_url}/tts",
                        headers=headers,
                        data=packed_data
                    ) as response:
                        if response.status == 200:
                            audio_data = await response.read()
                            logger.info(f"Fish Audio TTS: Successfully generated speech for '{text[:30]}...'")
                            return audio_data
                        else:
                            error_text = await response.text()
                            logger.error(f"Fish Audio TTS API error: {response.status} - {error_text}")
                            
            except asyncio.TimeoutError:
                logger.warning(f"Fish Audio TTS: Timeout on attempt {attempt + 1}")
            except Exception as e:
                logger.error(f"Fish Audio TTS: Error on attempt {attempt + 1}: {e}")
                
            if attempt < self.max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                
        return None
        
    async def _save_audio(self, audio_data: bytes, message: MaimMessage) -> Path:
        """Save audio data to file"""
        # Create audio directory if it doesn't exist
        audio_dir = Path("data/audio/fish_audio")
        audio_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        timestamp = int(time.time())
        filename = f"fish_audio_{timestamp}_{message.sender_id}.wav"
        audio_path = audio_dir / filename
        
        # Save audio file
        with open(audio_path, "wb") as f:
            f.write(audio_data)
            
        logger.info(f"Fish Audio TTS: Audio saved to {audio_path}")
        return audio_path
        
    async def _send_audio_message(self, audio_path: Path, message: MaimMessage):
        """Send audio message back to the chat"""
        try:
            # Import here to avoid circular imports
            from src.chat.message_receive.message_sender import MessageSender
            
            # Read audio file
            with open(audio_path, "rb") as f:
                audio_data = f.read()
                
            # Create audio message
            audio_message = MaimMessage(
                content="",
                sender_id=message.bot_id,
                receiver_id=message.receiver_id,
                message_type="audio",
                audio_data=audio_data,
                audio_path=str(audio_path)
            )
            
            # Send the message
            sender = MessageSender()
            await sender.send_message(audio_message)
            
        except Exception as e:
            logger.error(f"Fish Audio TTS: Failed to send audio message: {e}")
            
    def get_help(self) -> str:
        """Get help information for this action"""
        return """
🎵 Fish Audio TTS Plugin

功能：
- 随机触发语音合成
- 支持代理访问Fish Audio API
- 自动保存和发送语音消息

配置要求：
- FISH_AUDIO_API_KEY: Fish Audio API密钥
- FISH_AUDIO_MODEL_ID: 语音模型ID
- FISH_AUDIO_PROXY_URL: 代理URL（可选）

触发概率：10%（可配置）
        """ 