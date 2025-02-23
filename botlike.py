import requests
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

BOT_TOKEN = "7020986217:AAEYXHJJkhREm3III9t6kQ2us8BycDncoZ8"
REQUIRED_CHANNEL = "@shadowzrx_support" #your group user or channel
ACCOUNTS_FILE = "accs.txt"

async def is_user_member(bot, user_id):
    try:
        member = await bot.get_chat_member(chat_id=REQUIRED_CHANNEL, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False

def save_uid_to_file(uid):
    uids = {}
    uids_to_save = []
    try:
        with open(ACCOUNTS_FILE, "r") as file:
            for line in file:
                parts = line.strip().split(" ")
                existing_uid = parts[0]
                count = int(parts[1].strip("()")) if len(parts) > 1 else 1
                uids[existing_uid] = count
    except FileNotFoundError:
        pass

    if uid in uids:
        uids[uid] += 1
    else:
        uids[uid] = 1

    for uid_key, count in uids.items():
        uids_to_save.append(f"{uid_key} ({count})\n")
        
    with open(ACCOUNTS_FILE, "w") as file:
        file.writelines(uids_to_save)

async def send_loading_message(update: Update, stop_event: asyncio.Event):
    loading_message = await update.message.reply_text("⏳ Loading... 1%")
    for i in range(2, 101, 5):
        if stop_event.is_set() and i >= 20:
            break
        await loading_message.edit_text(f"⏳ Loading... {i}%")
    return loading_message

async def send_likes(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id

    if not await is_user_member(context.bot, user_id):
        await update.message.reply_text(
            f"⚠️ You must subscribe to the channel first: {REQUIRED_CHANNEL}\nThen try again."
        )
        return

    try:
        if len(context.args) != 1:
            await update.message.reply_text("⚠️ Please enter the UID, like: /like 6570832950")
            return

        uidd = context.args[0].strip()
        save_uid_to_file(uidd)

        keyy = "proAmine"
        url = f"https://ff-virusteam.vercel.app/likes2?key={keyy}&uid={uidd}"

        stop_event = asyncio.Event()
        loading_task = asyncio.create_task(send_loading_message(update, stop_event))

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            status = response.status_code
        except requests.exceptions.RequestException as e:
            await update.message.reply_text(f"❌ Request Error: with server")
            return

        await asyncio.sleep(0.2)
        stop_event.set()
        loading_message = await loading_task

        if status == 200:
            response_json = response.json()

            if isinstance(response_json.get("message"), dict):
                data = response_json["message"]
                await loading_message.edit_text(
                    f"✅ **Likes Sent Successfully!**\n\n"
                    f"📋 Profile Info:\n"
                    f"👤 Name: {data.get('Name')}\n"
                    f"🆔 UID: {data.get('UID')}\n"
                    f"🎯 Level: {data.get('Level')}\n"
                    f"🌍 Region: {data.get('Region')}\n"
                    f"❤️ Likes Before: {data.get('Likes Before')}\n"
                    f"👍 Likes After: {data.get('Likes After')}\n"
                    f"➕ Likes Added: {data.get('Likes Added')}\n"
                    f"⚡ Speed: {data.get('Time Sent')}"
                )
            else:
                translated_message = f"❌ The account with UID `{uidd}` has reached the maximum daily like limit or not found."
                await loading_message.edit_text(translated_message)
        else:
            await loading_message.edit_text(f"❌ Server error: {status}. Please try again later.")

    except Exception as e:
        await update.message.reply_text(f"⚠️ Error occurred: {e}")

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "👋 Welcome! Use the following commands:\n"
        "/like <UID> - To send likes\n"
        "/likes <UID> - Alternate command for sending likes\n"
    )

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("like", send_likes))
    application.add_handler(CommandHandler("likes", send_likes))
    application.add_handler(CommandHandler("start", start))
    application.run_polling()

if __name__ == "__main__":
    main()