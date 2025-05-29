import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class FormAutomation:
    # Selector del botón "Adicionar Operario" (ajusta según tu HTML)
    ADD_OPERATOR_BUTTON_SELECTOR = "/html/body/tu_ruta_al_boton_add_operario"
    ADD_OPERATOR_BUTTON_SELECTOR_TYPE = "xpath"

    def __init__(self):
        """Inicializa el driver de Chrome"""
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        # chrome_options.add_argument("--headless")  # Descomenta para modo headless

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)

    def _select_by_partial_text(self, select_elem: Select, partial_text: str):
        """
        Dado un objeto Select y una subcadena, selecciona la primera opción
        cuyo texto contenga esa subcadena (case-insensitive).
        """
        for option in select_elem.options:
            if partial_text.strip().lower() in option.text.strip().lower():
                select_elem.select_by_visible_text(option.text)
                return
        raise ValueError(f"No se encontró ninguna opción que contenga '{partial_text}'")

    def login(self, url, username, password):
        """Realiza el login en el sitio web"""
        try:
            print(f"Navegando a: {url}")
            self.driver.get(url)
            time.sleep(2)

            # 1) Ingreso de usuario y contraseña
            username_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "txtUsuario"))
            )
            password_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "txtPass"))
            )

            username_field.clear()
            username_field.send_keys(username)
            password_field.clear()
            password_field.send_keys(password)

            # 2) Clic en el botón de login
            login_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/form/div[4]/button"))
            )
            login_button.click()

            print("Login realizado exitosamente")

            # 3) Espera por el botón de reportes y clic en él
            report_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/aside/div/ul/li[8]/a"))
            )
            report_button.click()

            # 4) Fechas
            fecha_i = self.wait.until(
                EC.presence_of_element_located((By.NAME, "txtFechaI"))
            )
            fecha_f = self.wait.until(
                EC.presence_of_element_located((By.NAME, "txtFechaF"))
            )

            fecha_i.clear()
            fecha_i.send_keys("2025-12-01")
            fecha_f.clear()
            fecha_f.send_keys("2025-12-01")

            # 5) Clic en el botón de reporte
            report_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/table/tbody/tr[3]/td/div/input[2]"))
            )
            report_button.click()

            print("Fechas ingresadas exitosamente")

        except TimeoutException:
            print("Error: Tiempo de espera agotado al buscar elementos de login")
        except NoSuchElementException as e:
            print(f"Error: No se encontró el elemento: {e}")

    def load_json_data(self, json_file_path):
        """Carga los datos desde el archivo JSON"""
        try:
            with open(json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            print(f"Datos cargados exitosamente: {len(data)} registros")
            return data
        except FileNotFoundError:
            print(f"Error: No se encontró el archivo {json_file_path}")
            return []
        except json.JSONDecodeError:
            print("Error: El archivo JSON no tiene formato válido")
            return []

    def fill_form(self, record):
        """Llena el formulario con un registro de datos"""
        try:
            # 1) Campo fecha
            fecha_field = self.wait.until(
                EC.element_to_be_clickable((By.NAME, "fecha"))
            )
            fecha_field.clear()
            fecha_field.send_keys(record["fecha"])
            time.sleep(0.5)
            fecha_field.send_keys(Keys.TAB)

            # 2) Campo OP (Select) con búsqueda parcial
            op_elem = self.wait.until(EC.element_to_be_clickable((By.NAME, "cboOPF")))
            op_select = Select(op_elem)
            self._select_by_partial_text(op_select, str(record["OP"]))
            time.sleep(0.5)

            # 3) Campo operario (Select) con búsqueda parcial
            oper_elem = self.wait.until(EC.element_to_be_clickable((By.NAME, "cboOperario")))
            oper_select = Select(oper_elem)
            self._select_by_partial_text(oper_select, record["operario"])
            time.sleep(0.5)

            # 4) Campo actividad
            actividad_field = self.wait.until(
                EC.element_to_be_clickable((By.NAME, "txtActividad"))
            )
            actividad_field.clear()
            actividad_field.send_keys(record["actividad"])
            time.sleep(0.5)

            # 5) Campo tiempo ordinario
            tiempo_ord_field = self.wait.until(
                EC.element_to_be_clickable((By.NAME, "txtTiempoOrdinario"))
            )
            tiempo_ord_field.clear()
            tiempo_ord_field.send_keys(record["tiempo_ordinario"])
            time.sleep(0.5)

            # 6) Campo tiempo extra (opcional)
            if record.get("tiempo_extra"):
                tiempo_extra_field = self.wait.until(
                    EC.element_to_be_clickable((By.NAME, "txtTiempoExtra"))
                )
                tiempo_extra_field.clear()
                tiempo_extra_field.send_keys(record["tiempo_extra"])
                time.sleep(0.5)

            # 7) Campo equipo (Select) con búsqueda parcial
            equipo_elem = self.wait.until(EC.element_to_be_clickable((By.NAME, "cboEquipo")))
            equipo_select = Select(equipo_elem)
            self._select_by_partial_text(equipo_select, record["equipo"])
            time.sleep(0.5)

        except NoSuchElementException as e:
            print(f"Error: No se encontró el campo en el formulario: {e}")
        except Exception as e:
            print(f"Error al llenar el formulario: {e}")

    def click_button(self, button_selector, selector_type="xpath"):
        """Hace click en un botón específico"""
        try:
            if selector_type == "xpath":
                button = self.wait.until(EC.element_to_be_clickable((By.XPATH, button_selector)))
            elif selector_type == "id":
                button = self.wait.until(EC.element_to_be_clickable((By.ID, button_selector)))
            elif selector_type == "name":
                button = self.wait.until(EC.element_to_be_clickable((By.NAME, button_selector)))
            elif selector_type == "class":
                button = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, button_selector)))
            elif selector_type == "css":
                button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, button_selector)))
            else:
                raise ValueError("Tipo de selector no válido")

            button.click()
            print(f"Click realizado en: {button_selector}")
            time.sleep(1)

        except TimeoutException:
            print(f"Error: No se pudo hacer click en {button_selector}")
        except Exception as e:
            print(f"Error al hacer click: {e}")

    def process_all_records(self, json_file_path, submit_each=True):
        """Procesa todos los registros del archivo JSON"""
        data = self.load_json_data(json_file_path)
        if not data:
            return

        for i, record in enumerate(data, 1):
            print(f"\nProcesando registro {i}/{len(data)}")
            self.fill_form(record)

            # Solicitar permiso para adicionar operario
            # print("Formulario completado. Presiona ENTER para adicionar operario y continuar...")
            # input()

            # if submit_each:
            self.click_button("/html/body/div[3]/table/tbody/tr[17]/td/div/input", "xpath")
            time.sleep(2)
            # Esperar a que el siguiente botón esté disponible y hacer clic en él
            print("Añadido con éxito")
            report_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div[3]/table/tbody/tr[3]/td[1]/button"))
            )
            report_button.click()

            # Imprimir mensaje de éxito
            print("Continuando con nuevo registro de operario")
                

    def close(self):
        """Cierra el navegador"""
        self.driver.quit()
        print("Navegador cerrado")


def main():
    URL = "http://192.168.1.85:8181/scp/render.php?frm=acceso.logIn"
    USERNAME = "admin"
    PASSWORD = "123"
    JSON_FILE = "output/nelson_rangel_20250528_164058.json"

    automation = FormAutomation()
    try:
        automation.login(URL, USERNAME, PASSWORD)
        automation.process_all_records(JSON_FILE, submit_each=True)
        print("\nProceso completado exitosamente")
    except Exception as e:
        print(f"Error durante la ejecución: {e}")
    finally:
        time.sleep(5)
        automation.close()

if __name__ == "__main__":
    main()
