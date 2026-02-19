#build 2.3
import discord
from discord.ext import commands
import re
import json
import os
import time
import random
import asyncio
from collections import defaultdict


# ============================================================
#                       LINUX PATHS
# ============================================================
BASE_DIR = "/home/elly/botfolder"

GUILD_CONFIG_FILE = os.path.join(BASE_DIR, "guilds.json")
FACE_FILE = os.path.join(BASE_DIR, "data/faces.txt")
TWINKFACE_FILE = os.path.join(BASE_DIR, "data/twinkface.txt")
WHITELIST_FILE = os.path.join(BASE_DIR, "data/whitelist.txt")
GIF_DIR = os.path.join(BASE_DIR, "gifs")
HOMO_GIF_DIR = os.path.join(BASE_DIR, "gifs/homogifs")
BALLS_IMG = os.path.join(BASE_DIR, "images/balls.png")
DRPEPPER_IMG = os.path.join(BASE_DIR, "images/drpepper.png")

HOMO_WIN_IMG = os.path.join(HOMO_GIF_DIR, "homowin.gif")
HOMO_FAIL_IMG = os.path.join(HOMO_GIF_DIR, "homofail.gif")

BUG_LOG_FILE = os.path.join(BASE_DIR, "buglist.txt")




def has_word(text, word):
    return re.search(rf"(?<!\w){re.escape(word)}(?!\w)", text) is not None


# ============================================================
#                       CONFIG SYSTEM
# ============================================================
if os.path.exists(GUILD_CONFIG_FILE):
    with open(GUILD_CONFIG_FILE, "r") as f:
        guild_config = json.load(f)
else:
    guild_config = {}

def save_guild_config():
    with open(GUILD_CONFIG_FILE, "w") as f:
        json.dump(guild_config, f, indent=4)

def get_guild_config(gid: int):
    gid = str(gid)
    if gid not in guild_config:
        guild_config[gid] = {
            "cooldown": 1,
            "confess_enabled": True,
            "opted_out": []
        }
        save_guild_config()
    return guild_config[gid]

# ============================================================
#                     DISCORD BOT SETUP
# ============================================================
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)
user_cooldowns = defaultdict(lambda: defaultdict(lambda: 0))

# ============================================================
#     LOAD FACE + TWINKFACE + SAFE ZERO-WIDTH CHARACTERS
# ============================================================
SAFE_ZERO_WIDTH = ["\u200b", "\u200c", "\u200d", "\ufe0f"]

with open(FACE_FILE, "r", encoding="utf-8") as f:
    FACES = [line.strip() for line in f if line.strip()]

with open(TWINKFACE_FILE, "r", encoding="utf-8") as f:
    TWINK_FACES = [line.strip() for line in f if line.strip()]

# ============================================================
#     WHITELIST LOADER (patterns or words)
# ============================================================
if os.path.exists(WHITELIST_FILE):
    with open(WHITELIST_FILE, "r", encoding="utf-8") as f:
        WHITELIST_PATTERNS = [line.strip() for line in f if line.strip()]
else:
    WHITELIST_PATTERNS = []

WHITELIST = [re.compile(p) for p in WHITELIST_PATTERNS]

# ============================================================
#   FACE PATTERN BUILDER — NO ZERO-WIDTH CHARACTERS
# ============================================================

def build_unicode_face_pattern(face: str, strict: bool) -> re.Pattern:
    """
    strict=True  → uwu/owo (twinkface.txt), must be standalone
    strict=False → :3 faces (faces.txt), allowed anywhere
    Zero-width characters explicitly blocked.
    """

    # NO ZERO WIDTH CHARACTERS ALLOWED AT ALL.
    # Allowed separators: whitespace, punctuation, symbols.
    SEP = r"(?:[\s\W]{0,10})"

    escaped_parts = [re.escape(ch) for ch in face]
    inner = SEP.join(escaped_parts)

    if strict:
        # uwu/owo must not be inside larger words
        pattern = rf"(?<!\w){inner}(?!\w)"
    else:
        # :3 faces allowed anywhere
        pattern = inner

    return re.compile(pattern, re.IGNORECASE | re.DOTALL)



FACE_PATTERNS = [build_unicode_face_pattern(f, strict=False) for f in FACES]
TWINKFACE_PATTERNS = [build_unicode_face_pattern(f, strict=True) for f in TWINK_FACES]

# ============================================================
#                     EMOJI DETECTION
# ============================================================
TARGET_EMOJI_ID = "1437269389467586601"
EMOJI_ID_REGEX = re.compile(rf"<a?:\w+:{TARGET_EMOJI_ID}>")

# ============================================================
#                  TRIGGER WORDS
# ============================================================

