from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone
from apscheduler.triggers.cron import CronTrigger
import logging


# Configura o logger p monitorar agendador
logger = logging.getLogger('apscheduler')
logger.setLevel(logging.INFO)


class JobAddedFilter(logging.Filter):
    def filter(self, record):
        # Ignora mensagens sobre jobs adicionados, mas mantém outras mensagens
        return 'Added job' not in record.getMessage()


for handler in logger.handlers:
    if isinstance(handler, logging.StreamHandler):
        handler.addFilter(JobAddedFilter())  # Suprime logs de adição de jobs


scheduler = BackgroundScheduler(timezone=timezone("America/Sao_Paulo"))


def start_scheduler():
 
    if scheduler.running:
        #("✅ Scheduler está rodando!")
        return
        #print("✅ Scheduler está rodando!")

    from artistas.tasks import enviar_mensagens_agendadas, verificar_status

    scheduler.remove_all_jobs()

    scheduler.start()

    existing_jobs = {job.id for job in scheduler.get_jobs()}

    if 'enviar_mensagens_agendadas' not in existing_jobs:
        scheduler.add_job(enviar_mensagens_agendadas, CronTrigger(hour=12 , minute=38),
                            id='enviar_mensagens_agendadas', replace_existing=True)

    if 'verificar_status' not in existing_jobs:
        scheduler.add_job(verificar_status, CronTrigger(hour=6, minute=10),  
                            id='verificar_status', replace_existing=True)


 
