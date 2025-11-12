from telegram import Bot
from telegram.error import TelegramError
from loguru import logger
from typing import Optional

from app.config import settings


class TelegramNotifier:
    """Telegram notification handler."""
    
    def __init__(self):
        self.bot = Bot(token=settings.telegram_bot_token)
        self.chat_id = settings.telegram_chat_id
    
    async def send_message(self, message: str) -> bool:
        """Send a message to the configured Telegram chat."""
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode="HTML"
            )
            logger.info(f"Telegram notification sent: {message[:50]}...")
            return True
        except TelegramError as e:
            logger.error(f"Failed to send Telegram notification: {e}")
            return False
    
    async def notify_job_started(
        self,
        job_id: int,
        exchange: str,
        symbols: list,
        start_date: str,
        end_date: str,
        created_by: str
    ):
        """Notify when a download job starts."""
        symbols_str = ", ".join(symbols[:3])
        if len(symbols) > 3:
            symbols_str += f" (+{len(symbols) - 3} more)"
        
        message = (
            f"🚀 <b>Download Started</b>\n\n"
            f"<b>Job ID:</b> {job_id}\n"
            f"<b>Exchange:</b> {exchange}\n"
            f"<b>Symbols:</b> {symbols_str}\n"
            f"<b>Date Range:</b> {start_date} to {end_date}\n"
            f"<b>Requested by:</b> {created_by}"
        )
        await self.send_message(message)
    
    async def notify_job_completed(
        self,
        job_id: int,
        exchange: str,
        symbols: list,
        duration_minutes: Optional[float] = None
    ):
        """Notify when a download job completes successfully."""
        symbols_str = ", ".join(symbols[:3])
        if len(symbols) > 3:
            symbols_str += f" (+{len(symbols) - 3} more)"
        
        duration_str = ""
        if duration_minutes:
            duration_str = f"\n<b>Duration:</b> {duration_minutes:.1f} minutes"
        
        message = (
            f"✅ <b>Download Completed</b>\n\n"
            f"<b>Job ID:</b> {job_id}\n"
            f"<b>Exchange:</b> {exchange}\n"
            f"<b>Symbols:</b> {symbols_str}"
            f"{duration_str}"
        )
        await self.send_message(message)
    
    async def notify_job_failed(
        self,
        job_id: int,
        exchange: str,
        symbols: list,
        error: str
    ):
        """Notify when a download job fails."""
        symbols_str = ", ".join(symbols[:3])
        if len(symbols) > 3:
            symbols_str += f" (+{len(symbols) - 3} more)"
        
        # Truncate error message if too long
        error_msg = error[:200] + "..." if len(error) > 200 else error
        
        message = (
            f"❌ <b>Download Failed</b>\n\n"
            f"<b>Job ID:</b> {job_id}\n"
            f"<b>Exchange:</b> {exchange}\n"
            f"<b>Symbols:</b> {symbols_str}\n"
            f"<b>Error:</b> {error_msg}"
        )
        await self.send_message(message)


# Global notifier instance
notifier = TelegramNotifier()