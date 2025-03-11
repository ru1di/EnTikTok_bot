import asyncio
import logging
import re
import requests
import yt_dlp
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, FSInputFile

TOKEN = "7807151013:AAEillHt3Z2k7aL-ZoDfF21Ukf0z1Ve6xTM"

bot = Bot(token=TOKEN)
dp = Dispatcher()

TIKTOK_REGEX = r"(https?://(?:www\.|vm\.)?tiktok\.com/[^\s]+)"
INSTAGRAM_REGEX = r"(https?://(?:www\.)?instagram\.com/(reel|p)/[^\s]+)"
YOUTUBE_REGEX = r"(https?://(?:www\.|m\.)?youtube\.com/(watch\?v=|shorts/)[^\s]+|https?://youtu\.be/[^\s]+)"

def download_tiktok_video(url):
    api_url = "https://www.tikwm.com/api/"
    params = {"url": url, "hd": 1}
    response = requests.get(api_url, params=params)

    if response.status_code == 200:
        data = response.json()
        return data.get("data", {}).get("play", None)

    return None

def download_video_yt_dlp(url):
    downloads_folder = "downloads"
    if not os.path.exists(downloads_folder):
        os.makedirs(downloads_folder)

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'merge_output_format': 'mp4',
        'outtmpl': f'{downloads_folder}/%(title)s.%(ext)s'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_name = ydl.prepare_filename(info).replace('.webm', '.mp4').replace('.mkv', '.mp4')

        if os.path.exists(file_name):
            return file_name
        else:
            print("Ошибка: Файл не был скачан!")
            return None

    except Exception as e:
        print(f"Ошибка при скачивании видео: {e}")
        return None

@dp.message(lambda message: re.search(TIKTOK_REGEX, message.text) or re.search(INSTAGRAM_REGEX, message.text) or re.search(YOUTUBE_REGEX, message.text))
async def handle_video_link(message: Message):
    text = message.text
    video_url = None
    video_file = None
    source = "Неизвестный источник"

    if re.search(TIKTOK_REGEX, text):
        video_url = download_tiktok_video(text)
        source = "TikTok"
    elif re.search(INSTAGRAM_REGEX, text):
        video_file = download_video_yt_dlp(text)
        source = "Instagram"
    elif re.search(YOUTUBE_REGEX, text):
        video_file = download_video_yt_dlp(text)
        source = "YouTube"

    if video_url:
        await message.reply_video(video_url, caption=f"🎥 Ваше видео из {source}!")
    
    elif video_file:
        if os.path.exists(video_file):
            file_size_mb = os.path.getsize(video_file) / (1024 * 1024)  # Размер в MB

            # ❌ Если файл больше 50MB, не скачиваем и не отправляем
            if file_size_mb > 50:
                await message.reply(f"❗ Файл слишком большой ({file_size_mb:.2f} MB)")
                os.remove(video_file)  # ✅ Удаляем файл, если он уже скачался
                return

            video = FSInputFile(video_file)
            await message.reply_video(video, caption=f"🎥 Ваше видео из {source}!")  # Отправляем как видео

            # ✅ Удаляем файл после отправки
            os.remove(video_file)
            print(f"🗑️ Файл {video_file} удалён.")
        else:
            await message.reply("❌ Ошибка: видео не скачалось. Попробуйте другую ссылку.")
    else:
        await message.reply(f"❌ Не удалось скачать видео из {source}.")

async def main():
    logging.basicConfig(level=logging.INFO)
    print("🚀 Запуск бота...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
