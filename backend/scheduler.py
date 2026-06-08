from apscheduler.schedulers.background import BackgroundScheduler

_scheduler = BackgroundScheduler()


def start():
    from backend.agents.shift_handover import ShiftHandoverCopilot
    copilot = ShiftHandoverCopilot()
    _scheduler.add_job(copilot.run_handover, "cron", hour="6,14,22", minute=0)
    _scheduler.start()
    print("scheduler: shift handover jobs registered (6am, 2pm, 10pm)")


def stop():
    _scheduler.shutdown(wait=False)
