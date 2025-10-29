import discord
import yt_dlp
import asyncio
from discord.ext import commands

yt_dl_opts = {"format": "bestaudio", "noplaylist": True}
ytdl = yt_dlp.YoutubeDL(yt_dl_opts)

ffmpeg_opts = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn"
}

queues = {}
current_sources = {}


def get_source(url: str):
    info = ytdl.extract_info(url, download=False)
    return info["url"], info.get("title", "Unknown title")


async def animate_extraction(ctx, msg):
    frames = ["○", "●"]
    i = 0
    while True:
        try:
            frame = frames[i % len(frames)]
            await msg.edit(content=f"[ FFMPEG ] **Extracting and Downloading URL** (  {frame}  )")
            await asyncio.sleep(0.25)
            i += 1
        except (discord.NotFound, asyncio.CancelledError):
            break


async def next_song(ctx):
    vc = ctx.voice_client
    if ctx.guild.id in queues and queues[ctx.guild.id]:
        msg = await ctx.send("[ FFMPEG ] **Extracting and Downloading URL**")
        task = asyncio.create_task(animate_extraction(ctx, msg))

        song = queues[ctx.guild.id].pop(0)
        source_url, title = await asyncio.to_thread(get_source, song["url"])
        current_sources[ctx.guild.id] = source_url

        await asyncio.sleep(1.5)
        task.cancel()

        try:
            await msg.edit(content=f"[ FFMPEG ] **Stream ready!** (  ✓  )")
        except Exception:
            pass

        vc.play(
            discord.FFmpegPCMAudio(source_url, **ffmpeg_opts),
            after=lambda e: asyncio.run_coroutine_threadsafe(next_song(ctx), ctx.bot.loop)
        )
        await ctx.send(f"[  ▶  ] Now playing: **{title}**")
    else:
        await ctx.send("[  *  ] Queue finished")
        current_sources.pop(ctx.guild.id, None)


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def add(self, ctx, url: str):
        if not ctx.author.voice:
            await ctx.send("You need to be on a voice channel, man. Sybau")
            return

        if not ctx.voice_client:
            await ctx.author.voice.channel.connect(self_deaf=True)

        source_url, title = await asyncio.to_thread(get_source, url)

        if ctx.guild.id not in queues:
            queues[ctx.guild.id] = []

        queues[ctx.guild.id].append({"url": url, "title": title})
        await ctx.send(f"[  *  ] Music added: **{title}**")

        vc = ctx.voice_client
        if not vc.is_playing() and not vc.is_paused():
            await next_song(ctx)

    @commands.command()
    async def stop(self, ctx):
        vc = ctx.voice_client
        if vc and vc.is_playing():
            vc.pause()
            await ctx.send("[  ❚❚  ] Paused")
        else:
            await ctx.send("[  *  ] No music on queue")

    @commands.command()
    async def play(self, ctx):
        vc = ctx.voice_client
        if vc and vc.is_paused():
            vc.resume()
            await ctx.send("[  ▶  ] Playing")
        elif not vc:
            await ctx.send("Im not in a voice channel. Lemme join u! :D")
        else:
            await ctx.send("[  *  ] No music on queue")

    @commands.command()
    async def skip(self, ctx):
        vc = ctx.voice_client
        if vc and vc.is_playing():
            vc.stop()
            await ctx.send("[  ►►  ] Skipped ")
        else:
            await ctx.send("[  *  ] No music on queue")

    @commands.command()
    async def queue(self, ctx):
        if ctx.guild.id not in queues or len(queues[ctx.guild.id]) == 0:
            await ctx.send("[  *  ] No music on queue")
            return

        queue_list = "\n".join(
            [f"{i + 1}. **{song['title']}**" for i, song in enumerate(queues[ctx.guild.id])]
        )
        await ctx.send(f"[  *  ] **Queue:**\n{queue_list}")

    @commands.command()
    async def exit(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("👋 Bye bye")
        else:
            await ctx.send("Im not on a voice channel, vro")


async def setup(bot):
    await bot.add_cog(Music(bot))
