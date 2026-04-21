import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from yt_dlp import YoutubeDL

# Твій API токен
TOKEN = "8710992589:AAFSVZtIy-wkgkhJIsh5X75JrLVjcfJhpL4"

# Налаштування логування (корисно для відстеження помилок при скалінгу)
logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Налаштування yt-dlp для завантаження
def get_ydl_options(file_path):
    return {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': file_path,
        'merge_output_format': 'mp4',
        'noplaylist': True,
        'quiet': True,
        'max_filesize': 50 * 1024 * 1024, # 50MB ліміт Telegram
    }

async def download_media(url: str, user_id: int):
    loop = asyncio.get_event_loop()
    file_id = f"{user_id}_{int(asyncio.get_event_loop().time())}"
    file_path = f"downloads/{file_id}.mp4"
    
    ydl_opts = get_ydl_options(file_path)
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            # Завантажуємо в окремому потоці, щоб не блокувати інших користувачів
            await loop.run_in_executor(None, lambda: ydl.download([url]))
        return file_path
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise e

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привіт! Я допоможу скачати відео.\n\n"
        "Просто надішли посилання з:\n"
        "• YouTube 📺\n"
        "• TikTok 🎵\n"
        "• Instagram 📸\n"
        "• Pinterest 📌"
    )

@dp.message(F.text.regexp(r'(https?://[^\s]+)'))
async def handle_link(message: types.Message):
    url = message.text
    status_msg = await message.answer("🔍 Починаю завантаження...")
    
    try:
        # Створюємо папку, якщо її немає
        if not os.path.exists('downloads'):
            os.makedirs('downloads')

        file_path = await download_media(url, message.from_user.id)
        
        if os.path.exists(file_path):
            video = types.FSInputFile(file_path)
            await message.answer_video(video, caption="Ваше відео готове! ✅")
            await status_msg.delete()
            os.remove(file_path) # Очищення місця
        else:
            await status_msg.edit_text("❌ Помилка: Файл не знайдено.")
            
    except Exception as e:
        logging.error(f"Error downloading: {e}")
        await status_msg.edit_text("❌ Не вдалося скачати відео. Можливо, воно занадто велике (>50MB) або доступ обмежений.")

async def main():
    print("Бот запущений...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот вимкнений")
