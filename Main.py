import asyncio
import subprocess

async def run_script(script_name):
    # Chạy từng file bot như một tiến trình độc lập nhưng chung thư mục/ổ cứng
    process = await asyncio.create_subprocess_exec("python", script_name)
    await process.wait()

async def main():
    # Chạy song song Bot chính và Bot xúc xắc
    await asyncio.gather(
        run_script("Botkt.py"),
        run_script("Botxx.py")
    )

if __name__ == "__main__":
    asyncio.run(main())
