import discord
from discord.ext import commands
from discord.player import FFmpegPCMAudio
from discord.utils import get
import os
from youtube_dl import YoutubeDL
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

song_queue = ["defaut"]
song = []
client = commands.Bot(command_prefix="!", case_insensitive=True)

ydl_opts = {
    "format": "bestaudio",
    "noplaylist": True,
    "ignoreerrors": True,
    "logtostderr": False,
    "no_warnings": True,
    "default_search": "ytsearch1",
}
FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}


@client.event
async def on_ready():
    print("Bot is now online...")
    await client.change_presence(activity=discord.Game(name="TAKO | !play"))


@client.command(aliases=["p", "pl", "pla", "sing", "music", "song", "adin"])
async def play(ctx, *args):
    url = ' '.join(args)
    global song_queue
    voice = get(client.voice_clients, guild=ctx.guild)
    channel = ctx.message.author.voice.channel
    if voice and voice.is_connected():
        # song_queue.clear()
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
    if len(url) <= 0:
        await ctx.send("TAKO Does No Understand")
        return
    song_queue.append(url)
    await ctx.send(f"Searching... {url.upper()}")
    # song_queue.append(song)
    global song
    try:
        if not voice.is_playing() and not voice.is_paused():
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(song_queue[1], download=False)
            if info.get("url", None):
                data = info
            else:
                data = info["entries"][0]
            TITLE = data["title"]
            URL = data["url"]
            DURATION = data["duration"]
            THUMBNAIL = data["thumbnail"]
            song = {
                "title": TITLE,
                "url": URL,
                "duration": DURATION,
                "thumbnail": THUMBNAIL,
            }
            del song_queue[0]
            voice.play(
                discord.PCMVolumeTransformer(
                    FFmpegPCMAudio(song["url"], **FFMPEG_OPTIONS), volume=0.3
                ),
                after=lambda e: play_next(ctx),
            )
            voice.is_playing()
            x = divmod(song["duration"], 60)
            y = str(f"{x[0]:02d}") + ":" + str(f"{x[1]:02d}")
            now = datetime.now() + timedelta(hours=2)
            current_time = now.strftime("%H:%M")
            embed = discord.Embed(
                title=song["title"],
                description="Requested by: \n" + str(ctx.message.author),
                color=discord.Color.purple(),
            )
            embed.set_thumbnail(url=song["thumbnail"])
            embed.add_field(name="Status", value="Now Playing", inline=True)
            embed.add_field(name="Duration", value=y)
            embed.set_footer(text=current_time)
            # await ctx.send(f"Now playing: {song['title']} | Song Duration: {y}")
            await ctx.send(embed=embed)
            song.clear()
        else:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(
                    song_queue[-1], download=False
                )
                if info.get("url", None):
                    data = info
                else:
                    data = info["entries"][0]
                TITLE = data["title"]
                URL = data["url"]
                DURATION = data["duration"]
                THUMBNAIL = data["thumbnail"]
                song = {
                    "title": TITLE,
                    "url": URL,
                    "duration": DURATION,
                    "thumbnail": THUMBNAIL,
                    "author": str(ctx.message.author),
                }
                x = divmod(song["duration"], 60)
                y = str(f"{x[0]:02d}") + ":" + str(f"{x[1]:02d}")
                embed = discord.Embed(
                    title="Added to Queue",
                    description="Requested By: \n" + song["author"],
                    color=discord.Color.purple(),
                )
                embed.set_thumbnail(url=song["thumbnail"])
                embed.add_field(name="Song", value=song["title"], inline=True)
                embed.add_field(name="Duration", value=y)
                # await ctx.send(f"Added to Queue: {song['title']} | Song Duration: {y}")
                await ctx.send(embed=embed)
                song.clear()
    except Exception as e:
        del song_queue[-1]
        await ctx.send(e)
        return


