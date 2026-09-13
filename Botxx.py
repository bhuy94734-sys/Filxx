import asyncio
import logging
import os
import random
from aiogram import Bot, Dispatcher, F, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

TOKEN = os.getenv("BOT_TOKEN", "8554416932:AAGhOIgzgHGYTTd9H3ghd5HApxerB-9e20U")
ADMIN_ID = int(os.getenv("ADMIN_ID", "8985238179"))
GROUP_CHAT_ID = int(os.getenv("GROUP_CHAT_ID", "-100123456789"))

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

current_session = 105020
current_jackpot = 300000.0
recent_tai_xiu = []
recent_chan_le = []
game_running = True
players_in_session = {}

def get_dice_emoji(val: int) -> str:
    return ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"][val - 1]

def build_statistics_string():
    tx_str = "".join(["🔴" if x == "T" else "🔵" for x in recent_tai_xiu])
    cl_str = "".join(["⚫️" if x == "C" else "⚪️" for x in recent_chan_le])
    return f"""🚥 <b>THỐNG KÊ 12 PHIÊN GẦN NHẤT</b>
KẾT QUẢ TÀI XỈU: {tx_str if tx_str else "Chưa có dữ liệu"}
KẾT QUẢ CHẴN LẺ: {cl_str if cl_str else "Chưa có dữ liệu"}"""

def build_main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Nạp Tiền 💵", callback_data="btn_nap_tien")]
    ])

async def run_game_loop():
    global current_session, current_jackpot, recent_tai_xiu, recent_chan_le, game_running
    await asyncio.sleep(5)
    while True:
        if game_running:
            try:
                dice_msg_1 = await bot.send_dice(chat_id=GROUP_CHAT_ID, emoji="🎲")
                d1 = dice_msg_1.dice.value
                await asyncio.sleep(1)

                dice_msg_2 = await bot.send_dice(chat_id=GROUP_CHAT_ID, emoji="🎲")
                d2 = dice_msg_2.dice.value
                await asyncio.sleep(1)

                dice_msg_3 = await bot.send_dice(chat_id=GROUP_CHAT_ID, emoji="🎲")
                d3 = dice_msg_3.dice.value
                await asyncio.sleep(2)

                total = d1 + d2 + d3
                tx_result, tx_code = ("Xỉu", "X") if total <= 10 else ("Tài", "T")
                cl_result, cl_code = ("Chẵn", "C") if total % 2 == 0 else ("Lẻ", "L")

                recent_tai_xiu.append(tx_code)
                if len(recent_tai_xiu) > 12: recent_tai_xiu.pop(0)

                recent_chan_le.append(cl_code)
                if len(recent_chan_le) > 12: recent_chan_le.pop(0)

                tong_thang = random.randint(500000, 3000000)
                tong_thua = random.randint(500000, 3000000)
                cong_hu = tong_thua * 0.005
                current_jackpot += cong_hu

                text = f"""KẾT QUẢ XX PHIÊN (#{current_session})

_____________________
|   {get_dice_emoji(d1)} {get_dice_emoji(d2)} {get_dice_emoji(d3)} ➡️ {total} điểm → {tx_result} | {cl_result}
|  
|  TỔNG ĐIỂM: {total}  
|  TỔNG THẮNG: {tong_thang:,.0f} VND
|  TỔNG THUA: {tong_thua:,.0f} VND
|  CỘNG HŨ: {cong_hu:,.0f} VND  
|  HŨ HIỆN TẠI: {current_jackpot:,.0f} VND
|_____________________

{build_statistics_string()}"""

                await bot.send_message(chat_id=GROUP_CHAT_ID, text=text, reply_markup=build_main_keyboard())
                current_session += 1
            except Exception as e:
                logging.error(f"Lỗi vòng lặp: {e}")
        await asyncio.sleep(30)

# --- CÁC LỆNH ADMIN ---
@dp.message(Command("stop"))
async def admin_stop_game(message: types.Message):
    global game_running
    if message.from_user.id != ADMIN_ID: return
    game_running = not game_running
    await message.answer(f"Trạng thái game: {'Chạy' if game_running else 'Dừng'}")

