import discord
from discord.ext import commands, tasks
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import asyncio
import time
import os
import traceback

# --- Settings ---
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHROMEDRIVER_PATH = "/usr/local/bin/chromedriver"
CHROME_BINARY_PATH = "/usr/local/chrome-linux/chrome"
BASE_URL_PLAYER = "https://ffs.gg/statistics.php"
CLAN_URL = "https://ffs.gg/clans.php?clanid=2915"
CLAN_CHANNEL_ID = 1404474899564597308  # الروم الخاص بالكلان

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

last_clan_message_id = None

# --- Helper Functions ---
def extract_between(text, start, end):
    try:
        return text.split(start)[1].split(end)[0].strip()
    except IndexError:
        return "Not found"

def create_chrome_driver(headless=True):
    options = webdriver.ChromeOptions()
    options.binary_location = CHROME_BINARY_PATH
    if headless:
        options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    service = Service(CHROMEDRIVER_PATH)
    return webdriver.Chrome(service=service, options=options)

# --- Player Scraper ---
def scrape_player(player_name):
    driver = create_chrome_driver()
    try:
        driver.get(BASE_URL_PLAYER)
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

        return (
            f"🎮 **Player Profile: {username}**\n"
            f"👥 Clan: {clan}\n"
            f"🌍 Country: {country}\n"
            f"📅 Join Date: {join_date}\n"
            f"🏆 CarBall Points: {carball_points}\n"
            f"🎯 Wins: {winning_games}\n"
            f"⚽ Goals: {scored_goals}\n"
            f"🎖 Assists: {assists}\n"
            f"🧤 Saves: {saved_gk}\n"
            f"🔗 [Full Profile]({profile_url})"
        )
    except Exception as e:
        print(traceback.format_exc())
        return f"❌ An error occurred: {str(e)}"
    finally:
        driver.quit()

# --- Clan Scraper ---
def scrape_clan_status():
    driver = create_chrome_driver()
    clan_data = {
        "name": "Goalacticos",
        "description": "No description available",
        "tag": "Gs_",
        "members": "0",
        "clan_wars": "0",
        "ranked": "0 - 0W - 0L",
        "unranked": "0",
        "win_ratio": "0%",
        "bank": "$0",
        "online_players": []
    }

    try:
        driver.get(CLAN_URL)
        wait = WebDriverWait(driver, 15)

        # Members
        try:
            members_element = driver.find_element(By.CSS_SELECTOR, ".wwClanInfo:nth-child(3) div b")
            clan_data["members"] = members_element.text.strip()
        except NoSuchElementException:
            pass

        # Online players
        try:
            player_rows = driver.find_elements(By.CSS_SELECTOR, "table.fullwidth.dark.stats.clan tbody tr:not(.spacer)")
            clan_data["online_players"] = []
            for row in player_rows:
                try:
                    username = row.find_element(By.CSS_SELECTOR, "td:nth-child(2) a span").text.strip()
                    server_status = row.find_element(By.CSS_SELECTOR, "td:nth-child(5)").text.strip()
                    if "Online" in server_status:
                        clan_data["online_players"].append(username)
                except NoSuchElementException:
                    continue
            clan_data["members"] = str(len(player_rows))
        except NoSuchElementException:
            pass

        return clan_data
    finally:
        driver.quit()

# --- Commands ---
@bot.command(name="ffs")
async def ffs(ctx, player_name: str = None, arena: str = None):
    if not player_name:
        await ctx.send("❌ Please provide the player name. Example: `!ffs anasmorocco cb`")
        return

    await ctx.send(f"🔍 Searching for player **{player_name}**... This may take a few seconds.")
    result = await asyncio.to_thread(scrape_player, player_name)
    await ctx.send(result)

@bot.command(name="clan")
async def clan(ctx):
    await ctx.send("🔍 Fetching clan status... This may take a few seconds.")
    clan_data = await asyncio.to_thread(scrape_clan_status)

    online_count = len(clan_data["online_players"])
    members_count = clan_data["members"]
    online_list = ", ".join(clan_data["online_players"]) if online_count > 0 else "No players are currently online."

    embed = discord.Embed(
        title=f"🛡️ {clan_data['name']} [{clan_data['tag']}]",
        description=clan_data["description"],
        color=0xdaa520
    )
    embed.add_field(
        name="📊 Clan Statistics",
        value=(
            f"👥 Members: {members_count}\n"
            f"⚔️ Clan Wars: {clan_data['clan_wars']}\n"
            f"🏆 Ranked: {clan_data['ranked']}\n"
            f"🔓 Unranked: {clan_data['unranked']}\n"
            f"📈 Win Ratio: {clan_data['win_ratio']}\n"
            f"💰 Bank Balance: {clan_data['bank']}"
        ),
        inline=False
    )
    embed.add_field(
        name=f"👤 Members Online ({online_count}/{members_count})",
        value=online_list,
        inline=False
    )

    await ctx.send(embed=embed)

@bot.command(name="info")
async def info(ctx):
    await ctx.send("Use `!ffs <player_name> <mode>` to get player stats or `!clan` to see clan status.")

# --- Bot Startup ---
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")

bot.run(DISCORD_BOT_TOKEN)
