# views.py en Django
import re
import json
import time
import openai
import pandas as pd
from .obb import DataExtract
from unidecode import unidecode
from rest_framework import status
from nltk.corpus import stopwords 
from Keys.Keys import openai_api_key
from rest_framework.views import APIView
from .models import Trabajos_Clasificados
from rest_framework.response import Response
from sklearn.feature_extraction.text import CountVectorizer 

# assigning API KEY to initialize openai environment
openai.api_key = openai_api_key

class ClasificadorTextViewSet(APIView):
    def get(self, request):
        titulo = request.GET.get('titulo', None)
        
        if titulo:
            response = openai.ChatCompletion.create(
            model="gpt-4-0613",
            messages=[
            {"role": "user", "content": f"""
            Por favor, clasifica el título: {titulo} como 'SI' o 'NO'. Si el título está relacionado con 
            Tecnología de la Información o IT, 
            etiquétalo como 'SI'; de lo contrario, etiquétalo como 'NO'; UNICA y exclusivamente puedes responder 'SI' o 'NO', 
            absolutamente nada mas .
            """}]
            )
            if (response['choices'][0]['message']['content']=='SI'):

                data = Trabajos_Clasificados.objects.values_list('titulo', 'clasificacion')
                df = pd.DataFrame(data, columns=['titulo', 'clasificacion'])
                X, y = df['titulo'], df['clasificacion']
                max_features = 1000
                cou_vectorizer = CountVectorizer(max_features=max_features, stop_words=stopwords.words('spanish'), ngram_range=(1, 2))

                X_counts = cou_vectorizer.fit_transform(X)

                X = X_counts.toarray()
                from sklearn.naive_bayes import MultinomialNB

                classifier = MultinomialNB()

                classifier.fit(X, y)
                test = [titulo]
                X_counts = cou_vectorizer.transform(test)
                X = X_counts.toarray()
                predic = classifier.predict(X)

                # Trabajos_Clasificados(titulo=titulo, clasificacion=predic[0]).save()       
                return Response({'resultados': predic[0]}, status=status.HTTP_200_OK)

            else:

                return Response({'error': f'Parámetro {titulo} No coincide con el area de TI'}, status=status.HTTP_400_BAD_REQUEST)

        else: 

            return Response({'error': 'Parámetro "titulo" no proporcionado'}, status=status.HTTP_400_BAD_REQUEST)

class BotGeneradorPruebas(APIView):
    def get(self, request):
        titulo = request.GET.get('titulo', None)

        if titulo:
            generar_pruebas=DataExtract("https://labs.perplexity.ai")
            generar_pruebas.ingresar_link()
            time.sleep(1)
            generar_pruebas.busqueda_xpath('//*[@id="__next"]/main/div/div/div[2]/div[2]/div/div/div/div/div/div/div/div[1]/textarea').send_keys(f"Hacer una prueba técnica de 15 preguntas, para un {titulo} de tipo selección múltiple, en donde hay un enunciado y 4 posibles respuestas del enunciado, en donde solo una es la correcta.")
            generar_pruebas.busqueda_xpath('//*[@id="lamma-select"]/option[4]').click()
            generar_pruebas.busqueda_xpath('/html/body/div/main/div/div/div[2]/div[2]/div/div/div/div/div/div/div/div[2]/div[2]/button').click()
            time.sleep(60)
            respuesta = generar_pruebas.obtener_pruebas('/html/body/div/main/div/div/div[1]/div/div[2]/div/div/div/div[3]/div/div/div[2]/div[1]')
            generar_pruebas.Cerrar_drive()
            response = generar_pruebas.generar_pdf(titulo, respuesta)
            return response

        else: 

            return Response({'error': titulo}, status=status.HTTP_400_BAD_REQUEST)

