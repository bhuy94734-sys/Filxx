import asyncio
import sys

async def run_bot(script_name):
    while True:
        # Chạy từng bot dưới dạng tiến trình hệ thống độc lập
        process = await asyncio.create_subprocess_exec(
            sys.executable, script_name
        )
        await process.wait()
        print(f"[{script_name}] Bot bị dừng, đang khởi động lại sau 3 giây...")
        await asyncio.sleep(3)

async def main():
    # Chạy song song cả 2 bot, nếu con nào chết sẽ tự khởi động lại
    await asyncio.gather(
        run_bot("Botkt.py"),
        run_bot("Botxx.py")
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Đã dừng hệ thống bot.")
