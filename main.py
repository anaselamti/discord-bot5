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

chromedriver_path = "/usr/local/bin/chromedriver"
chrome_binary_path = "/usr/local/chrome-linux/chrome"
base_url = "https://ffs.gg/statistics.php"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

def extract_between(text, start, end):
    try:
        return text.split(start)[1].split(end)[0].strip()
    except IndexError:
        return "Not found"

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
            clan = "Unknown"

        body_text = driver.find_element(By.TAG_NAME, "body").text

        username = extract_between(body_text, "Member List", "Log in").split()[-1]
        nickname = extract_between(body_text, "Name", "Clan")
        join_date = extract_between(body_text, "last seen", "join date")
        country = extract_between(body_text, "Country", "Last Visit")
        carball_points = extract_between(body_text, "CarBall", "Won").split()[0]
        winning_games = extract_between(body_text, "Won:", "|").split()[0]
        scored_goals = extract_between(body_text, "Goals:", "|").split()[0]
        assists = extract_between(body_text, "Assists:", "Saves").split()[0]
        saved_gk = extract_between(body_text, "Saves:", "|").split()[0]

        return {
            "username": username,
            "clan": clan,
            "country": country,
            "join_date": join_date,
            "carball_points": carball_points,
            "winning_games": winning_games,
            "scored_goals": scored_goals,
            "assists": assists,
            "saved_gk": saved_gk,
            "profile_url": profile_url
        }

    except Exception as e:
        print(traceback.format_exc())
        return None

    finally:
        driver.quit()

def create_comparison_embed(player1_data, player2_data):
    embed = discord.Embed(
        title="⚔️ Player Comparison",
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )
    
    # Player 1 info
    p1_field = (
        f"👥 Clan: {player1_data['clan']}\n"
        f"🌍 Country: {player1_data['country']}\n"
        f"📅 Join Date: {player1_data['join_date']}\n"
        f"🔗 [Profile]({player1_data['profile_url']})"
    )
    
    # Player 2 info
    p2_field = (
        f"👥 Clan: {player2_data['clan']}\n"
        f"🌍 Country: {player2_data['country']}\n"
        f"📅 Join Date: {player2_data['join_date']}\n"
        f"🔗 [Profile]({player2_data['profile_url']})"
    )
    
    embed.add_field(name=f"🎮 {player1_data['username']}", value=p1_field, inline=True)
    embed.add_field(name=f"🆚", value="**VS**", inline=True)
    embed.add_field(name=f"🎮 {player2_data['username']}", value=p2_field, inline=True)
    
    # Stats comparison
    stats_fields = [
        ("🏆 CarBall Points", "carball_points", False),
        ("🎯 Wins", "winning_games", False),
        ("⚽ Goals", "scored_goals", True),
        ("🎖 Assists", "assists", True),
        ("🧤 Saves", "saved_gk", True)
    ]
    
    for stat_name, stat_key, show_difference in stats_fields:
        p1_val = player1_data.get(stat_key, "0")
        p2_val = player2_data.get(stat_key, "0")
        
        try:
            p1_num = int(p1_val.replace(",", ""))
            p2_num = int(p2_val.replace(",", ""))
            
            if show_difference:
                diff = p1_num - p2_num
                if diff > 0:
                    diff_str = f"(+{diff})"
                elif diff < 0:
                    diff_str = f"({diff})"
                else:
                    diff_str = "(=)"
                
                value = f"`{p1_val}` {diff_str} `{p2_val}`"
            else:
                value = f"`{p1_val}` vs `{p2_val}`"
            
            embed.add_field(name=stat_name, value=value, inline=True)
            
        except ValueError:
            embed.add_field(name=stat_name, value=f"`{p1_val}` vs `{p2_val}`", inline=True)
    
    embed.set_footer(text="Comparison made at")
    return embed

@bot.command(name="ffs")
async def ffs(ctx, player_name: str = None, arena: str = None):
    if not player_name:
        await ctx.send("❌ Please provide the player name. Example: `!ffs anasmorocco cb`")
        return

    await ctx.send(f"🔍 Searching for player **{player_name}**... This may take a few seconds.")

    result = scrape_player(player_name)
    if isinstance(result, dict):
        response = (
            f"🎮 **Player Profile: {result['username']}**\n"
            f"👥 Clan: {result['clan']}\n"
            f"🌍 Country: {result['country']}\n"
            f"📅 Join Date: {result['join_date']}\n"
            f"🏆 CarBall Points: {result['carball_points']}\n"
            f"🎯 Wins: {result['winning_games']}\n"
            f"⚽ Goals: {result['scored_goals']}\n"
            f"🎖 Assists: {result['assists']}\n"
            f"🧤 Saves: {result['saved_gk']}\n"
            f"🔗 [Full Profile]({result['profile_url']})"
        )
        await ctx.send(response)
    else:
        await ctx.send(result)

@bot.command(name="compare")
async def compare_players(ctx, player1: str = None, player2: str = None):
    if not player1 or not player2:
        await ctx.send("❌ Please provide two player names. Example: `!compare player1 player2`")
        return
    
    # Send initial message
    msg = await ctx.send(f"⚔️ Preparing comparison between **{player1}** and **{player2}**...")
    
    # Scrape first player with delay
    await msg.edit(content=f"🔍 Searching for **{player1}**... (1/2)")
    player1_data = scrape_player(player1)
    time.sleep(2)  # Delay between requests
    
    # Scrape second player
    await msg.edit(content=f"🔍 Searching for **{player2}**... (2/2)")
    player2_data = scrape_player(player2)
    
    # Check if both players were found
    if not player1_data or not player2_data:
        error_msg = "❌ Could not find data for one or both players. Please check the names and try again."
        await msg.edit(content=error_msg)
        return
    
    # Create and send comparison embed
    embed = create_comparison_embed(player1_data, player2_data)
    await msg.edit(content=None, embed=embed)

@bot.command(name="info")
async def info(ctx):
    help_text = (
        "**🤖 Bot Commands:**\n"
        "`!ffs <player_name>` - Get player stats\n"
        "`!compare <player1> <player2>` - Compare two players\n"
        "`!info` - Show this help message\n\n"
        "**Examples:**\n"
        "`!ffs anasmorocco`\n"
        "`!compare player1 player2`"
    )
    await ctx.send(help_text)

bot.run(os.getenv("DISCORD_BOT_TOKEN"))
