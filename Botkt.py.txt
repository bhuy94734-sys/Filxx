import logging
import threading
from flask import Flask
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from database import db

TOKEN = "8899883627:AAFPauXpK7tCapOiv3PSDLdSdEgwx9Iny88"
ADMIN_ID = 8985238179

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# --- TẠO WEB SERVER ĐỂ RENDER VÀ UPTIMEROBOT PING ---
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Bot Tai Xiu is running 24/7!"

def run_web():
    # Render tự cấp biến môi trường PORT, mặc định chạy cổng 10000 nếu test local
    import os
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)

# --- BÀN PHÍM VÀ LOGIC BOT (Giữ nguyên như cũ) ---
def get_main_menu_keyboard(user_id):
    keyboard = [
        ["🕹️ Danh sách game", "🪪 Tài Khoản"],
        ["💲 Nạp Tiền", "₿ Rút Tiền"],
        ["🌸 Giới Thiệu", "🥕 Đua top"],
        ["🧧 Event", "🔍 Lệnh"],
    ]
    if user_id == ADMIN_ID:
        keyboard.append(["⚡ MENU ADMIN"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_admin_menu_keyboard():
    keyboard = [
        ["➕ Cộng tiền", "➖ Trừ tiền"],
        ["🎁 Tạo Giftcode", "📢 Thông báo Server"],
        ["🔙 Quay lại Menu chính"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_game_menu_keyboard():
    keyboard = [
        ["🎲 Xúc Xắc", "🦀 Bầu Cua"],
        ["🤟 Chẵn Lẻ Tele", "🎰 Slot Tele"],
        ["⚽ Bóng Đá", "🏀 Bóng Rổ"],
        ["🎲 SOLO Xúc Xắc", "✊ Kéo Búa Bao"],
        ["🔙 Quay lại Menu chính"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.get_user(user.id, user.username or user.first_name)
    welcome_text = (
        f"✅ **ID của bạn là `{user.id}`**\n\n"
        f"🏛️ Tham gia Room TX để săn hũ và nhận giftcode hằng ngày https://t.me/chiaselanhmanh\n\n"
        f"💙 Tham gia kênh thông báo để nhận code hàng ngày 💙"
    )
    await update.message.reply_text(welcome_text, reply_markup=get_main_menu_keyboard(user.id), parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user
    user_data = db.get_user(user.id, user.username or user.first_name)
    
    if text == "⚡ MENU ADMIN" and user.id == ADMIN_ID:
        await update.message.reply_text("👑 **CHÀO MỪNG ADMIN ĐẾN VỚI BẢNG ĐIỀU KHIỂN**", reply_markup=get_admin_menu_keyboard(), parse_mode="Markdown")
        return
        
    if user.id == ADMIN_ID:
        if text == "➕ Cộng tiền":
            await update.message.reply_text("📌 Cú pháp: `/cong [ID] [Số tiền]`", parse_mode="Markdown")
            return
        elif text == "➖ Trừ tiền":
            await update.message.reply_text("📌 Cú pháp: `/tru [ID] [Số tiền]`", parse_mode="Markdown")
            return
        elif text == "🎁 Tạo Giftcode":
            await update.message.reply_text("📌 Cú pháp: `/taocode [Mã] [Số tiền]`", parse_mode="Markdown")
            return
        elif text == "📢 Thông báo Server":
            await update.message.reply_text("📌 Cú pháp: `/tb [Nội dung]`", parse_mode="Markdown")
            return

    if text == "🕹️ Danh sách game":
        await update.message.reply_text("🎮 **Chọn trò chơi:**", reply_markup=get_game_menu_keyboard(), parse_mode="Markdown")
    elif text == "🪪 Tài Khoản":
        account_info = (
            f"🪪 **TÀI KHOẢN**\n🆔 `{user_data['user_id']}`\n"
            f"💰 Số dư: `{user_data['balance']:,.0f} VNĐ`\n"
            f"📊 Tổng cược: `{user_data['total_bet']:,.0f} VNĐ`"
        )
        await update.message.reply_text(account_info, parse_mode="Markdown")
    elif text == "💲 Nạp Tiền":
        await update.message.reply_text(f"💲 Cú pháp nạp: `NAP {user_data['user_id']}`", parse_mode="Markdown")
    elif text == "₿ Rút Tiền":
        await update.message.reply_text("₿ Cú pháp: `/rut [Số tiền] [NH] [STK] [Tên]`", parse_mode="Markdown")
    elif text == "🌸 Giới Thiệu":
        await update.message.reply_text(f"🌸 Link: `https://t.me/{context.bot.username}?start=ref_{user.id}`", parse_mode="Markdown")
    elif text == "🥕 Đua top":
        await update.message.reply_text("🥕 Đang cập nhật...", parse_mode="Markdown")
    elif text == "🧧 Event":
        await update.message.reply_text("🧧 Dùng lệnh: `/code <mã>`", parse_mode="Markdown")
    elif text == "🔍 Lệnh":
        await update.message.reply_text("🔍 Lệnh: `/code`, `/rut`", parse_mode="Markdown")
    elif text == "🔙 Quay lại Menu chính":
        await update.message.reply_text("🏠 Đã về Menu chính:", reply_markup=get_main_menu_keyboard(user.id))
    elif text in ["🎲 Xúc Xắc", "🦀 Bầu Cua", "🤟 Chẵn Lẻ Tele", "🎰 Slot Tele", "⚽ Bóng Đá", "🏀 Bóng Rổ", "🎲 SOLO Xúc Xắc", "✊ Kéo Búa Bao"]:
        await update.message.reply_text(f"🎲 Đang phát triển trò chơi: **{text}**", parse_mode="Markdown")

async def cmd_cong(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    try:
        db.update_balance(int(context.args[0]), float(context.args[1]))
        await update.message.reply_text(f"✅ Đã cộng tiền thành công!")
    except:
        await update.message.reply_text("⚠️ Sai cú pháp: `/cong [ID] [Số tiền]`")

async def cmd_tru(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    try:
        db.update_balance(int(context.args[0]), -float(context.args[1]))
        await update.message.reply_text(f"✅ Đã trừ tiền thành công!")
    except:
        await update.message.reply_text("⚠️ Sai cú pháp: `/tru [ID] [Số tiền]`")

async def cmd_taocode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    try:
        if db.create_giftcode(context.args[0], float(context.args[1])):
            await update.message.reply_text(f"🎁 Tạo giftcode `{context.args[0]}` thành công!")
        else:
            await update.message.reply_text("⚠️ Mã code đã tồn tại!")
    except:
        await update.message.reply_text("⚠️ Sai cú pháp: `/taocode [Mã] [Số tiền]`")

async def cmd_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        res = db.use_giftcode(update.effective_user.id, context.args[0])
        if res == "not_found": await update.message.reply_text("❌ Mã không tồn tại!")
        elif res == "used": await update.message.reply_text("❌ Mã đã được dùng!")
        else: await update.message.reply_text(f"🎉 Nhận thành công `{res:,.0f} VNĐ`!")
    except:
        await update.message.reply_text("⚠️ Sai cú pháp: `/code <mã>`")

async def cmd_thongbao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    msg = " ".join(context.args)
    if not msg: return
    for uid in db.get_all_users():
        try: await context.bot.send_message(chat_id=uid, text=f"📢 **THÔNG BÁO**\n\n{msg}", parse_mode="Markdown")
        except: pass
    await update.message.reply_text("✅ Đã gửi thông báo xong!")

def main():
    # Khởi chạy Web Server Flask bằng luồng riêng (Thread) để không chặn Bot Telegram
    t = threading.Thread(target=run_web)
    t.daemon = True
    t.start()

    # Khởi chạy Bot Telegram
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CommandHandler("cong", cmd_cong))
    app.add_handler(CommandHandler("tru", cmd_tru))
    app.add_handler(CommandHandler("taocode", cmd_taocode))
    app.add_handler(CommandHandler("code", cmd_code))
    app.add_handler(CommandHandler("tb", cmd_thongbao))

    print("🤖 Bot và Web Server đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()
