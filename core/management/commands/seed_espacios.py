from django.core.management.base import BaseCommand
from core.models import EspacioParqueadero

class Command(BaseCommand):
    help = 'Popula la base de datos con espacios de parqueadero iniciales'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creando espacios de parqueadero...')
        
        # Crear 10 espacios para CARRO
        for i in range(1, 11):
            EspacioParqueadero.objects.get_or_create(
                numero=i,
                defaults={'tipo': 'CARRO', 'estado': 'LIBRE'}
            )
            
        # Crear 10 espacios para MOTO
        for i in range(11, 21):
            EspacioParqueadero.objects.get_or_create(
                numero=i,
                defaults={'tipo': 'MOTO', 'estado': 'LIBRE'}
            )

        self.stdout.write(self.style.SUCCESS('Espacios creados exitosamente.'))
