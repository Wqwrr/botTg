import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from yt_dlp import YoutubeDL

# Твій вигаданий API токен
TOKEN = "8710992589:AAFSVZtIy-wkgkhJIsh5X75JrLVjcfJhpL4"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Налаштування для yt-dlp
YDL_OPTIONS = {
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'noplaylist': True,
    'max_filesize': 50 * 1024 * 1024,  # Обмеження 50МБ для Telegram
}

async def download_video(url: str):
    loop = asyncio.get_event_loop()
    with YoutubeDL(YDL_OPTIONS) as ydl:
        # Виконуємо завантаження в окремому потоці, щоб не блокувати бот
        info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))
        return ydl.prepare_filename(info)

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("Привіт! Надішли мені посилання на відео з YouTube, TikTok, Instagram або Pinterest, і я спробую його скачати. 📥")

@dp.message(F.text.contains("http"))
async def handle_link(message: types.Message):
    status_msg = await message.answer("Обробляю посилання... ⏳")
    
    try:
        file_path = await download_video(message.text)
        
        video = types.FSInputFile(file_path)
        await message.answer_video(video, caption="Ось твоє відео! ✅")
        await status_msg.delete()
        
        # Видаляємо файл після відправки, щоб не забивати диск
        os.remove(file_path)
        
    except Exception as e:
        await status_msg.edit_text(f"Виникла помилка: {str(e)[:100]}...")

async def main():
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
