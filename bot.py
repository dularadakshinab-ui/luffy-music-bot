import discord
from discord.ext import commands
import os

TOKEN = os.environ.get("TOKEN")

RADIO_URL = "http://stream.zeno.fm/71ntub27u18uv"
VOICE_CHANNEL_ID = 1483395624278954086

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

voice_client = None


# ---------------- CONNECT ----------------
async def connect(ctx=None):
    global voice_client

    channel = bot.get_channel(VOICE_CHANNEL_ID)

    if channel is None:
        if ctx:
            await ctx.send("❌ Voice channel not found!")
        return

    # disconnect old connection if exists
    if voice_client and voice_client.is_connected():
        await voice_client.disconnect()

    voice_client = await channel.connect()

    if ctx:
        await ctx.send("✅ Joined voice channel!")


# ---------------- PLAY RADIO ----------------
async def play_radio(ctx=None):
    global voice_client

    if not voice_client:
        await connect(ctx)

    if not voice_client:
        return

    # always reset audio to avoid stuck state
    if voice_client.is_playing():
        voice_client.stop()

    source = discord.FFmpegPCMAudio(
        RADIO_URL,
        before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        options="-vn"
    )

    voice_client.play(source)

    if ctx:
        await ctx.send("🎵 Radio started!")


# ---------------- COMMANDS ----------------

@bot.command()
async def join(ctx):
    await connect(ctx)


@bot.command()
async def play(ctx):
    await play_radio(ctx)


@bot.command()
async def stop(ctx):
    global voice_client

    if voice_client and voice_client.is_playing():
        voice_client.stop()
        await ctx.send("⏹ Stopped radio")
    else:
        await ctx.send("⚠ Nothing is playing")


@bot.command()
async def leave(ctx):
    global voice_client

    if voice_client:
        await voice_client.disconnect()
        voice_client = None
        await ctx.send("👋 Left voice channel")
    else:
        await ctx.send("⚠ Not in voice channel")


@bot.command()
async def status(ctx):
    global voice_client

    if voice_client and voice_client.is_playing():
        await ctx.send("📻 Radio is playing 🎵")
    else:
        await ctx.send("⛔ Not playing anything")


@bot.command()
async def fix(ctx):
    global voice_client

    if voice_client and voice_client.is_connected():
        await voice_client.disconnect()
        voice_client = None

    await ctx.send("🔧 Reset done. Now use !play")


# ---------------- READY EVENT ----------------

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


bot.run(TOKEN)