@dp.message(Command("resethu"))
async def admin_reset_hu(message: types.Message):
    global current_jackpot
    if message.from_user.id != ADMIN_ID: return
    current_jackpot = 300000.0
    await message.answer("Đã reset hũ về 300,000 VNĐ")

@dp.message(Command("conghu"))
async def admin_cong_hu(message: types.Message):
    global current_jackpot
    if message.from_user.id != ADMIN_ID: return
    args = message.text.split()
    if len(args) < 2: return
    try:
        amount = float(args[1])
        current_jackpot += amount
        await message.answer(f"Đã cộng thêm {amount:,.0f} VNĐ vào hũ.")
    except ValueError: pass

@dp.message(Command("checkplayer"))
async def admin_check_player(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    if not players_in_session:
        await message.answer("Chưa có người chơi nào.")
        return
    text_p = "👥 DANH SÁCH NGƯỜI CHƠI:\n"
    for uid, info in players_in_session.items():
        text_p += f"- @{info['username']} ({uid}): {info['balance']:,.0f} VNĐ\n"
    await message.answer(text_p)

# --- USER & NẠP TIỀN ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(f"🎲 <b>HỆ THỐNG XÚC XẮC TỰ ĐỘNG</b>\nPhiên #{current_session}", reply_markup=build_main_keyboard(), parse_mode=ParseMode.HTML)

@dp.callback_query(F.data == "btn_nap_tien")
async def callback_nap_tien(callback: types.CallbackQuery):
    amounts = [20000, 50000, 100000, 200000, 500000, 1000000]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"💵 {amt:,.0f} VNĐ", callback_data=f"deposit_amt_{amt}")] for amt in amounts
    ])
    await callback.message.edit_text("Chọn số tiền cần nạp:", reply_markup=keyboard)
    await callback.answer()

@dp.callback_query(F.data.startswith("deposit_amt_"))
async def process_deposit_amount(callback: types.CallbackQuery):
    amount = int(callback.data.split("_")[2])
    user_id = callback.from_user.id
    username = callback.from_user.username or str(user_id)
    random_content = f"NAP{user_id}{random.randint(100, 999)}"
    
    if user_id not in players_in_session:
        players_in_session[user_id] = {"balance": 0.0, "username": username}

    qr_url = f"https://img.vietqr.io/image/970422-2105200999999-compact2.jpg?amount={amount}&addInfo={random_content}&accountName=KHONG%20QUOC%20BAO"
    
    caption = f"Chuyển khoản {amount:,.0f} VNĐ với nội dung: <code>{random_content}</code>"
    admin_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Duyệt", callback_data=f"approve_{user_id}_{amount}"),
         InlineKeyboardButton(text="❌ Từ chối", callback_data=f"reject_{user_id}_{amount}")]
    ])
    
    try:
        await callback.message.answer_photo(photo=qr_url, caption=caption, parse_mode=ParseMode.HTML)
    except Exception:
        await callback.message.answer(caption, parse_mode=ParseMode.HTML)
        
    await bot.send_message(chat_id=ADMIN_ID, text=f"Yêu cầu nạp từ @{username}: {amount:,.0f}đ", reply_markup=admin_kb)
    await callback.answer()

@dp.callback_query(F.data.startswith("approve_") | F.data.startswith("reject_"))
async def admin_handle_deposit(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID: return
    parts = callback.data.split("_")
    action, user_id, amount = parts[0], int(parts[1]), float(parts[2])
    
    if action == "approve":
        if user_id in players_in_session:
            players_in_session[user_id]["balance"] += amount
        else:
            players_in_session[user_id] = {"balance": amount, "username": str(user_id)}
        await bot.send_message(chat_id=user_id, text=f"✅ Đã duyệt {amount:,.0f} VNĐ vào tài khoản.")
        await callback.message.edit_caption(caption=callback.message.caption + "\n\n<b>✅ ĐÃ DUYỆT</b>", parse_mode=ParseMode.HTML)
    else:
        await bot.send_message(chat_id=user_id, text=f"❌ Giao dịch nạp {amount:,.0f} VNĐ bị từ chối.")
        await callback.message.edit_caption(caption=callback.message.caption + "\n\n<b>❌ ĐÃ TỪ CHỐI</b>", parse_mode=ParseMode.HTML)
    await callback.answer()

async def main():
    asyncio.create_task(run_game_loop())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
