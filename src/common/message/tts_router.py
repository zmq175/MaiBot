import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional
from maim_message import MessageBase, Seg, BaseMessageInfo, UserInfo, GroupInfo, FormatInfo
from src.common.logger_manager import get_logger
from src.config.config import global_config

logger = get_logger("tts_router")


class TTSRouter:
    """TTS消息路由器，负责将tts_text类型的消息路由到TTS适配器"""

    def __init__(self):
        self.tts_config = getattr(global_config, 'tts_adapter', None)
        self.enabled = self.tts_config and getattr(self.tts_config, 'enable', False)
        self.host = getattr(self.tts_config, 'host', '127.0.0.1') if self.tts_config else '127.0.0.1'
        self.port = getattr(self.tts_config, 'port', 8070) if self.tts_config else 8070
        self.session: Optional[aiohttp.ClientSession] = None
        
        if self.enabled:
            logger.info(f"TTS路由器已启用，目标地址: {self.host}:{self.port}")
        else:
            logger.warning("TTS路由器未启用，请检查配置文件中的tts_adapter设置")

    async def start(self):
        """启动TTS路由器"""
        if not self.enabled:
            logger.warning("TTS路由器未启用，跳过启动")
            return
            
        try:
            logger.debug("正在创建 aiohttp ClientSession...")
            self.session = aiohttp.ClientSession()
            logger.info("TTS路由器已启动")
            logger.debug(f"TTS路由器状态: enabled={self.enabled}, session={self.session is not None}")
        except Exception as e:
            logger.error(f"启动TTS路由器失败: {e}")
            self.session = None

    async def stop(self):
        """停止TTS路由器"""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("TTS路由器已停止")

    async def route_tts_message(self, message: MessageBase) -> bool:
        """路由TTS消息到TTS适配器"""
        logger.debug(f"TTS路由器状态检查: enabled={self.enabled}, session={self.session is not None}")
        if not self.enabled or not self.session:
            logger.warning("TTS路由器未启用或会话未创建")
            return False

        try:
            # 检查消息类型是否为tts_text
            if message.message_segment.type != "tts_text":
                return False

            # 构建发送到TTS适配器的消息
            tts_message = {
                "message_info": message.message_info.to_dict(),
                "message_segment": message.message_segment.to_dict(),
                "raw_message": message.raw_message
            }

            # 发送到TTS适配器
            url = f"ws://{self.host}:{self.port}/ws"
            logger.debug(f"正在连接到TTS适配器: {url}")
            async with self.session.ws_connect(url) as ws:
                await ws.send_json(tts_message)
                logger.info(f"TTS消息已发送到适配器: {message.message_segment.data[:50]}...")
                return True

        except Exception as e:
            logger.error(f"路由TTS消息失败: {e}")
            return False

    async def route_tts_text(self, text: str, platform: str, user_info: UserInfo, 
                           group_info: Optional[GroupInfo] = None) -> bool:
        """直接路由TTS文本到TTS适配器"""
        logger.debug(f"TTS路由器状态检查: enabled={self.enabled}, session={self.session is not None}")
        if not self.enabled or not self.session:
            logger.warning("TTS路由器未启用或会话未创建")
            return False

        try:
            # 构建TTS消息
            message_segment = Seg(type="tts_text", data=text)
            
            format_info = FormatInfo(
                content_format=["tts_text"],
                accept_format=["voice", "tts_text"]
            )
            
            message_info = BaseMessageInfo(
                platform=platform,
                user_info=user_info,
                group_info=group_info,
                format_info=format_info
            )
            
            message = MessageBase(
                message_info=message_info,
                message_segment=message_segment,
                raw_message=text
            )

            return await self.route_tts_message(message)

        except Exception as e:
            logger.error(f"路由TTS文本失败: {e}")
            return False


# 创建全局TTS路由器实例
tts_router = TTSRouter() 