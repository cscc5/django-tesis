import time
import platform
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
class Data_extract():
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

    def __init__(self, link):
        """
        Constructor de la clase Data_extract.

        Parámetros:
        - link (str): El enlace (URL) para la navegación web.

        Return: No devuelve ningún valor.
        """
        self.link = link
        
        # Configuración del servicio de Selenium WebDriver en función del sistema operativo
        if platform.system() == "Windows":
            ua = UserAgent()
            user_agent = ua.random
            chrome_options = Options()
            chrome_options.add_argument(f"--user-agent={user_agent}")
            chrome_options.add_argument ('--headless') 
            self.servicio = Service(executable_path=r".\main_app\chromedriver.exe")
        else:
            self.servicio = Service(executable_path="/usr/local/bin/chromedriver")

        # Inicialización del controlador de Chrome
        self.driver = webdriver.Chrome(service=self.servicio,options=chrome_options)
    
    def ingresar_link(self):
        """
        Abre el enlace en el navegador web.

        Return: No devuelve ningún valor.
        """
        return self.driver.get(self.link)
    
    def busqueda_xpath(self, dato):
        """
        Busca un elemento en la página web utilizando XPath.

        Parámetros:
        - dato (str): La expresión XPath utilizada para ubicar el elemento.

        Return: Un objeto que representa el elemento web encontrado.
        """
        return self.driver.find_element(By.XPATH, dato)
    
    def busqueda_id(self, dato):
        """
        Busca un elemento en la página web utilizando su atributo de identificación (ID).

        Parámetros:
        - dato (str): El valor del atributo de identificación (ID) utilizado para ubicar el elemento.

        Return: Un objeto que representa el elemento web encontrado.
        """
        return self.driver.find_element(By.ID, dato)
    
    def scroll_down(self, num, dato):
        """
        Desplaza hacia abajo en la página web un número específico de veces.

        Parámetros:
        - num (int): El número de veces que se realizará el desplazamiento hacia abajo.
        - dato (str): La expresión XPath utilizada para ubicar el elemento donde se realizará el desplazamiento.

        Return: No devuelve ningún valor.
        """
        for i in range(num):
            self.driver.find_element(By.XPATH, dato).send_keys(Keys.END)
            time.sleep(2)

    def Obtener_perfiles(self, title, company, location):
        """
        Obtiene información de perfiles de trabajo (título, empresa, ubicación).

        Parámetros:
        - title (str): La clase de elemento HTML que representa el título del trabajo.
        - company (str): La clase de elemento HTML que representa la empresa del trabajo.
        - location (str): La clase de elemento HTML que representa la ubicación del trabajo.

        Return: No devuelve ningún valor. Los datos extraídos se almacenan en las listas self.title, self.company y self.location.
        """
        self.title = [element.text for element in self.driver.find_elements(By.CLASS_NAME, title)]
        self.location = [element.text for element in self.driver.find_elements(By.CLASS_NAME, location)]
        self.company = [element.text for element in self.driver.find_elements(By.CLASS_NAME, company)]

    def Guardar_df(self):
        """
        Guarda los datos extraídos en un DataFrame de Pandas y luego los exporta a un archivo CSV.

        Parámetros:
        - name (str): El nombre del archivo CSV en el que se guardarán los datos.

        Return: No devuelve ningún valor.
        """
        df_jobs = pd.DataFrame({'title': self.title, 'location': self.location, 'company': self.company})
        return df_jobs.to_json(orient='split')
    
    def Cerrar_drive(self):
        """
        Cierra el controlador del navegador.

        Return: No devuelve ningún valor.
        """
        self.driver.close()
    
    def obtener_perfiles_paginados(self, dato, num, xpath):
        """
        Obtiene perfiles de trabajo en varias páginas web.

        Parámetros:
        - dato (str): La clase de elemento HTML que se extraerá de cada página.
        - num (int): El número de páginas que se recorrerán.
        - xpath (str): La expresión XPath que se utilizará para hacer clic en el botón de paginación.

        Return: No devuelve ningún valor. Los datos extraídos se almacenan en la lista self.text_list.
        """
        self.text_list = [[element.text for element in self.driver.find_elements(By.CLASS_NAME, dato)]]
        for i in range(num):
            self.busqueda_xpath(xpath).click()
            time.sleep(4)
            self.text_list.append([element.text for element in self.driver.find_elements(By.CLASS_NAME, dato)])