@client.command()
async def leave(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.stop()
    if voice.is_connected():
        await voice.disconnect()


@client.command()
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send("No Audio is playing...")


@client.command()
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.send("The audio is not paused.")


@client.command()
async def stop(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    voice.stop()


def play_next(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)
    if len(song_queue) > 1:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(song_queue[1], download=False)
            if info.get("url", None):
                data = info
            else:
                data = info["entries"][0]
            TITLE = data["title"]
            URL = data["url"]
            DURATION = data["duration"]
            THUMBNAIL = data["thumbnail"]
            song = {
                "title": TITLE,
                "url": URL,
                "duration": DURATION,
                "thumbnail": THUMBNAIL,
                "author": str(ctx.message.author),
            }
        del song_queue[0]
        voice.play(
            discord.PCMVolumeTransformer(
                FFmpegPCMAudio(song["url"], **FFMPEG_OPTIONS), volume=0.3
            ),
            after=lambda e: play_next(ctx),
        )
        voice.is_playing()
        x = divmod(song["duration"], 60)
        y = str(f"{x[0]:02d}") + ":" + str(f"{x[1]:02d}")
        # ctx.send(f"Now playing: {song['title']} | Song Duration: {y}")
        now = datetime.now() + timedelta(hours=2)
        current_time = now.strftime("%H:%M")
        embed = discord.Embed(
            title=song["title"],
            description="Requested by: \n" + str(ctx.message.author),
            color=discord.Color.purple(),
        )
        embed.set_thumbnail(url=song["thumbnail"])
        embed.add_field(name="Status", value="Now Playing", inline=True)
        embed.add_field(name="Duration", value=y)
        embed.set_footer(text=current_time)
        coro = ctx.send(embed=embed)
        fut = asyncio.run_coroutine_threadsafe(coro, client.loop)
        try:
            fut.result()
        except Exception as e:
            corou = ctx.send(e)
            new_fut = asyncio.run_coroutine_threadsafe(corou, client.loop)
            new_fut.result()
            pass


@client.command(pass_context=True, aliases=["s", "fs"])
async def skip(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.stop()


@client.command(aliases=["ps"])
async def playskip(ctx, *args):
    url = " ".join(args)
    voice = get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.stop()
        song_queue.clear()
        song_queue.append(url)
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(song_queue[1], download=False)
            if info.get("url", None):
                data = info
            else:
                data = info["entries"][0]
            TITLE = data["title"]
            URL = data["url"]
            DURATION = data["duration"]
            THUMBNAIL = data["thumbnail"]
            song = {
                "title": TITLE,
                "url": URL,
                "duration": DURATION,
                "thumbnail": THUMBNAIL,
                "author": str(ctx.message.author),
            }
        del song_queue[0]
        voice.play(
            discord.PCMVolumeTransformer(
                FFmpegPCMAudio(song["url"], **FFMPEG_OPTIONS), volume=0.3
            ),
            after=lambda e: play_next(ctx),
        )
        voice.is_playing()
        x = divmod(song["duration"], 60)
        y = str(f"{x[0]:02d}") + ":" + str(f"{x[1]:02d}")
        now = datetime.now() + timedelta(hours=2)
        current_time = now.strftime("%H:%M")
        embed = discord.Embed(
            title=song["title"],
            description="Requested by: \n" + str(ctx.message.author),
            color=discord.Color.purple(),
        )
        embed.set_thumbnail(url=song["thumbnail"])
        embed.add_field(name="Status", value="Now Playing", inline=True)
        embed.add_field(name="Duration", value=y)
        embed.set_footer(text=current_time)
        await ctx.send(embed=embed)


@client.command(aliases=["pn"])
async def playnext(ctx, *args):
    url = " ".join(args)
    song_queue.append(url)
    song_queue.insert(1, song_queue.pop())
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(song_queue[1], download=False)
        if info.get("url", None):
            data = info
        else:
            data = info["entries"][0]
        TITLE = data["title"]
        URL = data["url"]
        DURATION = data["duration"]
        THUMBNAIL = data["thumbnail"]
        song = {
            "title": TITLE,
            "url": URL,
            "duration": DURATION,
            "thumbnail": THUMBNAIL,
            "author": str(ctx.message.author),
        }
        x = divmod(song["duration"], 60)
        y = str(f"{x[0]:02d}") + ":" + str(f"{x[1]:02d}")
        now = datetime.now() + timedelta(hours=2)
        current_time = now.strftime("%H:%M")
        embed = discord.Embed(
            title="Playing Next",
            description="Requested by: \n" + str(ctx.message.author),
            color=discord.Color.purple(),
        )
        embed.set_thumbnail(url=song["thumbnail"])
        embed.add_field(name="Song", value=song["title"], inline=True)
        embed.add_field(name="Duration", value=y)
        embed.set_footer(text=current_time)
        await ctx.send(embed=embed)


@client.command(aliases=["q"])
async def queuelist(ctx):
    await ctx.send(">>Now Playing")
    await ctx.send(f"{0}. {song_queue[0]}")
    await ctx.send(">>Up Next")
    for x in range(1,len(song_queue)):
        await ctx.send(f"{x}. {song_queue[x]}")


@client.command(aliases=["r"])
async def remove(ctx, *args):
    try:
        x = int(" ".join(args))
    except:
        ctx.send(">>> Enter a number")
    if len(song_queue) > 1:
        temp = (song_queue[x]).upper()
        del song_queue[x]
        await ctx.send(f"{temp} has been removed from queue")


@client.command(aliases=["switch"])
async def replace(ctx, *args):
    fullstring = " ".join(args)
    try:
        origin = int(fullstring[0]) - 1
        target = int(fullstring[2]) - 1
    except:
        ctx.send('>>> Message needs to be 2 numbers with space in between e.g. "3 1"')
    temp = song_queue[target]
    song_queue[target] = song_queue[origin]
    song_queue[origin] = temp

    await ctx.send(f"Song {fullstring[0]} and {fullstring[2]} has been switched")


client.run(os.getenv("TOKEN"))
