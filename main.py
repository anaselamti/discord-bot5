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
import matplotlib.pyplot as plt
import io
import asyncio
from concurrent.futures import ThreadPoolExecutor

# ------------------- إعداد Selenium -------------------
chromedriver_path = "/usr/local/bin/chromedriver"
chrome_binary_path = "/usr/local/chrome-linux/chrome"
base_url = "https://ffs.gg/statistics.php"

# ------------------- إعداد Discord Bot -------------------
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ThreadPool لتشغيل Selenium بشكل آمن بدون تجميد البوت
executor = ThreadPoolExecutor(max_workers=3)

# ------------------- دوال مساعدة -------------------
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
        time.sleep(2)  # تقليل الوقت لتسريع البوت

        row = driver.find_element(By.CSS_SELECTOR, "table.stats tbody tr")
        profile_link = row.find_element(By.CSS_SELECTOR, "td a").get_attribute("href")

        if "member.php" in profile_link:
            user_id = profile_link.split("u=")[1].split("&")[0]
            profile_url = f"https://ffs.gg/members/{user_id}-{player_name}"
        else:
            profile_url = profile_link.replace("member.php", "members")

        driver.get(profile_url)
        time.sleep(2)

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
        join_date = extract_between(body_text, "last seen", "join date")
        country = extract_between(body_text, "Country", "Last Visit")
        carball_points = extract_between(body_text, "CarBall", "Won").split()[0]
        winning_games = extract_between(body_text, "Won:", "|").split()[0]
        scored_goals = extract_between(body_text, "Goals:", "|").split()[0]
        assists = extract_between(body_text, "Assists:", "Saves").split()[0]
        saved_gk = extract_between(body_text, "Saves:", "|").split()[0]

        result_text = (
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

        return result_text

    except Exception as e:
        print(traceback.format_exc())
        return f"❌ An error occurred: {str(e)}"

    finally:
        driver.quit()

async def scrape_player_async(player_name):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(executor, scrape_player, player_name)

# ------------------- أوامر البوت -------------------
@bot.command(name="ffs")
async def ffs(ctx, player_name: str = None):
    if not player_name:
        await ctx.send("❌ Please provide the player name. Example: `!ffs anasmorocco`")
        return

    await ctx.send(f"🔍 Searching for player **{player_name}**... This may take a few seconds.")
    result = await scrape_player_async(player_name)
    await ctx.send(result)

@bot.command(name="compare")
async def compare(ctx, player1: str = None, player2: str = None):
    if not player1 or not player2:
        await ctx.send("❌ Please provide two player names. Example: `!compare anasmorocco wassym`")
        return

    await ctx.send(f"🔍 Comparing **{player1}** and **{player2}**... Please wait.")

    result1, result2 = await asyncio.gather(
        scrape_player_async(player1),
        scrape_player_async(player2)
    )

    if result1.startswith("❌") or result2.startswith("❌"):
        await ctx.send("⚠️ Could not fetch one or both players' data.")
        return

    def extract_stat(text, label):
        for line in text.split("\n"):
            if line.startswith(label):
                value = line.split(":")[1].strip().split()[0]
                try:
                    return int(value)
                except ValueError:
                    return 0
        return 0

    stats_labels = ["🏆 CarBall Points", "🎯 Wins", "⚽ Goals", "🎖 Assists", "🧤 Saves"]
    player1_stats = [extract_stat(result1, label) for label in stats_labels]
    player2_stats = [extract_stat(result2, label) for label in stats_labels]

    # ------------------- رسم المبيان الاحترافي -------------------
    plt.style.use('dark_background')
    colors = ['#1f77b4', '#ff7f0e']
    fig, ax = plt.subplots(figsize=(10,6))
    x = range(len(stats_labels))
    ax.bar([i-0.2 for i in x], player1_stats, width=0.4, label=player1, color=colors[0])
    ax.bar([i+0.2 for i in x], player2_stats, width=0.4, label=player2, color=colors[1])
    ax.set_xticks(x)
    ax.set_xticklabels(stats_labels, rotation=25, fontsize=12)
    ax.set_ylabel("Values", fontsize=12)
    ax.set_title(f"📊 {player1} vs {player2}", fontsize=14, fontweight='bold')
    ax.legend()
    plt.tight_layout()

    img_bytes = io.BytesIO()
    plt.savefig(img_bytes, format='png')
    img_bytes.seek(0)
    plt.close()

    file = discord.File(img_bytes, filename="comparison.png")
    await ctx.send(file=file)

@bot.command(name="info")
async def info(ctx):
    await ctx.send("Use `!ffs <player_name>` to get player stats.\nUse `!compare <player1> <player2>` to compare players.")

# ------------------- تشغيل البوت -------------------
bot.run(os.getenv("DISCORD_BOT_TOKEN"))