TRIGGER_WORDS = [
    "balls", "penis", "cock",
    "dick", "shaft", "cum",
    "penuts", "peenar", "peenus",
    "weiner", "phalice","peen", "dihh",
    "dih"
]
ATDOOR = [
    "yo mista white someones at the door", "yo mista white someone is at the door",
]
WALTER = [
    "walter", "waltuh", "mr white", "mista white",
]
ASS = [
    "ass", "tiddies",
]
# ============================================================
#                MESSAGE HANDLER
# ============================================================
async def handle_message(message):
    if message.author.bot or not message.guild:
        return

    cfg = get_guild_config(message.guild.id)
    cooldown = cfg["cooldown"]
    opted_out = cfg["opted_out"]

    if message.author.id in opted_out:
        return

    now = time.time()
    last_time = user_cooldowns[message.guild.id][message.author.id]
    if now - last_time < cooldown:
        return

    content = message.content.lower().strip()

    # WHITELIST CHECK
    for w in WHITELIST:
        if w.search(content):
            return

    for word in ATDOOR:
        if has_word(content, word):
            await message.reply("who is it")
            user_cooldowns[message.guild.id][message.author.id] = now
            return

    for word in WALTER:
        if has_word(content, word):
            await message.reply("im waltering it til i white")
            user_cooldowns[message.guild.id][message.author.id] = now
            return

    for word in ASS:
        if has_word(content, word):
            await message.reply("where")
            user_cooldowns[message.guild.id][message.author.id] = now
            return

#FIX THIS ASAP ASHLEY WANTS IT REMOVED BEE HAS THE REPLACEMENT MESSSAGE ENSURE IT IS ALSO SET TO FOR WORD
    if content == "soda":
        await message.reply(
            f"{message.author.mention} i like dr pepper",
            file=discord.File(DRPEPPER_IMG)
        )
        user_cooldowns[message.guild.id][message.author.id] = now
        return

    # Trigger word response
    for word in TRIGGER_WORDS:
        if word in content:
            r1 = random.randint (1,2)
            if r1 == 1:
                await message.reply("yummy")
                user_cooldowns[message.guild.id][message.author.id] = now
                return
            else:
                await message.reply("\U0001F924")
                user_cooldowns[message.guild.id][message.author.id] = now
                return


    # Faces detection
    for pattern in FACE_PATTERNS:
        if pattern.search(content):
            await message.reply(
                f"{message.author.mention} TWINK DETECTED",
                file=discord.File(BALLS_IMG)
            )
            user_cooldowns[message.guild.id][message.author.id] = now
            return

    # Twinkface → GIF
    for pattern in TWINKFACE_PATTERNS:
        if pattern.search(content):
            gif_path = random.choice(os.listdir(GIF_DIR))
            gif_path = os.path.join(GIF_DIR, gif_path)
            embed = discord.Embed(
                description=f"{message.author.mention} TWINK DETECTED",
                color=discord.Color.purple()
            )
            embed.set_image(
                url=f"attachment://{os.path.basename(gif_path)}"
            )
            await message.reply(file=discord.File(gif_path), embed=embed)
            user_cooldowns[message.guild.id][message.author.id] = now
            return

    # emoji ID
    if EMOJI_ID_REGEX.search(content):
        await message.reply(
            f"{message.author.mention} TWINK DETECTED",
            file=discord.File(BALLS_IMG)
        )
        user_cooldowns[message.guild.id][message.author.id] = now
        return

# ============================================================
#                        EVENTS
# ============================================================
@bot.event
async def on_message(message):
    await handle_message(message)
    await bot.process_commands(message)

@bot.event
async def on_message_edit(before, after):
    await handle_message(after)

@bot.event
async def setup_hook():
    await bot.tree.sync()
    print("Slash commands synced.")

# ============================================================
#                     ADMIN COMMANDS
# ============================================================
@bot.tree.command(name="setcooldown", description="Admin: set cooldown for THIS server")
async def set_cooldown(interaction: discord.Interaction, seconds: float):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("Admin only.", ephemeral=True)

    cfg = get_guild_config(interaction.guild_id)
    cfg["cooldown"] = max(0, seconds)
    save_guild_config()

    await interaction.response.send_message(
        f"Cooldown set to **{seconds} seconds**.",
        ephemeral=True
    )

