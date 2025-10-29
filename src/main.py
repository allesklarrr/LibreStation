import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="libre!", intents=intents, help_command=None)


@bot.command(name="help")
async def help_command(ctx):
    embed = discord.Embed(
        title="📜 LibreStation Music Bot Help",
        description="Comandos disponíveis:",
        color=discord.Color.green()
    )
    embed.add_field(name="🎵 **libre!add <url>**", value="Adiciona uma música à fila e começa a tocar.", inline=False)
    embed.add_field(name="⏸ **libre!stop**", value="Pausa a reprodução atual.", inline=False)
    embed.add_field(name="▶️ **libre!play**", value="Retoma a música pausada.", inline=False)
    embed.add_field(name="⏭ **libre!skip**", value="Pula para a próxima música da fila.", inline=False)
    embed.add_field(name="📋 **libre!queue**", value="Mostra a fila de reprodução.", inline=False)
    embed.add_field(name="👋 **libre!exit**", value="Desconecta o bot do canal de voz.", inline=False)
    embed.set_footer(text="Feito com ♥ usando discord.py e yt-dlp")
    await ctx.send(embed=embed)


@bot.event
async def on_ready():
    print(f"[ LOG ] Bot conectado como: {bot.user}")


async def load_cogs():
    for filename in os.listdir("./src/cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"src.cogs.{filename[:-3]}")


async def main():
    async with bot:
        await load_cogs()
        await bot.start(os.getenv("BOT_TOKEN"))


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
