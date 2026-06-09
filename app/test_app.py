from django.test import TestCase
from django.urls import reverse
from artistas.models import Artista
from eventos.models import Evento
from datetime import date
from django.utils import timezone
import os
import json
from django.conf import settings
from unittest import mock
from django.apps import apps

class HomeViewTests(TestCase):
    
    def setUp(self):
        #cria um artista para teste
        self.artista = Artista.objects.create(
            nome="Artista Teste",
            cpf="12345678909",
            banco="Banco Teste",
            tipo_chave_pix="cel",
            chave_pix="12345678909"
        )
            
    def test_home_view_status_code(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        
    def test_home_view_template_used(self):
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'base.html')
        
    def test_home_view_contains_eventos_proximos(self):
        response = self.client.get(reverse('home'))
        self.assertIn('eventos_proximos', response.context)
        self.assertEqual(response.context['eventos_proximos'].count(), 0)
                
    def test_home_view_exibe_banner(self):
        response = self.client.get(reverse('home'))
    #cria um evento associado ao artista criado
        Evento.objects.create(
            artista=self.artista,
            descricao='Evento Teste',
            scheduled_date=timezone.make_aware(
                timezone.datetime(2024, 12, 18, 18, 0)
            )
        )
        response = self.client.get(reverse('home'))
        
        # Verifica se o evento aparece no contexto
        self.assertIn('eventos_proximos', response.context)
        eventos_proximos = response.context['eventos_proximos']
        print(eventos_proximos)  # Depuração
        self.assertEqual(eventos_proximos.count(), 1)  # Certifica-se de que um evento está no queryset
    
        # Verifica se a descrição do evento está no HTML
        self.assertContains(response, 'Bem-vindo ao Casting Artístico!') # Verifica se a descrição do evento está na resposta
        
class EventoListViewTests(TestCase):
    def setUp(self):
        self.artista = Artista.objects.create(
            nome="Artista Teste",
            cpf="12345678909",
            telefone="+5511988888888",
            banco="Banco Teste",
            tipo_chave_pix="cpf",
            chave_pix="12345678909",
            email="artista@teste.com"
        )
        self.evento = Evento.objects.create(
            artista=self.artista,                          
            descricao="Evento Funcional",
            scheduled_date=timezone.now()
        )

    def test_evento_list_view_exibe_descricao(self):
        response = self.client.get(reverse('evento_list'))
        self.assertContains(response, "Evento Funcional")

 

class AppViewsTestCase(TestCase):

    def setUp(self):
        self.caminho_json = os.path.join(settings.BASE_DIR, 'anotacoes_data.json')
        # Garantir que o arquivo não exista antes de alguns testes
        if os.path.exists(self.caminho_json):
            os.remove(self.caminho_json)

    def tearDown(self):
        # Limpeza após os testes
        if os.path.exists(self.caminho_json):
            os.remove(self.caminho_json)

    def test_pagina_anotacoes_status_code(self):
        response = self.client.get(reverse('anotacoes'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'anotacoes.html')

    def test_dados_anotacoes_get_sem_arquivo(self):
        response = self.client.get(reverse('dados_anotacoes'))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'editor1': ''})

    def test_dados_anotacoes_post_salva_conteudo(self):
        dados = {'editor1': 'texto 1'}
        response = self.client.post(
            reverse('dados_anotacoes'),
            data=json.dumps(dados),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'message': 'Anotações salvas com sucesso.'})
        # Verifica se salvou mesmo
        with open(self.caminho_json, 'r', encoding='utf-8') as f:
            conteudo_salvo = json.load(f)
        self.assertEqual(conteudo_salvo, dados)

    def test_dados_anotacoes_metodo_nao_permitido(self):
        response = self.client.put(reverse('dados_anotacoes'), data={})
        self.assertEqual(response.status_code, 405)
        self.assertIn('error', response.json())

class WSGIImportTest:
    def test_wsgi_application_import(self):
        from app.wsgi import application
        assert application is None
        
class ASGIImportTest:
    def test_asgi_application_import(self):
        from app.asgi import application
        assert application is not None
        
def test_app_config_name():
    from django.apps import apps
    config = apps.get_app_config('app')
    assert config.name == 'app'
     
 
 
def test_ready_inicia_scheduler_localmente(monkeypatch):
    # Garante que o scheduler ainda não foi iniciado
    from app.apps import scheduler_initialized
    monkeypatch.setitem(os.environ, "RUN_MAIN", "true")
    monkeypatch.delenv("RAILWAY_ENVIRONMENT_NAME", raising=False)

    # Força a variável global a False
    import app.apps
    app.apps.scheduler_initialized = False

    with mock.patch("app.scheduler.start_scheduler") as mock_start_scheduler:
        app_config = apps.get_app_config("app")
        app_config.ready()
        mock_start_scheduler.assert_called_once()
