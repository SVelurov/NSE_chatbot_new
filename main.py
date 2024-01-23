import asyncio
import os
from apscheduler.schedulers.background import BackgroundScheduler
from tzlocal import get_localzone
import config as cfg
from tg_bot import mk_bot
from nse_update import login_et

login_url_et = os.getenv('login_url_et')
username_et = os.getenv('username_et')
password_et = os.getenv('password_et')

scheduler = BackgroundScheduler()
scheduler.configure(timezone=str(get_localzone()))
scheduler.add_job(login_et, 'cron', hour=23, minute=30)


async def run_bot():
    bot, dp = await mk_bot(cfg.TG_BOT_TOKEN)
    session = await bot.get_session()
    try:
        await dp.start_polling(dp)
    finally:
        await session.close()


async def main():
    scheduler.start()
    tg_bot_task = asyncio.create_task(run_bot())
    await tg_bot_task

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped!")





