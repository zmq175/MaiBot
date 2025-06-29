"""Fish Audio TTS Plugin for MaiBot

This plugin provides text-to-speech functionality using Fish Audio API.
Supports proxy access for users in regions where Fish Audio is not directly accessible.
"""

from .actions.fish_audio_action import FishAudioAction

__version__ = "1.0.0"
__author__ = "MaiBot Community"
__description__ = "Fish Audio TTS Plugin with proxy support"

# Register the action
actions = [FishAudioAction] 