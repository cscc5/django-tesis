from rest_framework  import serializers
from .models import Trabajos_Clasificados
class TrabajosClasificadosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trabajos_Clasificados
        fields = ('titulo',)