class WebScraping(APIView):

    def get(self, request):
        if request.method == 'GET':

            # Computrabajo
            computrabajo = DataExtract("https://co.computrabajo.com/")
            computrabajo.ingresar_link()
            computrabajo.click_banner_button("/html/body/div/div[1]/div/div[1]/div[2]/svg/path[1]")
            computrabajo.busqueda_xpath("/html/body/main/div[2]/div/div/div/div[1]/div/div[1]/form/input[1]").send_keys("Informatica")
            computrabajo.busqueda_xpath("/html/body/main/div[2]/div/div/div/div[1]/div/div[2]/form/input[1]").send_keys("Colombia")
            time.sleep(2)
            computrabajo.click_banner_button("/html/body/div/div[1]/div/div[1]/div[2]/svg/path[1]")
            computrabajo.busqueda_xpath("/html/body/main/div[2]/div/div/div/div[1]/button").click() # buscar
            time.sleep(2)
            computrabajo.click_banner_button("/html/body/main/div[2]/div[2]/div/button[1]")
            time.sleep(1)
            computrabajo.obtener_title_perfiles_paginados('js-o-link',3,'//*[@id="offersGridOfferContainer"]/div[8]/span[2]')
            data_computrabajo = computrabajo.guardar_title_perfiles_paginados()

            # El empleo
            elempleo = DataExtract("https://www.elempleo.com/co/ofertas-empleo")
            elempleo.ingresar_link()
            elempleo.busqueda_xpath("/html/body/header/div/div[2]/div[2]/div/form/div/span/input[2]").send_keys("informática")
            elempleo.busqueda_xpath("/html/body/header/div/div[2]/div[2]/div/form/div/button").click()
            elempleo.scroll_down("/html")
            elempleo.busqueda_xpath("/html/body/div[8]/div[3]/div[1]/div[4]/div/form/div/select").click() # Buscar
            elempleo.busqueda_xpath("/html/body/div[8]/div[3]/div[1]/div[4]/div/form/div/select").click() # 100
            elempleo.busqueda_xpath("/html/body/div[8]/div[3]/div[1]/div[4]/div/form/div/select").send_keys("100") # 100
            time.sleep(2)
            elempleo.obtener_title_perfiles("js-offer-title")
            data_elempleo = elempleo.guardar_title_perfiles()

            # Linkedin
            linkedin = DataExtract('https://www.linkedin.com/jobs/search?trk=guest_homepage-basic_guest_nav_menu_jobs&position=1&pageNum=0')
            linkedin.ingresar_link()
            linkedin.busqueda_id("job-search-bar-keywords").send_keys('Informatica')
            linkedin.busqueda_id("job-search-bar-location").clear()
            linkedin.busqueda_id("job-search-bar-location").send_keys('Colombia')
            linkedin.busqueda_xpath("//*[@id='jobs-search-panel']/form/button").click()
            time.sleep(1)
            linkedin.scroll_down_smoothly()
            linkedin.obtener_title_perfiles('base-search-card__title')
            data_linkedin = linkedin.guardar_title_perfiles()

            #result_json = linkedin.combinar_json(data_linkedin, data_computrabajo, data_elempleo)

            # Unir los DataFrames en uno solo
            data_frames = [data_linkedin, data_elempleo, data_computrabajo]
            df = pd.concat(data_frames, ignore_index=True)

            df = df.dropna(subset=['title']) # Eliminar filas con valores nulos en la columna 'title'

            df = df.map(lambda x: x.lower() if isinstance(x, str) else x) # Se pasa todo el df a minuscula

            # Función para aplicar limpieza a cada celda del DataFrame
            def limpiar_celda(celda):
                if isinstance(celda, str):
                    # Eliminar caracteres que no sean letras o espacios en blanco
                    celda = re.sub(r'[^\w\s]', '', celda)
                    # Eliminar números
                    celda = re.sub(r'\d+', '', celda)
                    # Remover acentos y caracteres especiales
                    celda = unidecode(celda)
                return celda
    
            # Se aplicar limpieza a cada celda del DataFrame
            df = df.map(limpiar_celda)

            conteo = df['title'].value_counts()

            top_10 = conteo.head(10)

            # Convierte los datos a un diccionario
            top_10_dict = top_10.to_dict()

            # Convierte el diccionario a formato JSON
            json_data = json.dumps(top_10_dict, ensure_ascii=False, indent=4)

            # Parsear el JSON
            data = json.loads(json_data)

            # Crear las listas 'titulo' y 'cantidad'
            titulos = list(data.keys())
            cantidades = list(data.values())

            # Crear el nuevo JSON
            json_front = {
                "titulo": titulos,
                "cantidad": cantidades
            }

            # Convertir el nuevo JSON a una cadena JSON
            #nuevo_json_str = json.dumps(json_front, indent=4)

            linkedin.Cerrar_drive()

            return Response(json_front, status=status.HTTP_200_OK)

class BotGeneradorPruebasOpenai(APIView):
    def get(self, request):
        titulo = request.GET.get('titulo', None)
        generar_pruebas=DataExtract("https://platform.openai.com/")

        if titulo:

            response = openai.ChatCompletion.create(
            model="gpt-4-0613",
            messages=[
                    {"role": "system", "content": "Hello"},
                    {"role": "user", "content": f"""
                    Hacer una prueba técnica de 15 preguntas, para un {titulo} de tipo selección múltiple, en donde hay un enunciado y 4 posibles respuestas del enunciado, en donde solo una es la correcta."""
                    }
                ]
            )

            respuesta = response['choices'][0]['message']['content']

            pdf = generar_pruebas.generar_pdf(titulo, respuesta)

            return pdf

        else: 

            return Response({'error': titulo}, status=status.HTTP_400_BAD_REQUEST)