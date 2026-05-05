import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
import asyncio

TOKEN = os.getenv("TOKEN")

SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")

VOICE_CHANNEL_ID = 1483417064650702942  # your voice channel ID

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Spotify
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET
))

# YouTube
ytdl = yt_dlp.YoutubeDL({
    "format": "bestaudio",
    "quiet": True
})

queue = []
last_song = None
voice_client = None


# ---------------- VOICE CONNECT ----------------
async def join_voice():
    global voice_client

    channel = bot.get_channel(VOICE_CHANNEL_ID)
    if not channel:
        return False

    if voice_client and voice_client.is_connected():
        await voice_client.disconnect()

    voice_client = await channel.connect()
    return True


# ---------------- SPOTIFY FIXED ----------------
def get_spotify_tracks(url):
    tracks = []

    playlist = sp.playlist(url)
    results = sp.playlist_items(playlist["id"])

    while results:
        for item in results["items"]:
            track = item.get("track")
            if not track:
                continue

            name = track["name"]
            artist = track["artists"][0]["name"]
            tracks.append(f"{name} {artist}")

        if results["next"]:
            results = sp.next(results)
        else:
            break

    return tracks


# ---------------- PLAY NEXT ----------------
async def play_next(channel):
    global queue, last_song, voice_client

    if queue:
        song = queue.pop(0)
        last_song = song
    elif last_song:
        song = last_song
    else:
        await channel.send("📭 Queue finished")
        return

    try:
        info = ytdl.extract_info(f"ytsearch1:{song}", download=False)

        if not info["entries"]:
            await channel.send(f"❌ Not found: {song}")
            await play_next(channel)
            return

        url = info["entries"][0]["url"]

        source = discord.FFmpegPCMAudio(
            url,
            before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            options="-vn"
        )

        voice_client.play(
            source,
            after=lambda e: asyncio.run_coroutine_threadsafe(play_next(channel), bot.loop)
        )

        await channel.send(f"🎶 Now playing: **{song}**")

    except Exception as e:
        print("ERROR:", e)
        await play_next(channel)


# ---------------- /PLAY ----------------
@bot.tree.command(name="play", description="Play song or Spotify playlist")
async def play(interaction: discord.Interaction, query: str):
    global queue, voice_client

    await interaction.response.defer()

    if not voice_client:
        ok = await join_voice()
        if not ok:
            await interaction.followup.send("❌ Voice channel not found")
            return

    if "spotify.com/playlist" in query:
        tracks = get_spotify_tracks(query)
        queue.extend(tracks)
        await interaction.followup.send(f"✅ Added {len(tracks)} songs from Spotify")

    else:
        queue.append(query)
        await interaction.followup.send(f"🎵 Added: {query}")

    if not voice_client.is_playing():
        await play_next(interaction.channel)


# ---------------- /SKIP ----------------
@bot.tree.command(name="skip", description="Skip song")
async def skip(interaction: discord.Interaction):
    if voice_client and voice_client.is_playing():
        voice_client.stop()
        await interaction.response.send_message("⏭ Skipped")
    else:
        await interaction.response.send_message("⚠ Nothing playing")


# ---------------- /STOP ----------------
@bot.tree.command(name="stop", description="Stop music")
async def stop(interaction: discord.Interaction):
    global queue
    queue.clear()

    if voice_client and voice_client.is_playing():
        voice_client.stop()

    await interaction.response.send_message("⏹ Stopped")


# ---------------- READY ----------------
@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} commands")
    except Exception as e:
        print("Sync error:", e)

    print(f"Logged in as {bot.user}")

    try:
        await join_voice()
        print("🎧 Auto joined voice channel")
    except:
        pass


bot.run(TOKEN)
