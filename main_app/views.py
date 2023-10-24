# views.py en Django
import json
from .models import Trabajos_Clasificados
import pandas as pd  
from sklearn.model_selection import train_test_split  
from sklearn.feature_extraction.text import CountVectorizer 
from nltk.corpus import stopwords 
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from fake_useragent import UserAgent
import time
from .obb import DataExtract
import openai
from .Keys.Keys import *
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

            ua = UserAgent()

            user_agent = ua.random

            chrome_options = Options()
            chrome_options.add_argument(f"--user-agent={user_agent}")
            chrome_options.add_argument ('--headless')
            service = Service(executable_path=executable_path_linux)
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.get('https://labs.perplexity.ai/')
            time.sleep(6)

            driver.find_element(By.XPATH,"//*[@id='__next']/main/div/div/div[2]/div[2]/div/div/div/div/div/div/div/div[1]/textarea").send_keys(f"hacer una prueba técnica de 15 preguntas, para un {titulo} de tipo selección múltiple, en donde hay un enunciado y 4 posibles respuestas del enunciado, en donde solo una es la correcta.")
            time.sleep(3)

            driver.find_element(By.XPATH,"//*[@id='lamma-select']/option[4]").click()
            time.sleep(3)
            driver.find_element(By.XPATH,'/html/body/div/main/div/div/div[2]/div[2]/div/div/div/div/div/div/div/div[2]/div[2]/button').click()
            time.sleep(20)

            respuesta = driver.find_element(By.XPATH,'/html/body/div/main/div/div/div[1]/div/div[2]/div/div/div/div[3]/div/div/div[2]/div[1]').text
            driver.quit()
            return Response({'resultados': respuesta}, status=status.HTTP_200_OK)
        
        else: 
            
            return Response({'error': titulo}, status=status.HTTP_400_BAD_REQUEST)
            
class WebScraping(APIView):

    def get(self, request):
        if request.method == 'GET':
            # Linkedin
            linkedin = DataExtract('https://www.linkedin.com/jobs/search?trk=guest_homepage-basic_guest_nav_menu_jobs&position=1&pageNum=0')
            linkedin.ingresar_link()
            linkedin.busqueda_id("job-search-bar-keywords").send_keys('Informatica')
            linkedin.busqueda_id("job-search-bar-location").clear()
            linkedin.busqueda_id("job-search-bar-location").send_keys('Colombia')
            linkedin.busqueda_xpath("//*[@id='jobs-search-panel']/form/button").click()
            time.sleep(1)
            linkedin.scroll_down_smoothly()
            linkedin.Obtener_perfiles('base-search-card__title','base-search-card__subtitle','job-search-card__location')
            data_linkedin = linkedin.Guardar_perfiles()

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
            elempleo.Obtener_perfiles("js-offer-title", "info-company-name", "info-city")
            data_elempleo = elempleo.Guardar_perfiles()

            # Computrabajo
            computrabajo = DataExtract("https://co.computrabajo.com/")
            computrabajo.ingresar_link()
            computrabajo.busqueda_xpath("/html/body/main/div[2]/div/div/div/div[1]/div/div[1]/form/input[1]").send_keys("Informatica")
            computrabajo.busqueda_xpath("/html/body/main/div[2]/div/div/div/div[1]/div/div[2]/form/input[1]").send_keys("Colombia")
            computrabajo.busqueda_xpath("/html/body/main/div[2]/div/div/div/div[1]/button").click() # buscar
            time.sleep(2)
            #computrabajo.click_banner_button("/html/body/main/div[2]/div[2]/div/button[1]")
            #time.sleep(1)
            computrabajo.obtener_perfiles_paginados('js-o-link',3,'//*[@id="offersGridOfferContainer"]/div[8]/span[2]')
            data_computrabajo = computrabajo.Guardar_perfiles_paginados()

            # Convertir los JSON a diccionarios de Python
            dict_linkedin = json.loads(data_linkedin)
            dict_computrabajo = json.loads(data_computrabajo)
            dict_elempleo = json.loads(data_elempleo)

            # Combinar los diccionarios en uno solo
            combined_data = {
                "linkedin_data": dict_linkedin,
                "computrabajo_data": dict_computrabajo,
                "elempleo_data": dict_elempleo
            }

            # Convertir el resultado a JSON
            result_json = json.dumps(combined_data)

            return Response(result_json, status=status.HTTP_200_OK)