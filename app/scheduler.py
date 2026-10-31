
import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.reminder_service import (
    send_due_today_reminders,
    send_due_tomorrow_reminders
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# Create scheduler using Indian Standard Time
scheduler = AsyncIOScheduler(
    timezone="Asia/Kolkata"
)


def start_scheduler():
    """Register automatic reminder jobs."""

    # Morning: remind about tasks due today
    scheduler.add_job(
        send_due_today_reminders,
        trigger="cron",
        hour=8,
        minute=0,
        id="morning_task_reminder",
        replace_existing=True,
        max_instances=1,
        coalesce=True
    )

    # Evening: remind about tasks due tomorrow
    scheduler.add_job(
        send_due_tomorrow_reminders,
        trigger="cron",
        hour=18,
        minute=0,
        id="evening_task_reminder",
        replace_existing=True,
        max_instances=1,
        coalesce=True
    )

    scheduler.start()

    logger.info("AI TaskOps scheduler started!")

    for job in scheduler.get_jobs():
        logger.info(
            "Job: %s | Next execution: %s",
            job.id,
            job.next_run_time
        )


async def main():
    """Keep the scheduler running."""

    start_scheduler()

    try:
        # Keep the application alive
        await asyncio.Event().wait()

    finally:
        if scheduler.running:
            scheduler.shutdown(wait=False)

        logger.info("AI TaskOps scheduler stopped.")


if __name__ == "__main__":
    asyncio.run(main())
