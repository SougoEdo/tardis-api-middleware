from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_token: Optional[str] = None  # Simple API token for authentication
    
    # Tardis API
    tardis_api_key: str
    
    # Telegram Bot
    telegram_bot_token: str
    telegram_chat_id: str  # Can be a group/channel ID
    
    # Database
    database_url: str = "sqlite+aiosqlite:///./downloads.db"
    
    # Download Configuration
    default_output_path: str = "./datasets"
    
    # Allowed users (comma-separated list)
    allowed_users: str = ""  # e.g., "intern_username,another_user"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    def is_user_allowed(self, username: str) -> bool:
        """Check if a user is allowed to make requests."""
        if not self.allowed_users:
            return True  # If not configured, allow all
        allowed = [u.strip() for u in self.allowed_users.split(",")]
        return username in allowed


settings = Settings()