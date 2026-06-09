# artistas/tasks.py
from urllib import response
from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
from django.conf import settings
from .models import Artista, Message
import logging
from app.scheduler import scheduler
import os
import requests

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

for handler in logger.handlers:
    if isinstance(handler, logging.StreamHandler):
        handler.setLevel(logging.INFO)  # Suprime logs de adição de jobs, mas mantém logs importantes


# URL da API da WhatsGW
API_URL = settings.WHATS_GW_URL
apikey = settings.WHATS_GW_APIKEY


def enviar_mensagem_whatsgw(apikey, remetente, destinatario, mensagem_id, tipo_mensagem, corpo_mensagem):
    parametros = {
        "apikey": apikey,
        "phone_number": remetente,
        "contact_phone_number": destinatario,
        "message_custom_id": mensagem_id,
        "message_type": tipo_mensagem,
        "message_body": corpo_mensagem,
    }
 
    response = requests.post(API_URL, data=parametros)
    response.raise_for_status()
    return response.json()

 # Função para enviar mensagens agendadas
def enviar_mensagens_agendadas():
    agora = timezone.localdate()
    mensagens_pendentes = Message.objects.filter(
        artista__isnull=False,
        send_date__lte=timezone.localdate(), 
        sent=False
    )

    if mensagens_pendentes:
 
        artistas = Artista.objects.all()
        apikey = settings.WHATS_GW_APIKEY

        for artista in artistas:
            messages = Message.objects.filter(artista=artista, send_date__lte=agora, sent=False)
            for message in messages:
                if message.deve_enviar():
                    try:
                        remetente = "5548996269951"
                        destinatario = artista.telefone
                        mensagem_id = f"msg-{message.id}"
                        tipo_mensagem = "text"
                        corpo_mensagem = message.conteudo

                        # Tenta enviar a mensagem
                        enviar_mensagem_whatsgw(apikey, remetente, destinatario, mensagem_id, tipo_mensagem, corpo_mensagem)

                        message.enviar()
 
                    except requests.exceptions.RequestException as e:
                        logger.error(f"Erro na API WhatsGW para mensagem {message.id}: {e}")
                    except Exception as e:

                        logger.error(f"Erro ao enviar mensagem {message.id} para o artista {artista.id}: {e}")


def monitorar_mensagens():
    messages = Message.objects.filter(sent=False)
    agora = timezone.localdate()

    for message in messages:
        if message.send_date <= timezone.localdate() and not message.sent:
            try:
                enviar_mensagens_agendadas()

            except Exception as e:
                logger.error(f"Erro ao tentar enviar mensagem {message.id}: {e}")
                message.refresh_from_db()

# Função para atualizar status dos artistas e eventos, se necessário
def verificar_status():
    artistas = Artista.objects.all()
    for artista in artistas:
        try:
            if artista.deve_ser_atualizado():
                artista.atualizar_status()
                artista.save()
        except Exception as e:
            logger.error(f"Erro ao atualizar o status do artista {artista.id}: {e}")

        messages = Message.objects.filter(artista=artista)
        for message in messages:
            if message.deve_ser_atualizado():
                message.atualizar_status()
                message.save()


def iniciar_scheduler():
 
    # Apenas inicia o scheduler se não estiver rodando (sem agendar novas tarefas aqui)
    if not scheduler.running:
        scheduler.start()
        logger.info("Scheduler iniciado via iniciar_scheduler (sem reconfiguração de jobs).")
