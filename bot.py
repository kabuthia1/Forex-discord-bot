import discord
from discord.ext import commands
import yfinance as yf
from datetime import datetime
import os  # ADDED FOR RAILWAY

# Setup bot with proper intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

print("🔄 Starting Forex Trading Bot...")

# ===== WHEN BOT STARTS =====
@bot.event
async def on_ready():
    print(f'✅ {bot.user} is ONLINE')
    print('📊 Available Forex Commands:')
    print('   !price EURUSD     - Get live price')
    print('   !pairs            - List major forex pairs')
    print('   !risk 1000 2 1.08 1.07 - Risk calculator')
    print('   !time             - Check trading sessions')
    print('   !helpme           - Show all commands')

# ===== COMMAND 1: LIVE PRICE =====
@bot.command()
async def price(ctx, pair="EURUSD"):
    """Get live forex price"""
    try:
        # Format pair for Yahoo Finance
        formatted_pair = f"{pair[:3]}{pair[3:]}=X"
        
        # Fetch data
        ticker = yf.Ticker(formatted_pair)
        data = ticker.history(period="1d", interval="1m")
        
        if len(data) > 0:
            current = data['Close'].iloc[-1]
            high = data['High'].max()
            low = data['Low'].min()
            change = current - data['Open'].iloc[0]
            change_pct = (change / data['Open'].iloc[0]) * 100
            
            # Create pretty message
            embed = discord.Embed(
                title=f"📊 {pair.upper()}",
                description=f"*Live Price: ${current:.5f}*",
                color=0x00ff00 if change >= 0 else 0xff0000,
                timestamp=datetime.now()
            )
            embed.add_field(name="📈 Daily High", value=f"${high:.5f}", inline=True)
            embed.add_field(name="📉 Daily Low", value=f"${low:.5f}", inline=True)
            embed.add_field(name="🔄 Change", value=f"{change:.5f} ({change_pct:.2f}%)", inline=True)
            embed.set_footer(text=f"Data from Yahoo Finance • {datetime.now().strftime('%H:%M:%S')}")
            
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"❌ Could not fetch data for {pair}")
            
    except Exception as e:
        await ctx.send(f"❌ Error: Check pair format (e.g., EURUSD, GBPUSD)")
        print(f"Error: {e}")

# ===== COMMAND 2: MAJOR PAIRS =====
@bot.command()
async def pairs(ctx):
    """Show major forex pairs"""
    major_pairs = [
        "EUR/USD - Euro/US Dollar",
        "USD/JPY - US Dollar/Japanese Yen", 
        "GBP/USD - British Pound/US Dollar",
        "USD/CHF - US Dollar/Swiss Franc",
        "AUD/USD - Australian Dollar/US Dollar",
        "USD/CAD - US Dollar/Canadian Dollar",
        "NZD/USD - New Zealand Dollar/US Dollar"
    ]
    
    embed = discord.Embed(
        title="🌐 Major Forex Pairs",
        description="Most traded currency pairs",
        color=0x3498db
    )
    
    for pair in major_pairs:
        embed.add_field(name=pair.split(" - ")[0], value=pair.split(" - ")[1], inline=False)
    
    embed.set_footer(text="Use: !price EURUSD (no slash)")
    await ctx.send(embed=embed)

# ===== COMMAND 3: RISK CALCULATOR =====
@bot.command()
async def risk(ctx, balance: float, risk_percent: float, entry: float, stop_loss: float):
    """Calculate position size"""
    risk_amount = balance * (risk_percent / 100)
    pips_risk = abs(entry - stop_loss) * 10000
    pip_value = risk_amount / pips_risk if pips_risk > 0 else 0
    position_size = pip_value * 100000  # Standard lot
    
    embed = discord.Embed(
        title="🎯 Risk Management Calculator",
        color=0xe74c3c
    )
    embed.add_field(name="💰 Account Balance", value=f"${balance:,.2f}", inline=False)
    embed.add_field(name="⚠️ Risk %", value=f"{risk_percent}%", inline=True)
    embed.add_field(name="💸 Risk Amount", value=f"${risk_amount:.2f}", inline=True)
    embed.add_field(name="📏 Pips at Risk", value=f"{pips_risk:.1f}", inline=True)
    embed.add_field(name="💎 Pip Value", value=f"${pip_value:.2f}", inline=True)
    embed.add_field(name="📦 Position Size", value=f"{position_size/100000:.2f} lots", inline=True)
    
    await ctx.send(embed=embed)

# ===== COMMAND 4: TRADING SESSIONS =====
@bot.command()
async def time(ctx):
    """Check current trading session times"""
    from datetime import datetime
    import pytz
    
    # Define sessions (UTC times)
    sessions = {
        "🇯🇵 Tokyo": {"open": 0, "close": 9, "active": False},
        "🇬🇧 London": {"open": 8, "close": 17, "active": False},
        "🇺🇸 New York": {"open": 13, "close": 22, "active": False}
    }
    
    current_hour = datetime.utcnow().hour
    
    # Check active sessions
    for session, times in sessions.items():
        if times["open"] <= current_hour < times["close"]:
            sessions[session]["active"] = True
    
    embed = discord.Embed(
        title="🕒 Forex Trading Sessions",
        description=f"Current UTC Time: {datetime.utcnow().strftime('%H:%M')}",
        color=0x9b59b6
    )
    
    for session, times in sessions.items():
        status = "✅ *OPEN*" if times["active"] else "❌ Closed"
        hours = f"{times['open']:02d}:00 - {times['close']:02d}:00 UTC"
        embed.add_field(name=session, value=f"{status}\n{hours}", inline=True)
    
    embed.set_footer(text="Most volatility: 08:00-12:00 & 13:00-17:00 UTC")
    await ctx.send(embed=embed)

# ===== COMMAND 5: HELP =====
@bot.command()
async def helpme(ctx):
    """Show all available commands"""
    embed = discord.Embed(
        title="🆘 Forex Bot Commands",
        description="Your personal trading assistant",
        color=0xf1c40f
    )
    
    commands = {
        "!price [pair]": "Live price (default: EURUSD)",
        "!pairs": "List major forex pairs",
        "!risk [balance] [risk%] [entry] [SL]": "Position size calculator",
        "!time": "Check trading sessions",
        "!helpme": "This help message"
    }
    
    for cmd, desc in commands.items():
        embed.add_field(name=cmd, value=desc, inline=False)
    
    embed.add_field(
        name="💡 Examples", 
        value="!price GBPUSD\n`!risk 5000 2 1.2650 1.2600`", 
        inline=False
    )
    
    await ctx.send(embed=embed)

# ===== RUN BOT =====
# Get token from environment variable (RAILWAY WILL PROVIDE THIS)
TOKEN = os.environ['DISCORD_TOKEN']

bot.run(TOKEN)