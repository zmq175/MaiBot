#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试TTS配置加载
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config.config import global_config

def test_tts_config():
    """测试TTS配置加载"""
    print("=== 测试TTS配置加载 ===")
    
    # 检查tts_adapter配置
    tts_config = getattr(global_config, 'tts_adapter', None)
    print(f"tts_adapter配置: {tts_config}")
    
    if tts_config:
        enable = getattr(tts_config, 'enable', False)
        host = getattr(tts_config, 'host', '127.0.0.1')
        port = getattr(tts_config, 'port', 8070)
        
        print(f"enable: {enable}")
        print(f"host: {host}")
        print(f"port: {port}")
        
        if enable:
            print("✅ TTS适配器配置正确加载")
        else:
            print("❌ TTS适配器未启用")
    else:
        print("❌ 未找到tts_adapter配置")
    
    # 检查全局配置的所有属性
    print("\n=== 全局配置属性 ===")
    for attr in dir(global_config):
        if not attr.startswith('_'):
            print(f"{attr}: {getattr(global_config, attr)}")

if __name__ == "__main__":
    test_tts_config() 