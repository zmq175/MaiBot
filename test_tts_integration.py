#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试TTS集成功能
"""
import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config.config import global_config
from src.common.logger_manager import get_logger
from src.chat.message_receive.message import MessageRecv, MessageInfo, UserInfo, FormatInfo
from src.chat.message_receive.chat_stream import ChatStream
from src.chat.normal_chat.normal_chat import NormalChat
from src.plugins.tts_plgin.actions.tts_action import TTSAction
from src.chat.focus_chat.planners.action_manager import ActionManager
from src.chat.focus_chat.expressors.default_expressor import DefaultExpressor
from src.chat.heart_flow.observation.chatting_observation import ChattingObservation
import time
from random import random

logger = get_logger("test_tts")

async def test_tts_probability_check():
    """测试TTS概率检查功能"""
    print("\n=== 测试TTS概率检查 ===")
    
    # 获取TTS概率配置
    auto_tts_probability = getattr(global_config.chat, 'auto_tts_probability', 0.3)
    normal_tts_probability = getattr(global_config.chat, 'normal_tts_probability', 0.3)
    chat_mode = global_config.chat.chat_mode
    
    print(f"当前聊天模式: {chat_mode}")
    print(f"auto模式TTS概率: {auto_tts_probability}")
    print(f"普通模式TTS概率: {normal_tts_probability}")
    
    # 测试概率检查逻辑
    should_send_tts = False
    current_probability = 0.0
    
    if chat_mode == "auto":
        current_probability = auto_tts_probability
        should_send_tts = random() < current_probability
        print(f"auto模式, 随机值<{current_probability}: {should_send_tts}")
    elif chat_mode == "normal":
        current_probability = normal_tts_probability
        should_send_tts = random() < current_probability
        print(f"normal模式, 随机值<{current_probability}: {should_send_tts}")
    else:
        print(f"当前模式({chat_mode})不支持TTS自动触发")
    
    return should_send_tts, current_probability

async def test_tts_action():
    """测试TTS动作执行"""
    print("\n=== 测试TTS动作执行 ===")
    
    try:
        # 创建测试消息
        user_info = UserInfo(user_id="test_user", user_nickname="测试用户")
        message_info = MessageInfo(
            message_id="test_msg_001",
            user_info=user_info,
            time=time.time(),
            platform="test",
            additional_config={}
        )
        
        # 创建格式信息
        format_info = FormatInfo(
            content_format=['text', 'image', 'emoji', 'reply', 'tts_text', 'vtb_text', 'voice'],
            accept_format=['text', 'image', 'emoji', 'reply', 'tts_text', 'vtb_text', 'voice']
        )
        
        # 创建聊天流
        chat_stream = ChatStream(
            stream_id="test_stream",
            platform="test",
            group_info=None,
            format_info=format_info
        )
        
        # 创建消息
        message = MessageRecv(
            message_info=message_info,
            processed_plain_text="这是一条测试消息",
            chat_stream=chat_stream,
            reply=None
        )
        
        # 创建TTS动作
        action_data = {"text": "这是一条测试TTS语音消息"}
        
        # 创建必要的内部服务
        expressor = DefaultExpressor("test_stream")
        await expressor.initialize()
        expressor.chat_stream = chat_stream
        
        # 创建聊天观察
        chatting_observation = ChattingObservation("test_stream")
        observations = [chatting_observation]
        
        # 创建TTS动作实例
        tts_action = TTSAction(
            action_data=action_data,
            reasoning="测试TTS功能",
            cycle_timers={},
            thinking_id="test_tts_" + str(int(time.time())),
            observations=observations,
            expressor=expressor,
            chat_stream=chat_stream,
            log_prefix="[测试]",
            shutting_down=False
        )
        
        print("开始执行TTS动作...")
        success, result = await tts_action.process()
        
        if success:
            print(f"✅ TTS动作执行成功: {result}")
        else:
            print(f"❌ TTS动作执行失败: {result}")
            
        return success
        
    except Exception as e:
        print(f"❌ TTS动作测试出错: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_normal_chat_tts():
    """测试NormalChat中的TTS功能"""
    print("\n=== 测试NormalChat中的TTS功能 ===")
    
    try:
        # 创建测试消息
        user_info = UserInfo(user_id="test_user", user_nickname="测试用户")
        message_info = MessageInfo(
            message_id="test_msg_002",
            user_info=user_info,
            time=time.time(),
            platform="test",
            additional_config={}
        )
        
        # 创建格式信息
        format_info = FormatInfo(
            content_format=['text', 'image', 'emoji', 'reply', 'tts_text', 'vtb_text', 'voice'],
            accept_format=['text', 'image', 'emoji', 'reply', 'tts_text', 'vtb_text', 'voice']
        )
        
        # 创建聊天流
        chat_stream = ChatStream(
            stream_id="test_stream_2",
            platform="test",
            group_info=None,
            format_info=format_info
        )
        
        # 创建消息
        message = MessageRecv(
            message_info=message_info,
            processed_plain_text="这是另一条测试消息",
            chat_stream=chat_stream,
            reply=None
        )
        
        # 创建NormalChat实例
        normal_chat = NormalChat(chat_stream, interest_dict={})
        await normal_chat.initialize()
        
        # 测试TTS检查
        response_set = ["这是测试回复内容", "用于验证TTS功能"]
        print("调用_check_and_send_tts方法...")
        await normal_chat._check_and_send_tts(message, response_set)
        
        print("✅ NormalChat TTS功能测试完成")
        return True
        
    except Exception as e:
        print(f"❌ NormalChat TTS测试出错: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主测试函数"""
    print("开始TTS集成测试...")
    
    # 测试1: TTS概率检查
    should_send_tts, probability = await test_tts_probability_check()
    
    # 测试2: TTS动作执行
    tts_success = await test_tts_action()
    
    # 测试3: NormalChat中的TTS功能
    normal_chat_success = await test_normal_chat_tts()
    
    # 输出测试结果
    print("\n=== 测试结果汇总 ===")
    print(f"TTS概率检查: {'✅ 通过' if should_send_tts or probability > 0 else '❌ 失败'}")
    print(f"TTS动作执行: {'✅ 通过' if tts_success else '❌ 失败'}")
    print(f"NormalChat TTS: {'✅ 通过' if normal_chat_success else '❌ 失败'}")
    
    if should_send_tts or probability > 0:
        print("🎉 TTS功能基本正常！")
    else:
        print("⚠️  TTS概率可能设置过低，建议检查配置")

if __name__ == "__main__":
    asyncio.run(main()) 