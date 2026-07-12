import asyncio
import httpx
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes
from src.config import settings
from contextlib import asynccontextmanager

templates = Jinja2Templates(directory="templates")

# --- TELEGRAM BOT LOGIC ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    webapp_url = "https://cryotobot-production.up.railway.app/" 
    
    keyboard = [
        [InlineKeyboardButton("Launch Jarvis AI 🚀", web_app=WebAppInfo(url=webapp_url))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Welcome to the Jarvis Trading Terminal.\nClick below to open the Mini App.",
        reply_markup=reply_markup
    )

# --- FASTAPI SERVER LOGIC ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.TELEGRAM_BOT_TOKEN != "test_token":
        bot_app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
        bot_app.add_handler(CommandHandler("start", start_command))
        
        await bot_app.initialize()
        await bot_app.start()
        task = asyncio.create_task(bot_app.updater.start_polling(drop_pending_updates=True))
        yield
        await bot_app.updater.stop()
        await bot_app.stop()
        await bot_app.shutdown()
    else:
        yield

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

@app.get("/", response_class=HTMLResponse)
async def render_mini_app(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Route 2: Crypto Prices (CoinCap API - 100% Free & Reliable)
@app.get("/api/market-data")
async def get_market_data():
    url = "https://api.coincap.io/v2/assets?limit=10"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            data = response.json()
            
            formatted_data = []
            for item in data.get("data", []):
                formatted_data.append({
                    "symbol": f"{item['symbol']}/USD",
                    "price": float(item['priceUsd']),
                    "changePercent": float(item['changePercent24Hr'])
                })
            return JSONResponse(content={"status": "success", "data": formatted_data})
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)

# Route 3: Live Crypto News (CryptoCompare API)
@app.get("/api/news")
async def get_crypto_news():
    url = "https://min-api.cryptocompare.com/data/v2/news/?lang=EN"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=10.0)
            data = response.json()
            
            formatted_news = []
            for item in data.get('Data', [])[:5]:
                formatted_news.append({
                    "title": item["title"],
                    "source": item["source_info"]["name"],
                    "url": item["url"],
                    "image": item["imageurl"]
                })
            return JSONResponse(content={"status": "success", "data": formatted_news})
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)
