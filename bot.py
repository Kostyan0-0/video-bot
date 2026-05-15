import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

TOKEN = "8919314767:AAG979JvgvUXyv4NOlJbgPiQsYk5qtGZ-hE"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Отправь мне ссылку на видео - я скачаю его специально для тебя! Вот команды:\n\n"
        "/audio — скачать аудио (mp3)\n"
        "/video — скачать видео\n\n"
        "Просто напиши команду и отправь ссылку!"
    )

async def video_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['mode'] = 'video'
    await update.message.reply_text("🎬 Режим видео включён! Отправь ссылку.")
    await context.bot.set_my_commands([
        ("start", "🚀 Запустить бота"),
        ("audio", "🎵 Скачать аудио"),
        ("video", "🎬 Скачать видео ✅"),
    ])

async def audio_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['mode'] = 'audio'
    await update.message.reply_text("🎵 Режим аудио включён! Отправь ссылку.")
    await context.bot.set_my_commands([
        ("start", "🚀 Запустить бота"),
        ("audio", "🎵 Скачать аудио ✅"),
        ("video", "🎬 Скачать видео"),
    ])

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    mode = context.user_data.get('mode', 'video')

    if not url.startswith("http://") and not url.startswith("https://"):
        await update.message.reply_text("❌ Некорректная ссылка. Отправь ссылку начинающуюся с https://")
        return

    waiting_msg = await update.message.reply_text(
        "⏳ Скачиваю видео, подождите..." if mode == 'video' else "⏳ Скачиваю аудио, подождите..."
    )

    try:
        if mode == 'audio':
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': 'audio.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
        else:
            ydl_opts = {
                'format': 'best[filesize<45M]/best',
                'outtmpl': 'video.%(ext)s',
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if mode == 'audio':
                filename = os.path.splitext(filename)[0] + '.mp3'

        await waiting_msg.delete()

        if mode == 'audio':
            await update.message.reply_audio(audio=open(filename, 'rb'))
        else:
            await update.message.reply_video(video=open(filename, 'rb'))

        os.remove(filename)

    except yt_dlp.utils.DownloadError:
        await waiting_msg.delete()
        await update.message.reply_text("❌ Не удалось скачать. Проверь ссылку и попробуй ещё раз.")
    except Exception:
        await waiting_msg.delete()
        await update.message.reply_text("❌ Что-то пошло не так. Попробуй другую ссылку.")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("video", video_cmd))
app.add_handler(CommandHandler("audio", audio_cmd))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
app.run_polling()