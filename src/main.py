import asyncio
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes
from src.config import settings
from contextlib import asynccontextmanager

# Yeh line Python ko batati hai ki HTML files 'templates' folder me hain
templates = Jinja2Templates(directory="templates")

# --- TELEGRAM BOT LOGIC ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # YAHAN APNA ASLI RAILWAY LINK DAALEIN
    webapp_url = "https://cryotobot-production.up.railway.app/" 
    
    # Yeh code ek button banata hai
    keyboard = [
        [InlineKeyboardButton("Launch Jarvis AI 🚀", web_app=WebAppInfo(url=webapp_url))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Yeh code wo button user ko bhejta hai
    await update.message.reply_text(
        "Welcome to the Jarvis Trading Terminal.\nClick below to open the Mini App.",
        reply_markup=reply_markup
    )

# --- FASTAPI SERVER LOGIC (Background Process) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.TELEGRAM_BOT_TOKEN != "test_token":
        bot_app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
        bot_app.add_handler(CommandHandler("start", start_command))
        
        await bot_app.initialize()
        await bot_app.start()
        task = asyncio.create_task(bot_app.updater.start_polling())
        yield
        await bot_app.updater.stop()
        await bot_app.stop()
        await bot_app.shutdown()
    else:
        yield

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

# Yeh endpoint browser ya Telegram me HTML page dikhane ka kaam karta hai
@app.get("/", response_class=HTMLResponse)
async def render_mini_app(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