@bot.tree.command(name="toggleconfess", description="Admin: enable/disable /confess")
async def toggle_confess(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("Admin only.", ephemeral=True)

    cfg = get_guild_config(interaction.guild_id)
    cfg["confess_enabled"] = not cfg["confess_enabled"]
    save_guild_config()

    state = "ENABLED ✅" if cfg["confess_enabled"] else "DISABLED ❌"
    await interaction.response.send_message(f"`/confess` is now **{state}**.", ephemeral=True)

@bot.tree.command(name="imnotgayiswear", description="Opt out of twink detection")
async def opt_out(interaction: discord.Interaction):
    cfg = get_guild_config(interaction.guild_id)
    if interaction.user.id not in cfg["opted_out"]:
        cfg["opted_out"].append(interaction.user.id)
        save_guild_config()
    await interaction.response.send_message("You are now opted out.", ephemeral=True)

@bot.tree.command(name="nvm_im_gay", description="Opt back in")
async def opt_in(interaction: discord.Interaction):
    cfg = get_guild_config(interaction.guild_id)
    if interaction.user.id in cfg["opted_out"]:
        cfg["opted_out"].remove(interaction.user.id)
        save_guild_config()
    await interaction.response.send_message("You are opted in again.", ephemeral=True)

# ============================================================
#                 CONFESS COMMAND (FULL VERSION)
# ============================================================
CONFESS_TEXT = """My name is Walter Hartwell White. I live at 308 Negra Arroyo Lane, Albuquerque, New Mexico, 87104. This is my confession. If you're watching this tape, I'm probably dead, murdered by my brother-in-law Hank Schrader. Hank has been building a meth empire for over a year now and using me as his chemist. Shortly after my 50th birthday, Hank came to me with a rather, shocking proposition. He asked that I use my chemistry knowledge to cook methamphetamine, which he would then sell using his connections in the drug world. Connections that he made through his career with the DEA. I was... astounded, I... I always thought that Hank was a very moral man and I was... thrown, confused, but I was also particularly vulnerable at the time, something he knew and took advantage of. I was reeling from a cancer diagnosis that was poised to bankrupt my family. Hank took me on a ride along, and showed me just how much money even a small meth operation could make. And I was weak. I didn't want my family to go into financial ruin so I agreed. Every day, I think back at that moment with regret. I quickly realized that I was in way over my head, and Hank had a partner, a man named Gustavo Fring, a businessman. Hank essentially sold me into servitude to this man, and when I tried to quit, Fring threatened my family. I didn't know where to turn. Eventually, Hank and Fring had a falling out. From what I can gather, Hank was always pushing for a greater share of the business, to which Fring flatly refused to give him, and things escalated. Fring was able to arrange, uh I guess I guess you call it a "hit" on my brother-in-law, and failed, but Hank was seriously injured, and I wound up paying his medical bills which amounted to a little over $177,000. Upon recovery, Hank was bent on revenge, working with a man named Hector Salamanca, he plotted to kill Fring, and did so. In fact, the bomb that he used was built by me, and he gave me no option in it.."""

@bot.tree.command(name="confess", description="Walter White confession")
async def confess(interaction: discord.Interaction):
    cfg = get_guild_config(interaction.guild_id)
    if not cfg["confess_enabled"]:
        return await interaction.response.send_message("❌ This command is disabled.", ephemeral=True)

    await interaction.response.send_message(CONFESS_TEXT)

# ============================================================
#                 CAST HOMOSEXUALITY COMMAND
# ============================================================
@bot.tree.command(
    name="casthomosexuality",
    description="Roll a D20 to cast homosexuality on your friends"
)
async def casthomosexuality(interaction: discord.Interaction):

    roll = random.randint(1, 20)

    if roll > 9:
        image_path = HOMO_WIN_IMG
        text = f"You rolled **{roll}**.\nhomosexuality hath been casted"
    else:
        image_path = HOMO_FAIL_IMG
        text = f"You rolled **{roll}**.\nSpell failed :("

    embed = discord.Embed(
        title="Cast Homosexuality",
        description=text,
        color=discord.Color.purple()
    )
    embed.set_image(url=f"attachment://{os.path.basename(image_path)}")

    await interaction.response.send_message(
        embed=embed,
        file=discord.File(image_path)
    )


# ============================================================
#                     BUG REPORT SYSTEM
# ============================================================
@bot.tree.context_menu(name="Report Bug")
async def bug_context(interaction: discord.Interaction, message: discord.Message):

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    log_entry = (
        f"\n=== BUG REPORT ===\n"
        f"Date: {timestamp}\n"
        f"Guild: {interaction.guild_id}\n"
        f"Channel: {interaction.channel_id}\n"
        f"Reporter: {interaction.user.id}\n"
        f"Original Author: {message.author.id}\n"
        f"Message: {message.content}\n"
        f"===================\n"
    )

    with open(BUG_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry)

    await interaction.response.send_message("Bug logged — thank you :3", ephemeral=True)

# ============================================================
#                     START BOT
# ============================================================
bot.run("MTQ0MTI0NjQwNzQwMjA2NjA1MQ.GkUVsU.X8RHncTaTIL1n8x_pDPNAArUjPsdp7MLCqsgho")


# ============================================================
#                    DISCORD.PY CHEAT SHEET
#        (A quick guide to everything used in this bot)
# ============================================================

# -----------------------------
# 1)  Intents
# -----------------------------
# Discord requires bots to *request permission* for what they can see.
# Without message_content=True the bot cannot read messages at all.

# -----------------------------
# 2)  Bot Creation
# -----------------------------
# bot = commands.Bot(prefix, intents)
# Creates the bot and enables slash commands, message commands, etc.

# -----------------------------
# 3)  Slash Commands (@bot.tree.command)
# -----------------------------
# Modern Discord commands:
#
# @bot.tree.command(name="example")
# async def example(interaction):
#     await interaction.response.send_message("Hello")
#
# - Always respond within 3 seconds or defer()
# - You CANNOT read replied messages from slash commands.

# -----------------------------
# 4)  Defer + Followup
# -----------------------------
# Use this if the bot needs time (e.g., dice roll):
#
# await interaction.response.defer()
# await asyncio.sleep(1)
# await interaction.followup.send("Done")
#
# Prevents the “This interaction failed” error.

# -----------------------------
# 5)  Message Events (on_message)
# -----------------------------
# Fires every time ANY message is sent.
#
# Use this for:
# - auto replies
# - filters
# - triggers
# - logging
# - twink detector
#
# MUST include:
# await bot.process_commands(message)
# or else slash commands break.

# -----------------------------
# 6)  message.reply()
# -----------------------------
# Replies directly to a message.
#
# await message.reply("hi")
#
# Maintains threading and mentions the author.

# -----------------------------
# 7)  Embeds
# -----------------------------
# Fancy Discord messages.
#
# embed = discord.Embed(title="Hello", description="desc", color=...)
# embed.set_image(url="attachment://file.png")
# await message.reply(embed=embed)

# -----------------------------
# 8)  Sending Files
# -----------------------------
# discord.File("path") attaches local images/gifs.
#
# await interaction.followup.send(file=discord.File(path))

# -----------------------------
# 9)  Random Numbers
# -----------------------------
# random.randint(a, b) → used for dice rolls.

# -----------------------------
# 10)  AsyncIO (Delays)
# -----------------------------
# await asyncio.sleep(1)
# Non-blocking pause. The bot stays alive while waiting.

# -----------------------------
# 11)  Time (Timestamps)
# -----------------------------
# time.time() → cooldowns
# time.strftime(...) → readable dates for bug logs.

# -----------------------------
# 12)  Server Config (guild_config)
# -----------------------------
# A JSON file that stores settings PER SERVER.
# Example:
# {
#   "guild_id": {
#       "cooldown": 1,
#       "confess_enabled": true,
#       "opted_out": [userid, userid]
#   }
# }

# -----------------------------
# 13)  Cooldowns
# -----------------------------
# user_cooldowns[guild][user] = timestamp
# Prevents spam by checking how long since last auto-reply.

# -----------------------------
# 14)  Regex (re.compile)
# -----------------------------
# Used for:
# - detecting uwu/owo style faces
# - detecting disguised faces
# - emoji ID triggers
#
# pattern.search(msg_content) → True/False

# -----------------------------
# 15)  Whitelist System
# -----------------------------
# Regex patterns loaded from whitelist.txt
# If any match → message is ignored by detectors.
#
# Good for stopping false positives on:
# - timestamps (3:30)
# - URLs
# - common words
# - custom bypasses

# -----------------------------
# 16)  Context Menu Commands
# -----------------------------
# @bot.tree.context_menu(name="Report Bug")
#
# These appear in Discord when right-clicking a message.
# Useful for bug reporting, moderation, etc.

# -----------------------------
# 17)  Reply-Based Bug Logging
# -----------------------------
# If a user replies to a message and types "bug",
# this bot records:
# - timestamp
# - guild
# - channel
# - reporter ID
# - original author ID
# - original message content
#
# Saves into buglist.txt

# -----------------------------
# 18)  File Paths
# -----------------------------
# All bot assets (faces.txt, gifs, whitelist.txt, etc.)
# are stored on your Linux server under BASE_DIR.
#
# Good for:
# - organizing images
# - adding new detection faces
# - adding new whitelist patterns

# -----------------------------
# 19)  Opt-Out System
# -----------------------------
# Lets users disable twink detection for themselves:
# - /imnotgayiswear → opt out
# - /nvm_im_gay → opt back in

# -----------------------------
# 20)  Starting the Bot
# -----------------------------
# bot.run("TOKEN")
# Connects to Discord’s servers and goes live.

# ============================================================
#                     END OF CHEAT SHEET
# ============================================================

