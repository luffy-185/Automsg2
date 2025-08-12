import os
import asyncio
import random
import time
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from keep_alive import keep_alive  # import your flask keep-alive module

# ===== CONFIG =====
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
SESSION = os.environ.get("SESSION", "")
PHONE = os.environ.get("PHONE", None)  # optional, if you want

TARGET_CHAT = os.environ.get("TARGET_CHAT", "@noob_grabbers")
COMMAND_TEXT = os.environ.get("COMMAND_TEXT", "/explore@slave_waifu_bot")
OWNER = os.environ.get("OWNER", "lazy_luffy")

# ===== STATE =====
delay = 66
random_delay = False
sent_count = 0
start_time = time.time()
running = True

client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)

# ===== UTILS =====
async def is_owner(event):
    sender = await event.get_sender()
    return (sender.username or "").lower() == OWNER.lower()

def format_uptime():
    uptime = int(time.time() - start_time)
    hrs = uptime // 3600
    mins = (uptime % 3600) // 60
    secs = uptime % 60
    return f"{hrs}h {mins}m {secs}s"

# ===== SPAM LOOP =====
async def spam_loop():
    global sent_count
    while True:
        if running:
            await client.send_message(TARGET_CHAT, COMMAND_TEXT)
            sent_count += 1
        wait_time = random.randint(65, 70) if random_delay else delay
        await asyncio.sleep(wait_time)

# ===== COMMANDS =====
@client.on(events.NewMessage(pattern=r"^/delay (.+)$"))
async def change_delay(event):
    global delay, random_delay
    if not await is_owner(event): return
    arg = event.pattern_match.group(1).strip().lower()
    if arg == "random":
        random_delay = True
        await event.reply("✅ Delay set to random between 65–70 seconds.")
    else:
        try:
            sec = float(arg)
            delay = sec
            random_delay = False
            await event.reply(f"✅ Delay set to {delay} seconds.")
        except ValueError:
            await event.reply("❌ Invalid delay. Use /delay <seconds> or /delay random.")

@client.on(events.NewMessage(pattern=r"^/status$"))
async def status(event):
    if not await is_owner(event): return
    delay_info = "Random (65–70s)" if random_delay else f"{delay}s"
    await event.reply(
        f"📊 Bot Status\n"
        f"Uptime: {format_uptime()}\n"
        f"Messages Sent: {sent_count}\n"
        f"Delay: {delay_info}"
    )

@client.on(events.NewMessage(pattern=r"^/help$"))
async def help_cmd(event):
    if not await is_owner(event): return
    await event.reply(
        "📜 Commands:\n"
        "/delay <seconds> → Set fixed delay\n"
        "/delay random → Set random delay between 65–70s\n"
        "/status → Show uptime & sent count\n"
        "/help → Show this help message"
    )

# ===== STARTUP =====
async def main():
    await client.start(phone=PHONE)
    if not await client.is_user_authorized():
        print("⚠️ Not authorized. Check your SESSION and PHONE environment variables.")
        return
    print("✅ Bot Started")
    asyncio.create_task(spam_loop())
    await client.run_until_disconnected()

if __name__ == "__main__":
    keep_alive()  # Start Flask keep-alive server in a thread
    asyncio.run(main())
