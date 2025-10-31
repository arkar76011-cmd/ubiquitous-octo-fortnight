import os
import re
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import yt_dlp
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)


BOT_TOKEN = os.environ.get("BOT_TOKEN")
DEFAULT_SAVE_PATH = "tiktok_videos"
MAX_FILE_SIZE = 50 * 1024 * 1024  


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)



class TikTokDownloader:
    def __init__(self, save_path: str = DEFAULT_SAVE_PATH):
        self.save_path = save_path
        self.create_save_directory()
    
    def create_save_directory(self) -> None:
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
    
    @staticmethod
    def validate_url(url: str) -> bool:
        pattern = r"https?://((?:vm|vt|www)\.)?tiktok\.com/.*"
        return bool(re.match(pattern, url))
    
    @staticmethod
    def progress_hook(d: Dict[str, Any]) -> None:
        if d["status"] == "downloading":
            progress = d.get("_percent_str", "N/A")
            print(f"Downloading: {progress}", end="\r")
        elif d["status"] == "finished":
            print("\nDownload completed")
    
    def get_filename(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"tiktok_{timestamp}.mp4"
    
    def download_video(self, video_url: str) -> Optional[str]:
        if not self.validate_url(video_url):
            return None

        filename = self.get_filename()
        output_path = os.path.join(self.save_path, filename)
        
        ydl_opts = {
            "outtmpl": output_path,
            "format": "best[filesize<50M]",
            "noplaylist": True,
            "quiet": True,
            "progress_hooks": [self.progress_hook],
            "http_headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/91.0.4472.124 Safari/537.36"
            }
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.extract_info(video_url, download=True)
                return output_path
        except Exception as e:
            logger.error(f"Download error: {e}")
            return None



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌟 Welcome to TikTok Downloader Bot!\n"
        "Send me a TikTok URL and I'll download it for you!"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Just send me a TikTok video link and I'll handle the rest!")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return

    url = message.text.strip()
    downloader = TikTokDownloader()

    if not downloader.validate_url(url):
        await message.reply_text("❌ Invalid TikTok URL. Please send a valid link.")
        return

    msg = await message.reply_text("⏳ Downloading your TikTok video...")
    file_path = None

    try:
        file_path = downloader.download_video(url)
        
        if not file_path or not os.path.exists(file_path):
            await msg.edit_text("❌ Failed to download video. Please try again later.")
            return
        
        file_size = os.path.getsize(file_path)
        if file_size > MAX_FILE_SIZE:
            await msg.edit_text("❌ Video is too large for Telegram (max 50MB)")
            os.remove(file_path)
            return
        
        with open(file_path, "rb") as video_file:
            await message.reply_video(
                video=video_file,
                caption="✅ Here's your TikTok video!",
                supports_streaming=True
            )
        await msg.delete()
        
    except Exception as e:
        logger.error(f"Error: {e}")
        await msg.edit_text(f"❌ Error: {str(e)}")
    
    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)



def main():
    application = Application.builder().token(BOT_TOKEN).build()

    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Bot is running...")
    application.run_polling()


if __name__ == "__main__":
    main()
