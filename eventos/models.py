from wsgiref import validate
from django.db import models
from artistas.models import Artista
 


 
class Evento(models.Model):

    artista = models.ForeignKey(Artista, on_delete=models.CASCADE)
    data = models.DateField(auto_now_add=True)
    descricao = models.TextField(null=True, blank=True)
    scheduled_date = models.DateTimeField(null=True, blank=True)
 
    class Meta:
        ordering = ['data']


    def __str__(self):
        return f"{self.artista.nome} - {self.formatted_data()}"

    def formatted_data(self):
        return self.data.strftime('%d-%m-%Y')

    def formatted_horario(self):
        return self.horario.strftime('%H:%M')
