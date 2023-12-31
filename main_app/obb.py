import re
import json
import time
import platform
import pandas as pd
from io import BytesIO
from selenium import webdriver
from unidecode import unidecode
from reportlab.lib import colors
from fake_useragent import UserAgent
from django.http import HttpResponse
from reportlab.platypus import PageBreak
from reportlab.lib.pagesizes import letter
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from reportlab.lib.styles import getSampleStyleSheet
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from reportlab.platypus import SimpleDocTemplate, Paragraph
from selenium.webdriver.support import expected_conditions as EC

class DataExtract():

    """
    Clase para extraer datos de perfiles de trabajo utilizando Selenium.

    Atributos:
    - link (str): El enlace (URL) para la navegación web.

    Métodos:
    - __init__(link): Constructor de la clase.
    - ingresar_link(): Abre el enlace en el navegador.
    - busqueda_xpath(dato): Busca un elemento en la página web utilizando XPath.
    - busqueda_id(dato): Busca un elemento en la página web utilizando su atributo de identificación (ID).
    - scroll_down(num, dato): Desplaza hacia abajo en la página web un número específico de veces.
    - Obtener_perfiles(title, company, location): Obtiene información de perfiles de trabajo (título, empresa, ubicación).
    - Guardar_df(name): Guarda los datos extraídos en un archivo CSV.
    - Cerrar_drive(): Cierra el controlador del navegador.
    - obtener_perfiles_paginados(dato, num, xpath): Obtiene perfiles de trabajo en varias páginas web.
    """

    timeout = 30

    def __init__(self, link):

        self.link = link

        if platform.system() == "Windows":
            ua = UserAgent()
            user_agent = ua.random
            chrome_options = Options()
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument(f"--user-agent={user_agent}")
            chrome_options.add_argument ('--headless')
            self.servicio = Service(executable_path=r".\drivers\chromedriver-windows64\chromedriver.exe") 
        else:
            ua = UserAgent()
            user_agent = ua.random
            chrome_options = Options()
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument(f"--user-agent={user_agent}")
            chrome_options.add_argument ('--headless')
            self.servicio = Service(executable_path="./drivers/chromedriver-linux64/chromedriver")

        self.driver = webdriver.Chrome(service=self.servicio,options=chrome_options)

    def ingresar_link(self):
        return self.driver.get(self.link)

    def busqueda_xpath(self, dato):
        try:
            element = WebDriverWait(self.driver, DataExtract.timeout).until(
                EC.presence_of_element_located((By.XPATH, dato))
            )
            return element
        except Exception as e:
            print(f"Error al buscar el elemento con XPATH '{dato}': {str(e)}")
            return None
    
    def busqueda_id(self, dato):
        try:
            element = WebDriverWait(self.driver, DataExtract.timeout).until(
                EC.presence_of_element_located((By.ID, dato))
            )
            return element
        except Exception as e:
            print(f"Error al buscar el elemento con ID '{dato}': {str(e)}")
            return None

    def scroll_down(self, dato):
        previous_scroll_position = 0
        
        while True:
            try:
                element = WebDriverWait(self.driver, DataExtract.timeout).until(
                    EC.presence_of_element_located((By.XPATH, dato))
                )
                element.send_keys(Keys.END)
                time.sleep(3)
                current_scroll_position = self.driver.execute_script("return window.pageYOffset;")
                if current_scroll_position == previous_scroll_position:
                    break

                previous_scroll_position = current_scroll_position
            except Exception as e:
                print(f"Error al desplazar en la página: {str(e)}")
                break

    def Obtener_perfiles(self, title, company, location):
        self.title = [element.text for element in self.driver.find_elements(By.CLASS_NAME, title)]
        self.location = [element.text for element in self.driver.find_elements(By.CLASS_NAME, location)]
        self.company = [element.text for element in self.driver.find_elements(By.CLASS_NAME, company)]

    def Guardar_perfiles(self):
        df_jobs = pd.DataFrame({'title': self.title, 'location': self.location, 'company': self.company})
        return df_jobs.to_json(orient='split')

    def obtener_perfiles_paginados(self, dato, num, xpath):
        self.text_list = [[element.text for element in self.driver.find_elements(By.CLASS_NAME, dato)]]
        for i in range(num):
            self.busqueda_xpath(xpath).click()
            time.sleep(4)
            self.text_list.append([element.text for element in self.driver.find_elements(By.CLASS_NAME, dato)])
            
    def Guardar_perfiles_paginados(self):
        df_jobs = pd.DataFrame(self.text_list)
        return df_jobs.to_json(orient='split')
    
    def obtener_pruebas(self, xpath):
        return self.driver.find_element(By.XPATH, xpath).text

    def switch_screen(self, num):
        return self.driver.switch_to.window(self.driver.window_handles[num])

    def Cerrar_drive(self):
        try:
            self.driver.close()
        except Exception as e:
            print(f"Error al cerrar el navegador de manera segura: {str(e)}")

    def scroll_down_smoothly(self):
        script = "window.scrollBy(0, 1000);"
        
        while True:
            try:
                self.driver.execute_script(script)
                time.sleep(2)
                if self.driver.execute_script("return (window.innerHeight + window.scrollY) >= document.body.scrollHeight;"):
                    break
            except Exception as e:
                print(f"Error al realizar un desplazamiento suave hacia abajo: {str(e)}")
                break

    def click_banner_button(self, xpath):
        try:
            element = WebDriverWait(self.driver, DataExtract.timeout).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            element.click()
        except Exception as e:
            print(f"Error al hacer clic en el botón del banner: {str(e)}")

    def generar_pdf(selft, titulo, respuesta):
        # Crear un objeto BytesIO para almacenar el PDF
        buffer = BytesIO()

        # Crear el objeto PDF con el contenido de respuesta
        doc = SimpleDocTemplate(buffer, pagesize=letter)

        # Definir un estilo de párrafo con formato
        styles = getSampleStyleSheet()
        style = styles["Normal"]
        style.fontName = "Helvetica"  # Tipo de fuente
        style.fontSize = 12  # Tamaño de la fuente
        style.textColor = colors.black  # Color del texto

        # Crear un estilo de título
        title_style = styles["Title"]
        title_style.fontName = "Helvetica-Bold"  # Tipo de fuente en negrita
        title_style.fontSize = 16  # Tamaño de fuente del título
        title_style.alignment = 1  # Alineación al centro

        # Crear una lista de elementos del PDF
        elements = []

        # Agregar el título al PDF
        title_text = f"Prueba técnica para: {titulo}."
        title = Paragraph(title_text, title_style)
        elements.append(title)

        # Establecer un límite de líneas por página
        lines_per_page = 40
        line_count = 0

        # Agregar el contenido de respuesta al PDF
        text_lines = respuesta.split('\n')[2:-1] # Omitir las primeras 2 líneas
        for line in text_lines:
            p = Paragraph(line, style)
            elements.append(p)
            line_count += 1

            if line_count >= lines_per_page:
                elements.append(PageBreak())
                line_count = 0

        # Construir el PDF
        doc.build(elements)

        # Establecer la posición del búfer en el inicio
        buffer.seek(0)

        # Devolver el PDF como una respuesta HTTP en formato PDF descargable
        response = HttpResponse(buffer.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=" Prueba técnica para: {titulo}.pdf"'

        return response
    
    def combinar_json(self, data_linkedin, data_computrabajo, data_elempleo):
            
        # Convertir los JSON a diccionarios de Python
        self.dict_linkedin = json.loads(data_linkedin)
        self.dict_computrabajo = json.loads(data_computrabajo)
        self.dict_elempleo = json.loads(data_elempleo)

        # Combinar los diccionarios en uno solo
        self.combined_data = {
            "linkedin_data": self.dict_linkedin,
            "computrabajo_data": self.dict_computrabajo,
            "elempleo_data": self.dict_elempleo
        }

        # Convertir el resultado a JSON
        combined_data = json.dumps(self.combined_data)
        return combined_data

    def obtener_title_perfiles(self, title):
        self.title = [element.text for element in self.driver.find_elements(By.CLASS_NAME, title)]

    def guardar_title_perfiles(self):
        df_jobs = pd.DataFrame({"title": self.title})
        df_jobs.to_csv(index=False, mode="w")  # Guardar como CSV
        return df_jobs  # Devolver el DataFrame

    def obtener_title_perfiles_paginados(self, dato, num, xpath):
        self.text_list = []  # Inicializa la lista vacía
        self.text_list.extend([element.text for element in self.driver.find_elements(By.CLASS_NAME, dato)])  

        for i in range(num):
            self.busqueda_xpath(xpath).click()
            time.sleep(4)
            self.text_list.extend([element.text for element in self.driver.find_elements(By.CLASS_NAME, dato)])  # Agrega los elementos de la siguiente página

    def guardar_title_perfiles_paginados(self):
        df_jobs = pd.DataFrame({"title": self.text_list})
        df_jobs.to_csv(index=False, mode="w")  # Guardar como CSV
        return df_jobs  # Devolver el DataFrame
    
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