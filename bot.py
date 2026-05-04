import discord
from discord.ext import commands
import os

TOKEN = os.environ.get("TOKEN")

# Use HTTPS for better stability in Railway
RADIO_URL = "https://stream.zeno.fm/71ntub27u18uv"
VOICE_CHANNEL_ID = 1483417064650702942

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

voice_client = None


# ---------------- CONNECT ----------------
async def connect(ctx):
    global voice_client

    try:
        channel = ctx.guild.get_channel(VOICE_CHANNEL_ID)

        if not channel:
            await ctx.send("❌ Voice channel not found")
            return

        if voice_client and voice_client.is_connected():
            await voice_client.disconnect()

        voice_client = await channel.connect()

        await ctx.send("✅ Joined voice channel!")

    except Exception as e:
        print("VOICE ERROR:", e)
        await ctx.send(f"❌ Join failed: {e}")


# ---------------- PLAY RADIO ----------------
async def play_radio(ctx):
    global voice_client

    try:
        if not voice_client:
            await connect(ctx)

        if not voice_client:
            return

        if voice_client.is_playing():
            voice_client.stop()

        source = discord.FFmpegPCMAudio(
            RADIO_URL,
            executable="ffmpeg",
            before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            options="-vn -loglevel quiet"
        )

        voice_client.play(source)

        await ctx.send("🎵 Radio started!")

    except Exception as e:
        print("AUDIO ERROR:", e)
        await ctx.send(f"❌ Play failed: {e}")


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
        await ctx.send("⏹ Stopped")
    else:
        await ctx.send("⚠ Nothing playing")


@bot.command()
async def leave(ctx):
    global voice_client

    if voice_client:
        await voice_client.disconnect()
        voice_client = None
        await ctx.send("👋 Left voice")
    else:
        await ctx.send("⚠ Not in voice")


@bot.command()
async def status(ctx):
    global voice_client

    if voice_client and voice_client.is_playing():
        await ctx.send("📻 Playing 🎵")
    else:
        await ctx.send("⛔ Not playing")


@bot.command()
async def fix(ctx):
    global voice_client

    if voice_client and voice_client.is_connected():
        await voice_client.disconnect()

    voice_client = None
    await ctx.send("🔧 Reset done")


# ---------------- READY ----------------

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


bot.run(TOKEN)
