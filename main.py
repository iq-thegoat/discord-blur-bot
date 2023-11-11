import io

from blur import apply_blur_effect
import discord
from discord import app_commands
from discord.ext import commands
from discord.ext import tasks
from discord import File
import aiohttp
import os
from loguru import logger


bot = commands.Bot(command_prefix="-", intents=discord.Intents.all())


@logger.catch()
async def download_video(attachment):
    async with aiohttp.ClientSession() as session:
        async with session.get(attachment.url) as resp:
            if resp.status == 200:
                data = await resp.read()
                # You can save the video to a file or process it as needed
                with open(f"{attachment.filename}", "wb") as f:
                    f.write(data)
                print("Downloaded Video")
                return True
            else:
                return False



@logger.catch()
@bot.command()
async def sync(ctx):
    fmt = await ctx.bot.tree.sync()
    print(f"Synced {len(fmt)}")

@logger.catch()
async def blur(attachment:discord.Attachment,strength:int):
            if attachment.filename.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
                if await download_video(attachment):
                    output = os.path.split(attachment.filename)[0]+"edited"+os.path.split(attachment.filename)[1]
                    vid = apply_blur_effect(input_file=attachment.filename,output_file=output,strength=strength,applies=1)
                    return (vid,attachment.filename)
                else:
                    return "Couldn't download the video, sorry good luck next time"
            else:
                return "attachment must be a video in one of these filetypes ('.mp4', '.mov', '.avi', '.mkv')"


@logger.catch()
def create_embed(title: str, content: str, color: discord.Color):
    embed = discord.Embed(title=title, color=color)
    embed.add_field(name=content, value="")
    print(type(embed))
    return embed

@bot.tree.command(name="blur_video")
@app_commands.describe(
    message="caption",
    blur_strength="the strength of the blur",
    video="the video dumbass")
@app_commands.choices(
    blur_strength=[
        app_commands.Choice(name="low",value=5),
        app_commands.Choice(name="mid",value=10),
        app_commands.Choice(name="high",value=15),
        app_commands.Choice(name="SUPER",value=20),
        app_commands.Choice(name="SUPER SUPER",value=25)

    ]
)
@logger.catch()
async def blur_func(interaction:discord.Interaction,message:str,blur_strength:app_commands.Choice[int],video:discord.Attachment):
    await interaction.response.defer()
    resp = await blur(video,strength=int(blur_strength.value))
    if isinstance(resp,tuple):
        member = interaction.user
        webhook = await interaction.channel.create_webhook(name=member.name)
        await webhook.send(
            str(message),file=File(resp[0],resp[1]),username=member.name, avatar_url=member.avatar.url)

        webhooks = await interaction.channel.webhooks()
        for webhook in webhooks:
                await webhook.delete()
        await interaction.response.send_message("sent",ephemeral=True)
    else:
        await interaction.response.send_message(embed=create_embed("Error",resp,color=discord.Color.red()))










bot.run(os.environ.get("token"))
