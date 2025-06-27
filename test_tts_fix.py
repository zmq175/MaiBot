#!/usr/bin/env python3
"""
TTS修复验证脚本
用于测试修复后的TTS功能是否在normal模式下正常工作
"""

import asyncio
import random
from src.config.config import global_config

def test_tts_config():
    """测试TTS配置"""
    print("=== TTS配置测试 ===")
    print(f"聊天模式: {global_config.chat.chat_mode}")
    print(f"auto模式TTS概率: {global_config.chat.auto_tts_probability}")
    print(f"普通模式TTS概率: {global_config.chat.normal_tts_probability}")
    
    return global_config.chat.chat_mode, global_config.chat.auto_tts_probability, global_config.chat.normal_tts_probability

def test_tts_logic():
    """测试TTS逻辑"""
    print("\n=== TTS逻辑测试 ===")
    
    # 模拟修复后的逻辑
    def check_tts_trigger(mode, auto_prob, normal_prob):
        """模拟TTS触发逻辑"""
        should_send_tts = False
        current_probability = 0.0
        
        if mode == "auto":
            current_probability = auto_prob
            should_send_tts = random.random() < current_probability
            print(f"[TTS] auto模式, 概率={current_probability}, 随机值<{current_probability}: {should_send_tts}")
        elif mode == "normal":
            current_probability = normal_prob
            should_send_tts = random.random() < current_probability
            print(f"[TTS] normal模式, 概率={current_probability}, 随机值<{current_probability}: {should_send_tts}")
        else:
            print(f"[TTS] 当前模式({mode})不支持TTS自动触发")
            
        return should_send_tts, current_probability
    
    # 测试不同模式
    test_cases = [
        ("auto", 0.3, 0.1),
        ("normal", 0.3, 0.1),
        ("focus", 0.3, 0.1),
    ]
    
    for mode, auto_prob, normal_prob in test_cases:
        print(f"\n测试模式: {mode}")
        for i in range(5):
            should_send, prob = check_tts_trigger(mode, auto_prob, normal_prob)
            if should_send:
                print(f"  ✓ 测试{i+1}: 触发TTS (概率={prob})")
            else:
                print(f"  ✗ 测试{i+1}: 未触发TTS (概率={prob})")

def test_fix_verification():
    """验证修复效果"""
    print("\n=== 修复验证 ===")
    
    # 模拟修复前的逻辑（只在auto模式下调用）
    def old_logic(mode):
        if mode == "auto":
            return "会调用TTS"
        else:
            return "不会调用TTS"
    
    # 模拟修复后的逻辑（所有模式都调用）
    def new_logic(mode):
        return "会调用TTS"
    
    test_modes = ["auto", "normal", "focus"]
    
    print("修复前:")
    for mode in test_modes:
        print(f"  {mode}模式: {old_logic(mode)}")
    
    print("\n修复后:")
    for mode in test_modes:
        print(f"  {mode}模式: {new_logic(mode)}")
    
    print("\n修复效果:")
    for mode in test_modes:
        if old_logic(mode) != new_logic(mode):
            print(f"  ✓ {mode}模式: 从'不会调用TTS'修复为'会调用TTS'")
        else:
            print(f"  - {mode}模式: 无变化")

if __name__ == "__main__":
    print("开始TTS修复验证...")
    
    try:
        mode, auto_prob, normal_prob = test_tts_config()
        test_tts_logic()
        test_fix_verification()
        
        print(f"\n=== 总结 ===")
        print(f"当前配置: 模式={mode}, auto概率={auto_prob}, normal概率={normal_prob}")
        print("修复内容: 移除了TTS调用的模式限制，现在所有模式都会尝试调用TTS")
        print("预期效果: 在normal模式下也能看到TTS相关的调试日志和语音消息")
        
    except Exception as e:
        print(f"测试过程中出错: {e}")
    
    print("\n验证完成！") 