from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from pytube import YouTube
import os
import logging

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Initialize bot with token
TOKEN = '7426607108:AAFDXpucOlUyMGwpyXkGlP4NKZvoawx17Lc'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Welcome to the bot. Please send the video link you want to download.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    video_url = update.message.text
    context.user_data['video_url'] = video_url

    yt = YouTube(video_url)
    video_title = yt.title
    video_link = yt.watch_url

    video_options = [
        [InlineKeyboardButton("240p", callback_data='240p'),
         InlineKeyboardButton("360p", callback_data='360p')],
        [InlineKeyboardButton("480p", callback_data='480p'),
         InlineKeyboardButton("720p", callback_data='720p')],
        [InlineKeyboardButton("1080p", callback_data='1080p'),
         InlineKeyboardButton("1440p", callback_data='1440p')],
        [InlineKeyboardButton("2160p", callback_data='2160p'),
         InlineKeyboardButton("4320p", callback_data='4320p')]
    ]

    audio_options = [
        [InlineKeyboardButton("MP3 8-bit", callback_data='8-bit'),
         InlineKeyboardButton("MP3 16-bit", callback_data='16-bit')],
        [InlineKeyboardButton("MP3 24-bit", callback_data='24-bit'),
         InlineKeyboardButton("MP3 32-bit", callback_data='32-bit')]
    ]

    video_markup = InlineKeyboardMarkup(video_options)
    audio_markup = InlineKeyboardMarkup(audio_options)

    
    await update.message.reply_text('Please choose the video resolution:', reply_markup=video_markup)
    await update.message.reply_text('Please choose the audio resolution:', reply_markup=audio_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    resolution_choice = query.data
    video_url = context.user_data['video_url']

    yt = YouTube(video_url)

    # Send a message indicating the download has started
    loading_message = await query.message.reply_text("Downloading...")

    try:
        if resolution_choice in ['240p', '360p', '480p', '720p', '1080p', '1440p', '2160p', '4320p']:
            stream = yt.streams.filter(res=resolution_choice, progressive=True, file_extension='mp4').first()
            if stream:
                file_path = stream.download()
                with open(file_path, 'rb') as video:
                    await query.message.reply_video(video=video, caption=f"Downloaded: {yt.title}")
                os.remove(file_path)
            else:
                await query.message.reply_text("Video stream not available for the selected resolution.")
        elif resolution_choice in ['8-bit', '16-bit', '24-bit', '32-bit']:
            stream = yt.streams.filter(only_audio=True, abr=resolution_choice).first()
            if stream:
                file_path = stream.download()
                base, ext = os.path.splitext(file_path)
                new_file = base + '.mp3'
                os.rename(file_path, new_file)
                with open(new_file, 'rb') as audio:
                    await query.message.reply_audio(audio=audio, caption=f"Downloaded: {yt.title}")
                os.remove(new_file)
            else:
                await query.message.reply_text("Audio stream not available for the selected resolution.")
    except Exception as e:
        await query.message.reply_text(f"An error occurred: {str(e)}")
    finally:
        # Delete the loading message
        await loading_message.delete()

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button))

    # Print message when bot starts
    logger.info("Bot started...")

    application.run_polling()

if __name__ == '__main__':
    main()
