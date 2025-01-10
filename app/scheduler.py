from apscheduler.schedulers.background import BackgroundScheduler

from app.reservations.application.jobs.cancel_expired_reservations_job import cancel_expired_reservations_job


def init_apscheduler() -> None:
    scheduler = BackgroundScheduler()
    scheduler.add_job(cancel_expired_reservations_job, "interval", minutes=1)
    scheduler.start()
