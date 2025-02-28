import os
import re

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

from configs.config import Settings
from downloader import FacebookDownloader, TiktokDownloader, YoutubeDownloader
from logger import logger


# Function to detect video URLs
def contains_video_url(message):
    optimized_pattern = re.compile(r"https?://(?:www\.)?(?:(?:youtube\.com|youtu\.be|tiktok\.com|facebook\.com)/\S+)")
    return optimized_pattern.findall(message)


def determine_downloader(url: str):
    if "youtube.com" in url or "youtu.be" in url:
        return YoutubeDownloader(url)
    elif "tiktok.com" in url:
        return TiktokDownloader(url)
    elif "facebook.com" in url:
        return FacebookDownloader(url)


# Message handler for video URLs
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    text = message.text
    chat_id = message.chat_id

    video_urls = contains_video_url(text)
    if not video_urls:
        return

    for url in video_urls:
        logger.info(f"Processing URL: {url} from user {update.effective_user.id}")

        # Download the video
        downloader = determine_downloader(url)
        video_info = downloader.extract_info()
        file_path = downloader.download()

        # Send video back if downloaded successfully
        if file_path and os.path.exists(file_path):
            # Check file size (Telegram limit is 50MB for bots by default)
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # Size in MB
            if file_size > 50:
                await message.reply_text(f"Video is too large ({file_size:.2f} MB). Telegram limit is 50 MB.")
                logger.warning(f"Video {file_path} too large: {file_size:.2f} MB")
                os.remove(file_path)
                continue

            # Create inline button with the original URL
            keyboard = [[InlineKeyboardButton("Original Link", url=video_info.get("original_url"))]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            with open(file_path, "rb") as video:
                await context.bot.send_video(
                    chat_id=chat_id,
                    video=video,
                    reply_to_message_id=message.message_id,
                    caption=video_info.get("title"),
                    reply_markup=reply_markup,
                )
            logger.info(f"Sent video {file_path} to chat {chat_id}")
            os.remove(file_path)
        else:
            await message.reply_text(f"Failed to download video from {url}")
            logger.error(f"Failed to send video from {url} to chat {chat_id}")


# Main function to run the bot
def main():
    config = Settings()
    # Create the Application
    application = Application.builder().token(config.token).build()

    # Add handlers
    application.add_handler(MessageHandler(filters.TEXT & filters.USER & ~filters.COMMAND, handle_message))

    # Start the bot
    logger.info("Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
