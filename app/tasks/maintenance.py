from app.celery_app import celery_app

@celery_app.task(name="app.tasks.maintenance.cleanup_expired_sessions")
def cleanup_expired_sessions():
    print("🧹 Running session cleanup...")

@celery_app.task(name="app.tasks.maintenance.reset_daily_limits")
def reset_daily_limits():
    print("🔄 Resetting daily limits...")
