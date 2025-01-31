import discord
from discord.ext import commands
import asyncio
import yt_dlp

intents = discord.Intents.default()  # Use default intents (no privileged ones)
intents.message_content = True  # Enable message content intent if needed

bot = commands.Bot(command_prefix="!", intents=intents)

# Dictionary to store queues for each server
queues = {}

@bot.event
async def on_ready():
    print(f"Bot is ready. Logged in as {bot.user}")

# Join voice channel
@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await channel.connect()
        else:
            if ctx.voice_client.channel != channel:
                await ctx.voice_client.move_to(channel)
    else:
        await ctx.send("You need to be in a vc for this")

# Leave voice channel
@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
    else:
        await ctx.send("I'm not in a vc")

# Play music
@bot.command()
async def play(ctx, *, search):
    # Check if the bot is connected to a voice channel
    if not ctx.voice_client or not ctx.voice_client.is_connected():
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect()
        else:
            await ctx.send("You need to be in a vc for this")
            return

    vc = ctx.voice_client

    # Ensure no duplicate messages when playing
    if vc and vc.channel and vc.channel == ctx.author.voice.channel:
        # Download audio from YouTube
        ydl_opts = {
            "format": "bestaudio",
            "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3"}],
            "quiet": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{search}", download=False)
            url = info["entries"][0]["url"]

        # Play the audio
        ffmpeg_path = r"C:\\yourpath"  # Replace with your actual FFmpeg path
        if not vc.is_playing():
            vc.play(discord.FFmpegPCMAudio(url, executable=ffmpeg_path), after=lambda e: check_queue(ctx))
            await ctx.send(f"Now playing: {info['entries'][0]['title']}")
        else:
            # Add to the queue
            if ctx.guild.id not in queues:
                queues[ctx.guild.id] = []
            queues[ctx.guild.id].append(url)
            await ctx.send(f"Added to queue: {info['entries'][0]['title']}")
    else:
        await ctx.send("You need to be in the same voice channel as the bot.")


# Skip the current song
@bot.command()
async def skip(ctx):
    if not ctx.voice_client or not ctx.voice_client.is_connected():
        await ctx.send("I'm not in a vc")
        return

    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Skipped the current song.")
    else:
        await ctx.send("Nothing is playing...")

# Stop music
@bot.command()
async def stop(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Stopped playing music. (loser)")
    else:
        await ctx.send("Nothing is playing...")

# Check queue and play next song
def check_queue(ctx):
    if ctx.guild.id in queues and len(queues[ctx.guild.id]) > 0:
        next_song = queues[ctx.guild.id].pop(0)
        ffmpeg_path = r"C:\\yourpath"
        ctx.voice_client.play(discord.FFmpegPCMAudio(next_song, executable=ffmpeg_path), after=lambda e: check_queue(ctx))

# Debug voice connection status
@bot.command()
async def status(ctx):
    if ctx.voice_client:
        await ctx.send(f"Connected to: {ctx.voice_client.channel}")
    else:
        await ctx.send("I'm not in a vc :D'")

bot.run("")
