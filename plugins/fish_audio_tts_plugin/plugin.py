"""Fish Audio TTS Plugin for MaiBot

This plugin provides text-to-speech functionality using Fish Audio API.
Supports LLM-based triggering and proxy access for regions where Fish Audio is not directly accessible.
"""

import asyncio
import json
import time
from typing import Optional, Dict, Any, Tuple, List, Type
import httpx
import msgpack
from pathlib import Path
import os

from src.plugin_system import (
    BasePlugin, register_plugin, BaseAction, BaseCommand,
    ComponentInfo, ActionActivationType, ChatMode, ConfigField
)
from src.common.logger import get_logger

logger = get_logger("fish_audio_tts")


class FishAudioAction(BaseAction):
    """Fish Audio TTS Action
    
    Uses LLM to intelligently decide when to trigger TTS synthesis using Fish Audio API.
    Supports proxy configuration for regions where Fish Audio is not directly accessible.
    """

    # 激活设置 - Focus模式使用LLM判断，Normal模式一直激活
    focus_activation_type = ActionActivationType.LLM_JUDGE
    normal_activation_type = ActionActivationType.ALWAYS
    mode_enable = ChatMode.ALL
    parallel_action = False
    
    # Normal模式下的随机激活概率（LLM_JUDGE会被转换为概率激活）
    random_activation_probability = 0.15  # 15%的概率，相对保守

    # LLM判断提示词（用于Focus模式）
    llm_judge_prompt = """
判定是否需要使用Fish Audio TTS语音功能的条件：

建议使用语音的情况：
1. 用户明确要求语音回复、朗读或听语音
2. 对话内容包含情感表达、故事、诗歌等适合语音传达的内容
3. 回复内容较长且适合语音播报
4. 想要增强互动体验，让对话更加生动有趣
5. 回复内容包含问候、祝福、感谢等情感性表达
6. 用户询问或讨论语音相关话题
7. 对话氛围轻松愉快，适合使用语音增强表达效果
8. 想要提供更丰富的交互方式

不建议使用语音的情况：
1. 对话内容过于技术性或专业性，不适合语音传达
2. 用户明确表示不需要语音回复
3. 对话内容包含大量数字、代码或特殊符号
4. 当前环境不适合播放语音

请根据以上条件判断是否需要使用语音功能，回答"是"或"否"。
"""

    # 动作基本信息
    action_name = "fish_audio_tts_action"
    action_description = "用语音的方式进行回复"

    # 动作参数定义
    action_parameters = {
        "text": "需要转换为语音的文本内容，必填",
    }

    # 动作使用场景 - 优化描述，让AI更愿意使用
    action_require = [
        "用户要求语音回复",
        "想要增强互动体验",
        "包含情感表达",
        "回复内容较长",
        "适合用语音表达",
        "想要更生动的表达",
    ]

    # 关联类型
    associated_types = []  # 移除类型限制，避免在normal模式下被过滤

    def __init__(
        self,
        action_data: dict,
        reasoning: str,
        cycle_timers: dict,
        thinking_id: str,
        chat_stream=None,
        log_prefix: str = "",
        shutting_down: bool = False,
        plugin_config: dict = None,
        **kwargs,
    ):
        # 调用父类初始化
        super().__init__(
            action_data=action_data,
            reasoning=reasoning,
            cycle_timers=cycle_timers,
            thinking_id=thinking_id,
            chat_stream=chat_stream,
            log_prefix=log_prefix,
            shutting_down=shutting_down,
            plugin_config=plugin_config,
            **kwargs,
        )
        
        # Fish Audio TTS 特定配置
        self.api_base_url = "https://api.fish.audio/v1"
        self.proxy_url = None
        self.api_key = None
        self.model_id = None
        self.max_retries = 3
        self.timeout = 30

    async def can_execute(self) -> bool:
        """Check if the action should be executed"""
        # Load configuration
        await self._load_config()
        
        # Check if we have required configuration
        if not self.api_key or not self.model_id:
            logger.warning("Fish Audio TTS: Missing API key or model ID")
            return False
            
        return True

    async def execute(self) -> Tuple[bool, str]:
        """Execute the Fish Audio TTS action"""
        try:
            # Load configuration first
            await self._load_config()
            
            # Get the text to synthesize
            text = self.action_data.get("text", "")
            
            if not text:
                logger.error(f"{self.log_prefix} 执行Fish Audio TTS动作时未提供文本内容")
                return False, "执行Fish Audio TTS动作失败：未提供文本内容"

            # Ensure text is suitable for TTS
            processed_text = self._process_text_for_tts(text)
            
            # Generate speech
            audio_data = await self._generate_speech(processed_text)
            
            if audio_data:
                # Save audio file
                audio_path = await self._save_audio(audio_data)
                
                # Convert to absolute path for napcat compatibility
                absolute_audio_path = str(audio_path.absolute())
                
                # Send audio message using voiceurl type
                await self.send_custom(message_type="voiceurl", content=absolute_audio_path)
                
                logger.info(f"{self.log_prefix} Fish Audio TTS动作执行成功，文本长度: {len(processed_text)}")
                return True, f"Fish Audio TTS动作执行成功: {processed_text[:50]}..."
            else:
                logger.error(f"{self.log_prefix} Fish Audio TTS生成语音失败")
                return False, "Fish Audio TTS生成语音失败"
                
        except Exception as e:
            logger.error(f"{self.log_prefix} 执行Fish Audio TTS动作时出错: {e}")
            return False, f"执行Fish Audio TTS动作时出错: {e}"

    async def _load_config(self):
        """Load configuration from environment or config file"""
        logger.info(f"Fish Audio TTS: Loading configuration, plugin_config: {self.plugin_config is not None}")
        
        # Load API key
        self.api_key = os.getenv("FISH_AUDIO_API_KEY")
        if not self.api_key:
            logger.warning("Fish Audio TTS: FISH_AUDIO_API_KEY not found in environment")
        else:
            logger.info("Fish Audio TTS: API key loaded from environment")
            
        # Load model ID
        self.model_id = os.getenv("FISH_AUDIO_MODEL_ID")
        if not self.model_id:
            logger.warning("Fish Audio TTS: FISH_AUDIO_MODEL_ID not found in environment")
        else:
            logger.info("Fish Audio TTS: Model ID loaded from environment")
            
        # Load proxy configuration - environment variables take precedence
        self.proxy_url = os.getenv("FISH_AUDIO_PROXY_URL")
        if self.proxy_url:
            logger.info(f"Fish Audio TTS: Proxy URL loaded from environment: {self.proxy_url}")
        
        # Load configuration from plugin config
        if self.plugin_config:
            logger.info(f"Fish Audio TTS: Plugin config type: {type(self.plugin_config)}")
            logger.info(f"Fish Audio TTS: Plugin config keys: {list(self.plugin_config.keys()) if isinstance(self.plugin_config, dict) else 'Not a dict'}")
            self.max_retries = self.get_config("max_retries", 3)
            self.timeout = self.get_config("timeout", 30)
            
            # 如果环境变量没有设置代理，尝试从插件配置读取
            if not self.proxy_url:
                proxy_enabled = self.get_config("proxy.enabled", False)
                logger.info(f"Fish Audio TTS: Proxy enabled from config: {proxy_enabled}")
                if proxy_enabled:
                    self.proxy_url = self.get_config("proxy.url", "")
                    logger.info(f"Fish Audio TTS: Proxy URL from config: {self.proxy_url}")
                    if self.proxy_url:
                        logger.info(f"Fish Audio TTS: Using proxy from config: {self.proxy_url}")
                    else:
                        logger.warning("Fish Audio TTS: Proxy enabled in config but no URL provided")
                else:
                    logger.info("Fish Audio TTS: Proxy disabled in config")
            else:
                logger.info(f"Fish Audio TTS: Using proxy from environment (overrides config): {self.proxy_url}")
        else:
            logger.warning("Fish Audio TTS: No plugin config available")
        
        # Final proxy status log
        if self.proxy_url:
            logger.info(f"Fish Audio TTS: Final proxy configuration: {self.proxy_url}")
        else:
            logger.info("Fish Audio TTS: No proxy configured, will use direct connection")
            
    async def _generate_speech(self, text: str) -> Optional[bytes]:
        """Generate speech using Fish Audio API with transparent proxy support via PySocks"""
        logger.info("=" * 60)
        logger.info("Fish Audio TTS: Starting speech generation")
        logger.info("=" * 60)
        
        # Log request details
        logger.info(f"Fish Audio TTS: Request details:")
        logger.info(f"  - API Base URL: {self.api_base_url}")
        logger.info(f"  - Model ID: {self.model_id}")
        logger.info(f"  - Text length: {len(text)} characters")
        logger.info(f"  - Text preview: {text[:100]}{'...' if len(text) > 100 else ''}")
        logger.info(f"  - Proxy: {self.proxy_url or 'None (direct connection)'}")
        logger.info(f"  - Max retries: {self.max_retries}")
        logger.info(f"  - Timeout: 120 seconds")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/msgpack"
        }
        
        logger.info(f"Fish Audio TTS: Request headers:")
        for key, value in headers.items():
            if key == "Authorization":
                logger.info(f"  - {key}: Bearer {self.api_key[:10]}...")
            else:
                logger.info(f"  - {key}: {value}")
        
        # Prepare request data
        request_data = {
            "model_id": self.model_id,
            "text": text,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        
        logger.info(f"Fish Audio TTS: Request data:")
        logger.info(f"  - Model ID: {request_data['model_id']}")
        logger.info(f"  - Text: {request_data['text'][:50]}{'...' if len(request_data['text']) > 50 else ''}")
        logger.info(f"  - Voice settings: {request_data['voice_settings']}")
        
        # Pack data using MessagePack
        packed_data = msgpack.packb(request_data)
        logger.info(f"Fish Audio TTS: Packed data size: {len(packed_data)} bytes")
        
        # 增加超时时间，因为代理可能比较慢
        timeout = httpx.Timeout(120.0)  # 增加到120秒
        
        for attempt in range(self.max_retries):
            logger.info("-" * 40)
            logger.info(f"Fish Audio TTS: Attempt {attempt + 1}/{self.max_retries}")
            logger.info("-" * 40)
            
            start_time = time.time()
            
            try:
                logger.info(f"Fish Audio TTS: Creating HTTP client...")
                logger.info(f"Fish Audio TTS: Client settings:")
                logger.info(f"  - Timeout: 120 seconds")
                logger.info(f"  - SSL verification: Disabled")
                logger.info(f"  - Connection limits: max_keepalive=5, max_connections=10")
                
                # 配置代理
                proxy_config = None
                if self.proxy_url:
                    logger.info(f"Fish Audio TTS: Configuring proxy: {self.proxy_url}")
                    # 根据httpx文档，SOCKS代理需要特殊处理
                    if self.proxy_url.startswith("socks5://"):
                        # 对于SOCKS5代理，需要确保URL格式正确
                        proxy_config = self.proxy_url
                        logger.info(f"Fish Audio TTS: SOCKS5 proxy configuration: {proxy_config}")
                    elif self.proxy_url.startswith("http://") or self.proxy_url.startswith("https://"):
                        # HTTP代理
                        proxy_config = self.proxy_url
                        logger.info(f"Fish Audio TTS: HTTP proxy configuration: {proxy_config}")
                    else:
                        logger.warning(f"Fish Audio TTS: Unsupported proxy protocol: {self.proxy_url}")
                        proxy_config = None
                else:
                    logger.info("Fish Audio TTS: No proxy configured, using direct connection")
                
                async with httpx.AsyncClient(
                    timeout=timeout,
                    verify=False,  # 禁用SSL验证，可能有助于连接
                    limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
                    proxy=proxy_config
                ) as client:
                    logger.info(f"Fish Audio TTS: HTTP client created successfully")
                    logger.info(f"Fish Audio TTS: Sending POST request to {self.api_base_url}/tts")
                    
                    response = await client.post(
                        f"{self.api_base_url}/tts",
                        headers=headers,
                        content=packed_data
                    )
                    
                    elapsed_time = time.time() - start_time
                    logger.info(f"Fish Audio TTS: Request completed in {elapsed_time:.2f} seconds")
                    logger.info(f"Fish Audio TTS: Response status: {response.status_code}")
                    logger.info(f"Fish Audio TTS: Response headers: {dict(response.headers)}")
                    
                    if response.status_code == 200:
                        audio_data = response.content
                        logger.info(f"Fish Audio TTS: ✅ Success! Audio generated successfully")
                        logger.info(f"Fish Audio TTS: Audio data size: {len(audio_data)} bytes")
                        logger.info(f"Fish Audio TTS: Content-Type: {response.headers.get('content-type', 'unknown')}")
                        return audio_data
                    else:
                        error_text = response.text
                        logger.error(f"Fish Audio TTS: ❌ API Error!")
                        logger.error(f"Fish Audio TTS: Status code: {response.status_code}")
                        logger.error(f"Fish Audio TTS: Error response: {error_text}")
                        logger.error(f"Fish Audio TTS: Response headers: {dict(response.headers)}")
                        
            except httpx.TimeoutException as e:
                elapsed_time = time.time() - start_time
                logger.warning(f"Fish Audio TTS: ⏰ Timeout after {elapsed_time:.2f} seconds")
                logger.warning(f"Fish Audio TTS: Timeout details: {e}")
                logger.warning(f"Fish Audio TTS: This might be due to slow proxy or network issues")
            except httpx.ConnectError as e:
                elapsed_time = time.time() - start_time
                logger.error(f"Fish Audio TTS: 🔌 Connection error after {elapsed_time:.2f} seconds")
                logger.error(f"Fish Audio TTS: Connection details: {e}")
                logger.error(f"Fish Audio TTS: This might be a proxy connection issue")
            except httpx.ProxyError as e:
                elapsed_time = time.time() - start_time
                logger.error(f"Fish Audio TTS: 🌐 Proxy error after {elapsed_time:.2f} seconds")
                logger.error(f"Fish Audio TTS: Proxy details: {e}")
            except Exception as e:
                elapsed_time = time.time() - start_time
                logger.error(f"Fish Audio TTS: ❌ Unexpected error after {elapsed_time:.2f} seconds")
                logger.error(f"Fish Audio TTS: Error: {e}")
                logger.error(f"Fish Audio TTS: Error type: {type(e).__name__}")
                
            if attempt < self.max_retries - 1:
                wait_time = 2 ** attempt
                logger.info(f"Fish Audio TTS: Waiting {wait_time} seconds before retry...")
                await asyncio.sleep(wait_time)  # Exponential backoff
            else:
                logger.error(f"Fish Audio TTS: All {self.max_retries} attempts failed")
                
        logger.info("=" * 60)
        logger.info("Fish Audio TTS: Speech generation failed")
        logger.info("=" * 60)
        return None
        
    async def _save_audio(self, audio_data: bytes) -> Path:
        """Save audio data to file and convert to WAV format for napcat compatibility"""
        # Create audio directory if it doesn't exist
        audio_dir = Path("data/audio/fish_audio")
        audio_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        timestamp = int(time.time())
        mp3_filename = f"fish_audio_{timestamp}.mp3"
        wav_filename = f"fish_audio_{timestamp}.wav"
        
        mp3_path = audio_dir / mp3_filename
        wav_path = audio_dir / wav_filename
        
        # Save original MP3 file
        with open(mp3_path, "wb") as f:
            f.write(audio_data)
            
        logger.info(f"Fish Audio TTS: Original MP3 saved to {mp3_path}")
        
        # Convert MP3 to WAV format for napcat compatibility
        try:
            from pydub import AudioSegment
            
            # Load MP3 and convert to WAV
            audio = AudioSegment.from_mp3(mp3_path)
            
            # Export as WAV with napcat-compatible settings
            audio.export(
                wav_path, 
                format="wav",
                parameters=["-ar", "16000", "-ac", "1"]  # 16kHz, mono
            )
            
            logger.info(f"Fish Audio TTS: Converted to WAV format: {wav_path}")
            
            # Clean up MP3 file
            mp3_path.unlink()
            logger.info(f"Fish Audio TTS: Cleaned up MP3 file")
            
            return wav_path
            
        except ImportError:
            logger.warning("Fish Audio TTS: pydub not available, using original MP3 format")
            return mp3_path
        except Exception as e:
            logger.error(f"Fish Audio TTS: Audio conversion failed: {e}")
            logger.info(f"Fish Audio TTS: Using original MP3 format")
            return mp3_path

    def _process_text_for_tts(self, text: str) -> str:
        """
        处理文本使其更适合TTS使用
        - 移除不必要的特殊字符和表情符号
        - 修正标点符号以提高语音质量
        - 优化文本结构使语音更流畅
        """
        import re

        # 移除多余的标点符号
        processed_text = re.sub(r"([!?,.;:。！？，、；：])\1+", r"\1", text)

        # 确保句子结尾有合适的标点
        if not any(processed_text.endswith(end) for end in [".", "?", "!", "。", "！", "？"]):
            processed_text = processed_text + "。"

        return processed_text


class FishAudioCommand(BaseCommand):
    """Fish Audio TTS Command
    
    手动触发Fish Audio TTS功能
    """

    # 命令基本信息
    command_name = "fish_audio_tts"
    command_description = "手动触发Fish Audio TTS语音合成"
    command_pattern = r"^/fish_audio\s+(.+)$"
    intercept_message = True

    # 命令参数定义
    command_parameters = {
        "text": "需要转换为语音的文本内容"
    }

    async def execute(self) -> Tuple[bool, str]:
        """Execute the Fish Audio TTS command"""
        try:
            # Get the text from command
            text = self.command_data.get("text", "")
            
            if not text:
                await self.send_text("❌ 请提供要转换的文本内容\n用法: /fish_audio <文本内容>")
                return False, "未提供文本内容"

            # Create action instance and execute
            action = FishAudioAction(
                action_data={"text": text},
                reasoning="",
                cycle_timers={},
                thinking_id="",
                chat_stream=None,
                log_prefix="",
                shutting_down=False,
                plugin_config=None
            )
            
            # Load configuration
            await action._load_config()
            
            if not action.api_key or not action.model_id:
                await self.send_text("❌ Fish Audio TTS未正确配置，请检查API密钥和模型ID")
                return False, "配置错误"
            
            # Generate speech
            audio_data = await action._generate_speech(text)
            
            if audio_data:
                # Save audio file
                audio_path = await action._save_audio(audio_data)
                
                # Send audio message
                await self.send_custom(message_type="audio", content="", audio_path=str(audio_path))
                
                await self.send_text(f"✅ 语音生成成功！文本: {text[:50]}...")
                return True, f"Fish Audio TTS命令执行成功: {text[:50]}..."
            else:
                await self.send_text("❌ 语音生成失败，请检查网络连接和API配置")
                return False, "语音生成失败"
                
        except Exception as e:
            logger.error(f"Fish Audio TTS命令执行错误: {e}")
            await self.send_text(f"❌ 命令执行出错: {e}")
            return False, f"命令执行出错: {e}"


@register_plugin
class FishAudioTTSPlugin(BasePlugin):
    """Fish Audio TTS Plugin
    
    A plugin that provides text-to-speech functionality using Fish Audio API.
    Supports LLM-based triggering and proxy access for regions where Fish Audio is not directly accessible.
    """

    # 插件基本信息（必须填写）
    plugin_name = "fish_audio_tts_plugin"  # 内部标识符
    plugin_description = "Fish Audio TTS插件，支持LLM智能判断和代理访问"
    plugin_version = "1.0.0"
    plugin_author = "MaiBot Community"
    enable_plugin = True  # 启用插件
    config_file_name = "config.toml"  # 配置文件名

    # 配置节描述
    config_section_descriptions = {
        "plugin": "插件基本信息配置",
        "components": "组件启用控制",
        "fish_audio": "Fish Audio API配置",
        "proxy": "代理配置",
        "logging": "日志记录相关配置",
    }

    # 配置Schema定义
    config_schema = {
        "plugin": {
            "enabled": ConfigField(type=bool, default=True, description="是否启用插件")
        },
        "components": {
            "enable_fish_audio_tts": ConfigField(type=bool, default=True, description="是否启用Fish Audio TTS Action"),
            "enable_fish_audio_command": ConfigField(type=bool, default=True, description="是否启用Fish Audio TTS Command")
        },
        "fish_audio": {
            "max_retries": ConfigField(type=int, default=3, description="API调用最大重试次数"),
            "timeout": ConfigField(type=int, default=30, description="API调用超时时间（秒）"),
            "random_activation_probability": ConfigField(type=float, default=0.15, description="Normal模式下随机触发概率（0.0-1.0）", example=0.15),
            "voice_settings": {
                "stability": ConfigField(type=float, default=0.5, description="语音稳定性 (0.0-1.0)"),
                "similarity_boost": ConfigField(type=float, default=0.75, description="相似度提升 (0.0-1.0)"),
            }
        },
        "proxy": {
            "enabled": ConfigField(type=bool, default=False, description="是否启用代理"),
            "url": ConfigField(type=str, default="", description="代理URL"),
        },
        "logging": {
            "level": ConfigField(
                type=str, default="INFO", description="日志记录级别", choices=["DEBUG", "INFO", "WARNING", "ERROR"]
            ),
            "prefix": ConfigField(type=str, default="[Fish Audio TTS]", description="日志记录前缀"),
        },
    }

    def get_plugin_components(self) -> List[Tuple[ComponentInfo, Type]]:
        """返回插件包含的组件列表"""

        # 从配置获取组件启用状态
        enable_fish_audio_tts = self.get_config("components.enable_fish_audio_tts", True)
        enable_fish_audio_command = self.get_config("components.enable_fish_audio_command", True)
        
        # 动态设置随机激活概率
        if enable_fish_audio_tts:
            random_probability = self.get_config("fish_audio.random_activation_probability", 0.15)
            FishAudioAction.random_activation_probability = random_probability
        
        components = []
        
        if enable_fish_audio_tts:
            components.append((FishAudioAction.get_action_info(), FishAudioAction))
            
        if enable_fish_audio_command:
            components.append((FishAudioCommand.get_command_info(), FishAudioCommand))

        return components 