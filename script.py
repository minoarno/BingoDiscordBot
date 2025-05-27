import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
from PIL import Image, ImageDraw, ImageFont
import random
import webbrowser

import webserver

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log',
                              encoding='utf-8',
                              mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Remove standard help-command
bot.remove_command('help')

bingoFont = ImageFont.truetype('ARIAL.TTF', 18)

length = 600
amount = 5
offset = (length / amount)
margin = 10

rbBingoList = [
    "Insert server?", "Do we need to buy cannon?", "Can I have allowance",
    "Placed the cannon outside of instance", "lEvEl X?",
    "Puturum first mudster first?", "Harper break", "Bcn?",
    "Comparing someone to oresu", "Ctg?", "Time / start when?",
    "ppl jumping into water before khan dies", "Mimi shenanigans",
    "Alkamor calling someone a cretin (deservably)",
    "Vell taxi, vell first or vell break", "Khan platoon",
    "Someone from RB dying on bosses like a twat",
    "Somebody getting a jackpot drop", "PPl autopathing to boss",
    "Someone crashing", "Can someone deploy cannon", "Someone dying to khan",
    "Training cannon", "Do we host to avoid twats ?",
    "Someone forgetting to participate."
]

coBingoList = [
    "Can I have allowance ?", "Placed the cannon outside of instance ?",
    "Ppl jumping into water before khan dies",
    "Alkamor calling someone a cretin (deservably)",
    "Somebody getting a jackpot drop", "PPl autopathing to boss",
    "Someone crashing", "Someone dying to khan",
    "Someone forgetting to participate.", "Twat posting 435345435 heart.",
    "Twilight Warrior clicks a button", "Lecko clicks button",
    "Player is in a platoon with Inso", "Inso not even being in game",
    "Someone doesnt get loot and complains", "Inso says fuck you",
    "Petty says she’s new", "Reed drops a strike",
    "RB not clicking the button", "Registration error",
    "Someone crafting a treasure item", "Someone is wrong position",
    "Someone is loaded a ton of bcn", "Red karma griefing", "Astralis moment"
]


@bot.event
async def on_ready():
  print(f"We logged in as {bot.user}")


@bot.event
async def on_message(message):
  if message.author == bot.user:
    return

  await bot.process_commands(message)


@bot.command()
async def list(ctx, *, question):
  if ctx.channel.name != "khan-bingo":
    await ctx.send("You can only use this command in the khan-bingo channel.")
    return
  if "rb" in question:
    await ctx.send(f"The Red Bloods list is {rbBingoList}")
  elif "co" in question:
    await ctx.send(f"The Coalition list is {coBingoList}")
  else:
    await ctx.send(f"Please specify a list: example !list rb or !list co")


@bot.command()
async def help(ctx):
  help_message = ("!play <rb/co> to join the bingo.\n"
                  "Example: '!play rb' or '!play co'\n"
                  "!list <rb/co> to see the list of all the possibilities.\n"
                  "Example: '!list rb' or '!list co'")
  await ctx.send(help_message)


#https://stackoverflow.com/questions/8257147/wrap-text-in-pil
def get_wrapped_text(text: str, font: ImageFont.ImageFont, line_length: int):
  lines = ['']
  for word in text.split():
    line = f'{lines[-1]} {word}'.strip()
    if font.getlength(line) <= line_length:
      lines[-1] = line
    else:
      lines.append(word)
  return '\n'.join(lines)


@bot.command()
async def play(ctx, *, question):
  if ctx.channel.name != "khan-bingo":
    await ctx.send("You can only use this command in the khan-bingo channel.")
    return
  img = Image.new('RGBA', size=(length, length), color=(120, 120, 120))
  draw = ImageDraw.Draw(img)  #creates a draw object

  for x in range(1, amount):
    draw.rectangle((0, x * offset, length, x * offset + 1), outline=0, fill=1)
    draw.rectangle((x * offset, 0, x * offset + 1, length), outline=0, fill=1)

  randomList = []
  listTypeText = "Invalid List"
  if "rb" in question:
    randomList = random.sample(rbBingoList, 25)
    listTypeText = "Red Bloods"
  elif "co" in question:
    randomList = random.sample(coBingoList, 25)
    listTypeText = "Coalition"
  else:
    await ctx.send("Please specify a list: example '!play rb' or '!play co'")
    return

  for x in range(0, amount):
    for y in range(0, amount):
      #draw.rectangle((x * offset, y * offset, x * offset + offset, y * offset + offset), outline=0, fill=1
      wrappedText = get_wrapped_text(randomList[x * amount + y], bingoFont,
                                     offset - 2 * margin)
      draw.text((margin + x * offset, margin + y * offset),
                wrappedText,
                fill=(255, 255, 255),
                font=bingoFont)

  imgName = f"{ctx.author.name}.PNG"
  img.save(imgName, save_all=True)
  embeddedImage = discord.Embed(
      title=f"{listTypeText} bingo card for {ctx.author.name}")
  embeddedFile = discord.File(imgName, filename=imgName)
  embeddedImage.set_image(url=f"attachment://{imgName}")
  await ctx.send(file=embeddedFile, embed=embeddedImage)


@bot.command()
async def clear(ctx):
  if ctx.channel.name != "khan-bingo":
    await ctx.send("You can only use this command in the khan-bingo channel.")
    return
  if not ctx.author.guild_permissions.manage_messages:
    await ctx.send("You do not have permission to use this command.")
    return
  await ctx.channel.purge(limit=1000)

webserver.keep_alive()
bot.run(token, log_handler=handler, log_level=logging.DEBUG)