import asyncio
import logging
import re
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message

# Вставь свой Telegram API-токен от @BotFather
TOKEN = "7807151013:AAEillHt3Z2k7aL-ZoDfF21Ukf0z1Ve6xTM"

# Создаём бота и диспетчер
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Регулярка для поиска ссылок на TikTok
TIKTOK_REGEX = r"(https?://(?:www\.|vm\.)?tiktok\.com/[^\s]+)"

# Функция для скачивания видео с TikTok через API (используем сторонний сервис)
def download_tiktok_video(url):
    api_url = "https://www.tikwm.com/api/"
    params = {"url": url, "hd": 1}
    
    response = requests.get(api_url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        return data.get("data", {}).get("play", None)
    
    return None


# Обработчик сообщений с TikTok-ссылками
@dp.message(lambda message: re.search(TIKTOK_REGEX, message.text))
async def handle_tiktok_link(message: Message):
    match = re.search(TIKTOK_REGEX, message.text)
    if match:
        tiktok_url = match.group(1)

        video_url = download_tiktok_video(tiktok_url)
        if video_url:
            await message.reply_video(video_url, caption="🎥")
        else:
            await message.reply("❌ Не удалось скачать видео.")

# Основная асинхронная функция запуска бота
async def main():
    logging.basicConfig(level=logging.INFO)
    print("Запускаю бота...")
    await dp.start_polling(bot)

# Запуск бота
if __name__ == "__main__":
    asyncio.run(main())
