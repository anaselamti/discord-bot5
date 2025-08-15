import discord
from discord.ext import commands
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import traceback
from datetime import datetime
import asyncio

# Server settings
chromedriver_path = "/usr/local/bin/chromedriver"
chrome_binary_path = "/usr/local/chrome-linux/chrome"
base_url = "https://ffs.gg/statistics.php"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ------------------ Helper Functions ------------------

def extract_between(text, start, end):
    try:
        return text.split(start)[1].split(end)[0].strip()
    except IndexError:
        return "❌ Not Available"

def scrape_player(player_name):
    options = webdriver.ChromeOptions()
    options.binary_location = chrome_binary_path
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(base_url)
        search_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input.searchField"))
        )
        search_field.send_keys(player_name)
        search_field.send_keys(Keys.RETURN)
        time.sleep(3)

        row = driver.find_element(By.CSS_SELECTOR, "table.stats tbody tr")
        profile_link = row.find_element(By.CSS_SELECTOR, "td a").get_attribute("href")

        if "member.php" in profile_link:
            user_id = profile_link.split("u=")[1].split("&")[0]
            profile_url = f"https://ffs.gg/members/{user_id}-{player_name}"
        else:
            profile_url = profile_link.replace("member.php", "members")

        driver.get(profile_url)
        time.sleep(5)

        try:
            clan_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    "//div[contains(@class,'ww_box') and contains(@class,'profileStats')]//div[contains(text(),'Clan')]/span/b/a"
                ))
            )
            clan = clan_element.text.strip()
        except:
            clan = "❌ No Clan"

        body_text = driver.find_element(By.TAG_NAME, "body").text

        return {
            "name": extract_between(body_text, "Member List", "Log in").split()[-1],
            "clan": clan,
            "country": extract_between(body_text, "Country", "Last Visit"),
            "join_date": extract_between(body_text, "last seen", "join date"),
            "points": extract_between(body_text, "CarBall", "Won").split()[0],
            "wins": extract_between(body_text, "Won:", "|").split()[0],
            "goals": extract_between(body_text, "Goals:", "|").split()[0],
            "assists": extract_between(body_text, "Assists:", "Saves").split()[0],
            "saves": extract_between(body_text, "Saves:", "|").split()[0],
            "profile_url": profile_url
        }

    except Exception as e:
        print(traceback.format_exc())
        return None
    finally:
        driver.quit()

def progress_bar(val, max_val=100, length=15):
    ratio = min(int((val / max_val) * length), length)
    return "█" * ratio + "░" * (length - ratio)

def get_embed_color(p1_adv, p2_adv):
    if p1_adv > p2_adv:
        return 0xffd700  # ذهبي
    elif p2_adv > p1_adv:
        return 0x1e90ff  # أزرق
    else:
        return 0x8a2be2  # بنفسجي

def get_thumbnail(p1_adv, p2_adv):
    if p1_adv > p2_adv:
        return "https://i.imgur.com/GoldTrophy.png"
    elif p2_adv > p1_adv:
        return "https://i.imgur.com/BlueTrophy.png"
    else:
        return "https://i.imgur.com/EqualBalance.png"

# ------------------ Comparison Embed ------------------

def create_legendary_comparison(p1, p2):
    def to_int(val):
        try:
            return int(val.replace(",", ""))
        except:
            return 0

    stats = [
        ("🏆 CarBall Points", "points", 2000),
        ("⚔️ Wins", "wins", 100),
        ("⚽ Goals", "goals", 500),
        ("🎯 Assists", "assists", 300),
        ("🛡️ Saves", "saves", 200)
    ]

    comparisons = []
    p1_advantages = 0
    p2_advantages = 0

    for stat in stats:
        p1_val = to_int(p1[stat[1]])
        p2_val = to_int(p2[stat[1]])
        diff = p1_val - p2_val

        if diff > 0:
            p1_advantages += 1
            emoji = "✨"
            comparison = f"{p1['name']} leads by **{diff}** {stat[2]}(s)"
        elif diff < 0:
            p2_advantages += 1
            emoji = "💫"
            comparison = f"{p2['name']} leads by **{abs(diff)}** {stat[2]}(s)"
        else:
            emoji = "⚖️"
            comparison = "Exactly equal!"

        comparisons.append(
            f"{emoji} **{stat[0]}**\n"
            f"{p1['name']}: {progress_bar(p1_val, stat[2])} `{p1_val}`\n"
            f"{p2['name']}: {progress_bar(p2_val, stat[2])} `{p2_val}`\n"
            f"**{comparison}**\n"
        )

    embed_color = get_embed_color(p1_advantages, p2_advantages)
    embed_thumbnail = get_thumbnail(p1_advantages, p2_advantages)

    embed = discord.Embed(
        title=f"⚡ Legendary Comparison: {p1['name']} vs {p2['name']} ⚡",
        description="\n".join(comparisons),
        color=embed_color
    )

    if p1_advantages > p2_advantages:
        result = f"🔥 {p1['name']} leads in {p1_advantages} stats!"
    elif p2_advantages > p1_advantages:
        result = f"🌪️ {p2['name']} leads in {p2_advantages} stats!"
    else:
        result = "⚖️ Both players are equally strong!"

    embed.add_field(name="🎖️ Final Result", value=result, inline=False)
    embed.add_field(
        name="📌 Player Info",
        value=f"• {p1['name']} ({p1['clan']}) | [Profile]({p1['profile_url']})\n"
              f"• {p2['name']} ({p2['clan']}) | [Profile]({p2['profile_url']})",
        inline=False
    )
    embed.set_thumbnail(url=embed_thumbnail)
    embed.set_footer(text=f"⌛ Comparison done at {datetime.now().strftime('%Y/%m/%d %H:%M:%S')} | Made with ⚡ Power")

    return embed

