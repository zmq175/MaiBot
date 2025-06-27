import time

class WillingInfo:
    def __init__(self):
        self.message: str = ""
        self.user_id: str = ""
        self.group_id: str = ""
        self.is_mentioned: bool = False
        self.is_at: bool = False
        self.current_willing: float = 0.0
        self.interested_rate: float = 0.0
        self.last_reply_time: float = 0.0
        self.message_count: int = 0
        self.emoji_count: int = 0

    def update(self, message: str, user_id: str, group_id: str):
        """更新意愿信息"""
        self.message = message
        self.user_id = user_id
        self.group_id = group_id
        self.is_mentioned = "@bot" in message
        self.is_at = "[CQ:at,qq=bot]" in message
        self.emoji_count = message.count("[CQ:face") + message.count("[CQ:emoji")
        self.message_count += 1
        self.last_reply_time = time.time()

    def reset(self):
        """重置意愿信息"""
        self.__init__() 