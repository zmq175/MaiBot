#!/usr/bin/env python3
"""
TTS功能测试脚本
用于测试普通模式和auto模式下的TTS功能
"""

import asyncio
import random
from src.config.config import global_config

def test_tts_config():
    """测试TTS配置是否正确加载"""
    print("=== TTS配置测试 ===")
    print(f"聊天模式: {global_config.chat.chat_mode}")
    print(f"auto模式TTS概率: {global_config.chat.auto_tts_probability}")
    print(f"普通模式TTS概率: {global_config.chat.normal_tts_probability}")
    
    # 测试概率计算
    print("\n=== 概率测试 ===")
    for i in range(10):
        if global_config.chat.chat_mode == "auto":
            should_send = random.random() < global_config.chat.auto_tts_probability
            print(f"测试 {i+1}: auto模式, 概率={global_config.chat.auto_tts_probability}, 是否发送TTS: {should_send}")
        elif global_config.chat.chat_mode == "normal":
            should_send = random.random() < global_config.chat.normal_tts_probability
            print(f"测试 {i+1}: 普通模式, 概率={global_config.chat.normal_tts_probability}, 是否发送TTS: {should_send}")

def test_tts_probability_logic():
    """测试TTS概率逻辑"""
    print("\n=== TTS概率逻辑测试 ===")
    
    # 模拟不同配置
    test_configs = [
        ("auto", 0.3, 0.1),
        ("normal", 0.3, 0.1),
        ("auto", 0.0, 0.1),
        ("normal", 0.3, 0.0),
    ]
    
    for mode, auto_prob, normal_prob in test_configs:
        print(f"\n测试配置: 模式={mode}, auto概率={auto_prob}, normal概率={normal_prob}")
        
        # 模拟概率判断逻辑
        if mode == "auto":
            current_prob = auto_prob
        elif mode == "normal":
            current_prob = normal_prob
        else:
            current_prob = 0.0
            
        should_send = random.random() < current_prob
        print(f"当前概率: {current_prob}, 是否发送TTS: {should_send}")

if __name__ == "__main__":
    print("开始TTS功能测试...")
    test_tts_config()
    test_tts_probability_logic()
    print("\n测试完成！") 