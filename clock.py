from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()


@sched.scheduled_job('cron', hour="*/3", minute=0)
def updater():
    """
    Run our update command every three hours.
    """
    # Set env
    import os
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

    # Boot Django
    import django
    django.setup()

    # Run the command
    from django.core.management import call_command
    call_command("updatedownloadswebsite", noinput=True, verbosity=3)


sched.start()
