# import_excel_data.py
import pandas as pd
from django.core.management.base import BaseCommand
from main_app.models import Trabajos_Clasificados  

class Command(BaseCommand):
    help = 'Import data from Excel to MyModel'

    def handle(self, *args, **kwargs):
        excel_file_path = r'C:\Users\david\Downloads\trabajo_final_carrera\final\entrenamiento.csv'
        data = pd.read_csv(excel_file_path, delimiter=',')

        for index, row in data.iterrows():
            my_model_instance = Trabajos_Clasificados(
                titulo=row['title'],
                clasificacion=row['category'],
                
            )
            my_model_instance.save()
            self.stdout.write(self.style.SUCCESS(f'Successfully imported data for ID {my_model_instance.id}'))