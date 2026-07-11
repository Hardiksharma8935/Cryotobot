import asyncio
from fastapi import FastAPI
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from src.config import settings
from contextlib import asynccontextmanager

# Telegram Bot ka reply logic
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello Boss! Jarvis AI is Online. 🚀 Ready for crypto analysis!")

# Background me Telegram bot ko lagatar chalane ka logic
@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.TELEGRAM_BOT_TOKEN != "test_token":
        bot_app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
        bot_app.add_handler(CommandHandler("start", start_command))
        
        await bot_app.initialize()
        await bot_app.start()
        # Polling background me chalti rahegi
        task = asyncio.create_task(bot_app.updater.start_polling())
        yield
        
        # Server band hone par bot ko safely close karna
        await bot_app.updater.stop()
        await bot_app.stop()
        await bot_app.shutdown()
    else:
        yield

# FastAPI Server Setup
app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Jarvis Crypto Bot is Alive!", "environment": settings.ENVIRONMENT}
