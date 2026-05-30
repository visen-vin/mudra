import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import redis.asyncio as redis
from backend.services.screener_engine import ScreenerEngine

logger = logging.getLogger(__name__)

class ScreenerScheduler:
    def __init__(self, redis_client: redis.Redis):
        self.scheduler = AsyncIOScheduler()
        self.engine = ScreenerEngine(redis_client)

    def start(self):
        """Start the scheduler with the 1-minute scan job"""
        logger.info("Starting Screener Scheduler...")
        
        # Trigger at :01 second of every minute
        trigger = CronTrigger(second=1)
        
        self.scheduler.add_job(
            self.engine.run_scan,
            trigger=trigger,
            id="screener_scan_job",
            name="1-Minute Market Scan",
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info("Screener Scheduler active. Job: 1-Minute Market Scan")

    def stop(self):
        """Shutdown the scheduler"""
        logger.info("Stopping Screener Scheduler...")
        self.scheduler.shutdown()