# ------------------ Commands ------------------

@bot.command(name="ffs")
async def player_stats(ctx, player_name: str = None):
    if not player_name:
        return await ctx.send("⚠️ Please provide a player name! Example: `!ffs player_name`")
    
    msg = await ctx.send(f"🔎 Searching for {player_name}...")
    await asyncio.sleep(1.5)

    data = scrape_player(player_name)
    if not data:
        return await msg.edit(content="❌ Could not find this player!")

    def to_int(val):
        try:
            return int(val.replace(",", ""))
        except:
            return 0

    stats = [
        ("🏆 CarBall Points", "points", 2000),
        ("⚔️ Wins", "wins", 100),
        ("⚽ Goals", "goals", 500),
        ("🎯 Assists", "assists", 300),
        ("🛡️ Saves", "saves", 200)
    ]

    embed = discord.Embed(
        title=f"📊 Stats for {data['name']}",
        color=0x3498db,
        url=data["profile_url"]
    )

    embed.add_field(name="🏷️ Clan", value=data["clan"], inline=True)
    embed.add_field(name="🌍 Country", value=data["country"], inline=True)
    embed.add_field(name="📅 Join Date", value=data["join_date"], inline=True)

    # Add progress bars for stats
    for stat in stats:
        val = to_int(data[stat[1]])
        embed.add_field(
            name=stat[0],
            value=f"{progress_bar(val, stat[2])} `{val}`",
            inline=False
        )

    embed.add_field(name="🔗 Profile", value=f"[Click Here]({data['profile_url']})", inline=False)
    embed.set_thumbnail(url="https://i.imgur.com/Jr6Q2bX.png")
    await msg.edit(content=None, embed=embed)

@bot.command(name="compare")
async def compare_players(ctx, player1: str = None, player2: str = None):
    if not player1 or not player2:
        return await ctx.send("⚠️ Please provide two player names! Example: `!compare player1 player2`")

    msg = await ctx.send(f"⚡ Preparing legendary comparison: **{player1}** vs **{player2}**...")

    loading_msgs = ["🔎 Searching players...", "⚡ Gathering stats...", "🚀 Almost ready..."]
    for text in loading_msgs:
        await msg.edit(content=text)
        await asyncio.sleep(1.5)

    p1_data = scrape_player(player1)
    if not p1_data:
        return await msg.edit(content=f"❌ Could not find player {player1}")

    await msg.edit(content=f"🔍 Gathering data for {player2}...")
    await asyncio.sleep(1.5)

    p2_data = scrape_player(player2)
    if not p2_data:
        return await msg.edit(content=f"❌ Could not find player {player2}")

    comparison_embed = create_legendary_comparison(p1_data, p2_data)
    await msg.edit(content=None, embed=comparison_embed)

@bot.command(name="help")
async def help_command(ctx):
    embed = discord.Embed(
        title="🎮 Help Center - Free Fire Stats Bot",
        description="**Available Commands:**",
        color=0x7289da
    )
    
    embed.add_field(name="`!ffs <player_name>`", value="Show full stats of the player", inline=False)
    embed.add_field(name="`!compare <player1> <player2>`", value="Legendary comparison between two players", inline=False)
    embed.add_field(name="`!help`", value="Display this help message", inline=False)
    
    embed.set_thumbnail(url="https://i.imgur.com/vZ7vQ3a.png")
    embed.set_footer(text="Bot Developer: [Your Name]")
    await ctx.send(embed=embed)

bot.run(os.getenv("DISCORD_BOT_TOKEN"))
