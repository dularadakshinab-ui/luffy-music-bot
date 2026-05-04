dadasdadadimport discord
from discord.ext import commands, tasks
import os

TOKEN = os.environ.get("TOKEN") 

RADIO_URL = "http://stream.zeno.fm/71ntub27u18uv"
VOICE_CHANNEL_ID = 1483395624278954086  # 👈 PUT YOUR CHANNEL ID

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

voice_client = None

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    keep_alive.start()

async def connect():
    global voice_client
    channel = bot.get_channel(VOICE_CHANNEL_ID)

    if not voice_client or not voice_client.is_connected():
        voice_client = await channel.connect()

async def play():
    global voice_client

    if voice_client and not voice_client.is_playing():
        source = discord.FFmpegPCMAudio(
            RADIO_URL,
            before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            options="-vn"
        )
        voice_client.play(source)

@tasks.loop(seconds=15)
async def keep_alive():
    try:
        await connect()
        await play()
    except Exception as e:
        print(e)

bot.run(TOKEN)
