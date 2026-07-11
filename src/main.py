import asyncio
import httpx
from openai import AsyncOpenAI
from fastapi import FastAPI
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from src.config import settings
from contextlib import asynccontextmanager

# OpenAI Setup (Agar key daali hai tabhi active hoga)
openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "test_key" else None

# Command 1: Start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello Boss! Jarvis AI is Online. 🚀 Ready for crypto analysis!")

# Command 2: Live Crypto Price (Binance API - No Key Required)
async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Bhai, coin ka naam toh batao! (Example: /price BTCUSDT)")
        return
    
    symbol = context.args[0].upper()
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = response.json()
            
        if "price" in data:
            price = float(data['price'])
            await update.message.reply_text(f"💰 **{symbol} Live Price:** ${price:,.2f}", parse_mode="Markdown")
        else:
            await update.message.reply_text(f"❌ {symbol} nahi mila. Sahi naam daalo (e.g., ETHUSDT, SOLUSDT).")
    except Exception as e:
        await update.message.reply_text("⚠️ Market data lane mein error aayi.")

# Command 3: AI Market Analysis (OpenAI API Required)
async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not openai_client:
        await update.message.reply_text("⚠️ Boss, OpenAI API Key missing hai. Pehle Railway me key daalo!")
        return
        
    if not context.args:
        await update.message.reply_text("Coin ka naam daalo! (Example: /analyze BTC)")
        return
        
    coin = context.args[0].upper()
    await update.message.reply_text(f"🧠 Jarvis {coin} ko analyze kar raha hai... Please wait.")
    
    prompt = f"You are Jarvis, a pro crypto analyst. Give a short, highly technical 3-sentence analysis for {coin}. Mention trend, key support, and resistance levels. Do not give financial advice. Keep it crisp."
    
    try:
        response = await openai_client.chat.completions.create(
            model="gpt-3.5-turbo", # Aap chaho toh ise 'gpt-4o' kar sakte ho
            messages=[{"role": "user", "content": prompt}]
        )
        ai_reply = response.choices[0].message.content
        await update.message.reply_text(f"📊 **{coin} AI Analysis:**\n\n{ai_reply}", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"⚠️ AI Server Error: {str(e)}")

# Background Server & Telegram Setup
@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.TELEGRAM_BOT_TOKEN != "test_token":
        bot_app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
        
        # Naye commands ko bot se link karna
        bot_app.add_handler(CommandHandler("start", start_command))
        bot_app.add_handler(CommandHandler("price", price_command))
        bot_app.add_handler(CommandHandler("analyze", analyze_command))
        
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

@app.get("/")
async def root():
    return {"message": "Jarvis Crypto Bot is Alive!", "environment": settings.ENVIRONMENT}
