#!/usr/bin/env python3
"""Fish Audio TTS Plugin Test Script

This script tests the Fish Audio TTS plugin functionality.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.plugins.fish_audio_tts.actions.fish_audio_action import FishAudioAction
from src.chat.message_receive.message import MaimMessage


async def test_fish_audio_action():
    """Test the Fish Audio Action"""
    print("🧪 Testing Fish Audio TTS Plugin...")
    
    # Create a test action
    action = FishAudioAction()
    
    # Create a test message
    test_message = MaimMessage(
        content="Hello, this is a test message for Fish Audio TTS!",
        sender_id="test_user_123",
        receiver_id="test_group_456",
        message_type="text",
        bot_id="test_bot_789"
    )
    
    print(f"📝 Test message: {test_message.content}")
    print(f"🎲 Trigger probability: {action.trigger_probability}")
    
    # Test configuration loading
    print("\n⚙️ Loading configuration...")
    await action._load_config()
    
    print(f"🔑 API Key configured: {'Yes' if action.api_key else 'No'}")
    print(f"🎯 Model ID configured: {'Yes' if action.model_id else 'No'}")
    print(f"🌐 Proxy configured: {'Yes' if action.proxy_url else 'No'}")
    
    # Test can_execute
    print("\n🔍 Testing can_execute...")
    can_execute = await action.can_execute(test_message)
    print(f"Can execute: {can_execute}")
    
    if can_execute:
        print("\n🚀 Testing execute...")
        result = await action.execute(test_message)
        print(f"Execute result: {result}")
    else:
        print("❌ Cannot execute - check configuration")
    
    print("\n✅ Test completed!")


async def test_api_connection():
    """Test API connection"""
    print("\n🌐 Testing API connection...")
    
    action = FishAudioAction()
    await action._load_config()
    
    if not action.api_key or not action.model_id:
        print("❌ Missing API key or model ID")
        return
    
    # Test with a simple text
    test_text = "Hello, this is a connection test."
    
    try:
        audio_data = await action._generate_speech(test_text)
        if audio_data:
            print(f"✅ API connection successful! Generated {len(audio_data)} bytes")
        else:
            print("❌ API connection failed - no audio data received")
    except Exception as e:
        print(f"❌ API connection error: {e}")


def check_dependencies():
    """Check if required dependencies are installed"""
    print("📦 Checking dependencies...")
    
    required_packages = ['aiohttp', 'msgpack']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} - OK")
        except ImportError:
            print(f"❌ {package} - Missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install " + " ".join(missing_packages))
        return False
    
    return True


def check_environment():
    """Check environment variables"""
    print("\n🔧 Checking environment variables...")
    
    required_vars = ['FISH_AUDIO_API_KEY', 'FISH_AUDIO_MODEL_ID']
    optional_vars = ['FISH_AUDIO_PROXY_URL']
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var} - Configured")
        else:
            print(f"❌ {var} - Not configured")
    
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var} - Configured: {value}")
        else:
            print(f"ℹ️  {var} - Not configured (optional)")


async def main():
    """Main test function"""
    print("🎵 Fish Audio TTS Plugin Test Suite")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Check environment
    check_environment()
    
    # Test action
    await test_fish_audio_action()
    
    # Test API connection
    await test_api_connection()
    
    print("\n" + "=" * 50)
    print("🎉 Test suite completed!")


if __name__ == "__main__":
    asyncio.run(main()) 