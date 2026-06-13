from datetime import datetime
from django import forms
from django.utils import timezone
from .models import Evento
 
class EventoForm(forms.ModelForm):
    scheduled_date = forms.DateTimeField(
        label='Data Agendada',
        input_formats=['%Y-%m-%dT%H:%M'],
        widget=forms.DateTimeInput(
            format='%Y-%m-%dT%H:%M',
            attrs={
                'type': 'date',
                'class': 'form-control',
            }
        )
    )
    
    horario = forms.TimeField(
        label='Hora',
        input_formats=['%H:%M'],
        widget=forms.TimeInput(
            format='%H:%M',
            attrs={
                'type': 'time',
                'class': 'form-control',
            }
        )
    )


    class Meta:
        model = Evento
        fields = ['artista', 'scheduled_date', 'horario', 'descricao']
        widgets = {
            'artista': forms.Select(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        labels = {
            'descricao': 'Descrição',             
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.scheduled_date:
            scheduled_date = timezone.localtime(self.instance.scheduled_date)
            self.fields['scheduled_date'].initial = scheduled_date.date()
            self.fields['horario'].initial = scheduled_date.time()

    def save(self, commit=True):
        evento = super().save(commit=False)

        data_agendada = self.cleaned_data['scheduled_date']
        horario = self.cleaned_data['horario']

        scheduled_datetime = datetime.combine(data_agendada, horario)

        if timezone.is_naive(scheduled_datetime):
            scheduled_datetime = timezone.make_aware(
                scheduled_datetime,
                timezone.get_current_timezone()
            )

        evento.scheduled_date = scheduled_datetime

        if commit:
            evento.save()

        return evento   