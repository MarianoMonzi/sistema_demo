from django.forms import ModelForm
from .models import Cliente, Tarea, ListaCorrectiva, ListaPreventiva


class ClienteForm(ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'numero', 'patente', 'modelo']


class TareaForm(ModelForm):
    class Meta:
        model = Tarea
        fields = ['fecha', 'planilla',
                  'kilometros', 'proxservicio', 'mecanico']


class ListaCorrectivaForm(ModelForm):
    class Meta:
        model = ListaCorrectiva
        fields = ['items']


class ListaPreventivaForm(ModelForm):
    class Meta:
        model = ListaPreventiva
        fields = ['items']
