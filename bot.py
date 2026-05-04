import discord
from discord.ext import commands
import os

TOKEN = os.environ.get("TOKEN")

RADIO_URL = "https://open.spotify.com/playlist/2QWjR53UPARsEJb3gJUIKV?si=ce55f19c0d6541b7"
VOICE_CHANNEL_ID = 1483417064650702942

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

voice_client = None


# ---------------- JOIN ----------------
@bot.command()
async def join(ctx):
    global voice_client

    try:
        channel = ctx.guild.get_channel(VOICE_CHANNEL_ID)

        if channel is None:
            await ctx.send("❌ Voice channel not found")
            return

        if voice_client and voice_client.is_connected():
            await voice_client.disconnect()

        voice_client = await channel.connect()

        await ctx.send("✅ Joined voice channel")

    except Exception as e:
        await ctx.send(f"❌ Join error: {e}")
        print("JOIN ERROR:", e)


# ---------------- PLAY ----------------
@bot.command()
async def play(ctx):
    global voice_client

    try:
        if not voice_client:
            await join(ctx)

        if not voice_client:
            return

        if voice_client.is_playing():
            voice_client.stop()

        source = discord.FFmpegPCMAudio(
            RADIO_URL,
            before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            options="-vn"
        )

        voice_client.play(source)

        await ctx.send("🎵 Playing radio")

    except Exception as e:
        await ctx.send(f"❌ Play error: {e}")
        print("PLAY ERROR:", e)


# ---------------- STOP ----------------
@bot.command()
async def stop(ctx):
    global voice_client

    if voice_client and voice_client.is_playing():
        voice_client.stop()
        await ctx.send("⏹ Stopped")
    else:
        await ctx.send("⚠ Nothing playing")


# ---------------- LEAVE ----------------
@bot.command()
async def leave(ctx):
    global voice_client

    if voice_client:
        await voice_client.disconnect()
        voice_client = None
        await ctx.send("👋 Left voice")
    else:
        await ctx.send("⚠ Not in voice")


# ---------------- STATUS ----------------
@bot.command()
async def status(ctx):
    global voice_client

    if voice_client and voice_client.is_playing():
        await ctx.send("📻 Playing 🎵")
    else:
        await ctx.send("⛔ Not playing")


# ---------------- READY ----------------
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


bot.run(TOKEN)
