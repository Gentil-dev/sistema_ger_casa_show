from django import forms
from .models import Evento
from artistas.models import Artista

class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = ['artista', 'descricao', 'scheduled_date']
        widgets = {
            'artista': forms.Select(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'scheduled_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }
        labels = {
            'descricao': 'Descrição',
            'scheduled_date': 'Data Agendada',
        }