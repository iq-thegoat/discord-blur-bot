import io
from urllib.parse import urlparse
from blur import apply_blur_effect,apply_blur_effect_img
import discord
from discord import app_commands
from discord.ext import commands
from discord.ext import tasks
from discord import File
import aiohttp
import os
from loguru import logger
from typing import Union
from apis import TiktokDownloader,YoutubeDownloader,generate_random_file_id

bot = commands.Bot(command_prefix="-", intents=discord.Intents.all())


def create_ratio_string(
    percentage:Union[int,float],
    upchar: str = "🟩",
    downchar: str = "🟥",
):
    percentage = int(percentage)
    win_string = upchar * (percentage // 10)
    win_string = win_string + (downchar * (10 - len(win_string)))
    print(win_string)
    return f"progress:{win_string} ({round((percentage),2)}%)"


def create_embed(title: str, content: str, color: discord.Color):
    embed = discord.Embed(title=title, color=color)
    embed.add_field(name=content, value="")
    print(type(embed))
    return embed


async def download_attachment(attachment):
    async with aiohttp.ClientSession() as session:
        async with session.get(attachment.url) as resp:
            if resp.status == 200:
                data = await resp.read()
                # You can save the video to a file or process it as needed
                with open(f"{attachment.filename}", "wb") as f:
                    f.write(data)
                return True
            else:
                return False




@bot.command()
async def sync(ctx):
    fmt = await ctx.bot.tree.sync()
    print(f"Synced {len(fmt)}")


async def blur_vid(attachment:discord.Attachment or str,strength:int,interaction:discord.Interaction):
            if isinstance(attachment,discord.Attachment):
                if attachment.filename.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
                    if await download_attachment(attachment):
                        output = os.path.split(attachment.filename)[0]+"edited"+os.path.split(attachment.filename)[1]
                        for percentage in apply_blur_effect(input_file=attachment.filename,output_file=output,strength=strength):
                            print("PERCENTAGE"+str(percentage))
                            if isinstance(percentage,int) or isinstance(percentage,float):
                                await interaction.edit_original_response(embed=create_embed("Percentage",create_ratio_string(percentage),discord.Color.gold()))
                            elif isinstance(percentage,io.BytesIO):
                                vid = percentage
                                await interaction.edit_original_response(embed=create_embed("Uploading","finished blurring, uploading...",discord.Color.green()))
                                break
                            else:
                                vid = percentage
                        return (vid,attachment.filename)

                    else:
                        return "Couldn't download the video, sorry good luck next time"

                else:
                    return "attachment must be a video in one of these filetypes ('.mp4', '.mov', '.avi', '.mkv')"


            elif isinstance(attachment,str):
                name = generate_random_file_id()+".mp4"
                try:
                    parsed_url = urlparse(attachment)
                    domain = parsed_url.netloc
                except:
                    return "please use a valid url with the following format [scheme]://[domain]/[path]"
                if domain.lower() == "www.tiktok.com":
                    data = TiktokDownloader.download(url=attachment,output=name)
                elif domain.lower() == "youtube.com":
                    data = YoutubeDownloader.download(url=attachment,output=name)

                output = os.path.split(name)[0]+"edited"+os.path.split(name)[1]
                if data:
                        print(data)
                        for percentage in apply_blur_effect(input_file=name,output_file=output,strength=strength):
                            if isinstance(percentage,int) or isinstance(percentage,float):
                                await interaction.edit_original_response(embed=create_embed("Percentage",create_ratio_string(percentage),discord.Color.gold()))
                            elif isinstance(percentage,io.BytesIO):
                                vid = percentage
                                await interaction.edit_original_response(embed=create_embed("Uploading","finished blurring, now uploading...",discord.Color.green()))
                            else:
                                vid = percentage
                        return(vid,name)




@bot.tree.command(name="blur_video_test")
@app_commands.describe(
    message="caption",
    blur_strength="the strength of the blur",
    video="the video you want to blur",
    url ="the url of a video on one of theese platforms[Tiktok,Youtube]")
@app_commands.choices(
    blur_strength=[
        app_commands.Choice(name="low", value=10),
        app_commands.Choice(name="moderate", value=15),
        app_commands.Choice(name="medium", value=20),
        app_commands.Choice(name="high", value=25),
        app_commands.Choice(name="SUPER", value=30),
        app_commands.Choice(name="EXTREME", value=35),
        app_commands.Choice(name="MAXIMUM", value=50),
        app_commands.Choice(name="OVERKILL", value=1)]


)

async def blur_video(interaction:discord.Interaction,blur_strength:app_commands.Choice[int],video:discord.Attachment =None,message:str=" ",url:str =None):
    await interaction.response.send_message(embed=create_embed("Working On it...","",discord.Color.green()),ephemeral=True)
    if video:
        resp = await blur_vid(video,strength=int(blur_strength.value),interaction=interaction)
    else:
        resp = await blur_vid(url,strength=int(blur_strength.value),interaction=interaction)

    if isinstance(resp,tuple):
        member = interaction.user
        webhook = await interaction.channel.create_webhook(name=member.name)
        await webhook.send(
            str(message),file=File(resp[0],resp[1]),username=member.name, avatar_url=member.avatar.url)
        await interaction.delete_original_response()
        webhooks = await interaction.channel.webhooks()
        for webhook in webhooks:
                await webhook.delete()
    else:
        await interaction.edit_original_response(embed=create_embed("Error",resp,color=discord.Color.red()))







async def blur_img(attachment:discord.Attachment,radius:int):
    if attachment.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
        if await download_attachment(attachment):
            IMGIO = apply_blur_effect_img(attachment.filename,radius)
            if IMGIO:
                return (IMGIO,attachment.filename)
            else:
                return False

@bot.tree.command(name="blur_image_test")
@app_commands.describe(
    message="caption",
    blur_strength="the strength of the blur",
    image="the image you want to blur")
@app_commands.choices(
    blur_strength=[
        app_commands.Choice(name="low", value=6),
        app_commands.Choice(name="moderate", value=10),
        app_commands.Choice(name="medium", value=14),
        app_commands.Choice(name="high", value=22),


    ]
)



async def blur_image(interaction:discord.Interaction,blur_strength:app_commands.Choice[int],image:discord.Attachment,message:str=" "):
    await interaction.response.send_message(embed=create_embed("Working On it...","",discord.Color.green()),ephemeral=True)
    resp = await blur_img(image,radius=int(blur_strength.value))
    if isinstance(resp,tuple):
        member = interaction.user
        webhook = await interaction.channel.create_webhook(name=member.name)
        await webhook.send(
            str(message),file=File(resp[0],resp[1]),username=member.name, avatar_url=member.avatar.url)
        await interaction.delete_original_response()
        webhooks = await interaction.channel.webhooks()
        for webhook in webhooks:
                await webhook.delete()
    else:
        await interaction.edit_original_response(embed=create_embed("Error",resp,color=discord.Color.red()))



bot.run()
