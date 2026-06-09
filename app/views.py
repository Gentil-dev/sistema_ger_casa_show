from django.shortcuts import render 
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import os, json
from django.utils.html import strip_tags


def pagina_anotacoes(request):
    return render(request, 'anotacoes.html')   

@csrf_exempt
def dados_anotacoes(request):
    caminho_arquivo = os.path.join(settings.BASE_DIR, 'anotacoes_data.json')

    if request.method == 'GET':
        if os.path.exists(caminho_arquivo):
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return JsonResponse({'editor1': data.get('editor1', '')})
         
        return JsonResponse({'editor1': ''})

    if request.method == 'POST':
        conteudo_html = json.loads(request.body).get("editor1", "")          
        conteudo_anterior = ""
        
        if os.path.exists(caminho_arquivo):
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                try:
                    data_antiga = json.load(f)
                    conteudo_anterior = data_antiga.get("editor1", "")
                except json.JSONDecodeError:
                    pass
        #salva o novo conteúdo    
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            json.dump({'editor1': conteudo_html}, f, ensure_ascii=False, indent=4)
        #Limpa para comparar só o texto real
        texto_atual = strip_tags(conteudo_html).strip()
        texto_anterior = strip_tags(conteudo_anterior).strip()
        #lógica das msgs
        if not texto_atual:
            return JsonResponse({'message': 'Todas anotações removidas com sucesso.'})
        if texto_anterior and texto_atual != texto_anterior and len(texto_atual) < len(texto_anterior):
            return JsonResponse({'message': 'Anotação parcial removida com sucesso'})
        
        return JsonResponse({'message': 'Anotações salvas com sucesso.'})

    return JsonResponse({'error': 'Método não permitido'}, status=405)
