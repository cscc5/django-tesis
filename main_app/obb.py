import time
import platform
import pandas as pd
from selenium import webdriver
from fake_useragent import UserAgent
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
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
            self.servicio = Service(executable_path=r".\main_app\chromedriver.exe")
        else:
            ua = UserAgent()
            user_agent = ua.random
            chrome_options = Options()
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument(f"--user-agent={user_agent}")
            chrome_options.add_argument ('--headless')
            self.servicio = Service(executable_path="/home/cscc/Documents/Projects/Trabajo-de-grado/media/chromedriver-linux64/chromedriver")

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
        return df_jobs.to_json(orient='split', index=False)
    
    def obtener_perfiles_paginados(self, dato, num, xpath):
        self.text_list = [[element.text for element in self.driver.find_elements(By.CLASS_NAME, dato)]]
        for i in range(num):
            self.busqueda_xpath(xpath).click()
            time.sleep(4)
            self.text_list.append([element.text for element in self.driver.find_elements(By.CLASS_NAME, dato)])
            
    def Guardar_perfiles_paginados(self):
        df_jobs = pd.DataFrame(self.text_list)
        return df_jobs.to_json(orient="split", index=False)
        
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