import os
from dataclasses import dataclass
from typing import List

@dataclass
class TwitterAccount:
    bearer_token: str
    api_key: str
    api_secret: str
    access_token: str
    access_token_secret: str
    daily_tweet_limit: int = 500
    daily_view_limit: int = 100
    remaining_tweets: int = 500
    remaining_views: int = 100

@dataclass
class Config:
    accounts: List[TwitterAccount]
    current_account_index: int = 0
    bot_name: str
    bot_personality: str
    bot_language: str
    check_interval_hours: int = 3

    @classmethod
    def from_env(cls, env_file='.env'):
        accounts = []
        for i in range(1, 3):  # 2 hesap için
            prefix = f"TWITTER{i}_"
            account = TwitterAccount(
                bearer_token=os.getenv(f'{prefix}BEARER_TOKEN'),
                api_key=os.getenv(f'{prefix}API_KEY'),
                api_secret=os.getenv(f'{prefix}API_SECRET'),
                access_token=os.getenv(f'{prefix}ACCESS_TOKEN'),
                access_token_secret=os.getenv(f'{prefix}ACCESS_TOKEN_SECRET')
            )
            accounts.append(account)

        return cls(
            accounts=accounts,
            bot_name=os.getenv('BOT_NAME'),
            bot_personality=os.getenv('BOT_PERSONALITY'),
            bot_language=os.getenv('BOT_LANGUAGE')
        )

    def get_current_account(self):
        """Get current account for viewing or posting"""
        if self.current_account_index == 0:
            # Birinci hesap için tweet limiti dolmuşsa, sadece görüntüleme için ikinci hesaba geç
            if self.accounts[0].remaining_views <= 0:
                self.current_account_index = 1
                return self.accounts[1]
            return self.accounts[0]
        return self.accounts[1]  # İkinci hesap sadece görüntüleme için

    def get_posting_account(self):
        """Her zaman birinci hesabı döndür"""
        return self.accounts[0]

    def switch_account(self):
        """Sadece görüntüleme için hesap değiştir"""
        if self.current_account_index == 0 and self.accounts[0].remaining_views <= 0:
            self.current_account_index = 1
            return self.accounts[1]
        return self.accounts[0] 