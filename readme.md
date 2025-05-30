# 🤖 Sistema de Extracción de Datos y Automatización Web

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Selenium](https://img.shields.io/badge/Selenium-4.0%2B-green.svg)](https://selenium-python.readthedocs.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()
[![Maintenance](https://img.shields.io/badge/Maintained-Yes-green.svg)]()

Un sistema automatizado para extraer datos de archivos Excel/CSV y llenar formularios web de manera automática utilizando Selenium WebDriver.

---

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Tecnologías](#-tecnologías)
- [Requisitos Previos](#-requisitos-previos)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Uso](#-uso)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Personalización](#-personalización)
- [Solución de Problemas](#-solución-de-problemas)
- [Licencia](#-licencia)
- [Autor](#-autor)

---

## ✨ Características

- 🔄 **Extracción Automatizada**: Lee datos desde archivos Excel (.xlsx, .xls) y CSV
- 🌐 **Automatización Web**: Llena formularios web automáticamente usando Selenium
- 🔐 **Login Automático**: Maneja autenticación en sitios web
- 📊 **Procesamiento JSON**: Convierte datos Excel/CSV a formato JSON estructurado
- ⌨️ **Simulación de Teclado**: Simula teclas como TAB, ENTER para navegación natural
- 🛡️ **Manejo de Errores**: Sistema robusto de manejo de excepciones
- 📝 **Logging Detallado**: Seguimiento completo del proceso de automatización
- 🔧 **Configuración Flexible**: Fácil adaptación a diferentes formularios web

---

## 🛠️ Tecnologías

![Python](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)
![Selenium](https://img.shields.io/badge/Selenium-43B02A?style=for-the-badge&logo=selenium&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2C2D72?style=for-the-badge&logo=pandas&logoColor=white)
![JSON](https://img.shields.io/badge/JSON-5E5C5C?style=for-the-badge&logo=json&logoColor=white)

### Librerías Principales

- **Selenium**: Automatización de navegadores web
- **Pandas**: Manipulación y análisis de datos
- **OpenPyXL**: Lectura de archivos Excel
- **WebDriver Manager**: Gestión automática de drivers
- **JSON**: Procesamiento de datos estructurados

---

## 📋 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:

- ![Python](https://img.shields.io/badge/Python-3.8+-blue) Python 3.8 o superior
- ![Chrome](https://img.shields.io/badge/Chrome-Latest-red) Google Chrome (última versión)
- ![Git](https://img.shields.io/badge/Git-Latest-orange) Git para clonar el repositorio

---

## 🚀 Instalación

### 1. Clonar el Repositorio

```bash
git clone https://github.com/Jonatan1014/Automatizacion-Ingenieria-SCP.git
cd Automatizacion-Ingenieria-SCP
```

### 2. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 3. Verificar Instalación

```bash
python --version
pip list
```

---

## ⚙️ Configuración

### 1. Configuración de Credenciales

Edita el archivo `Registro de datos.py` o directamente en `main()`:

```python
# Configuración del sitio web
URL = "http://tu-sitio-web.com/login"
USERNAME = "tu_usuario"
PASSWORD = "tu_contraseña"

# Archivo de datos
JSON_FILE = "ruta/a/tu/archivo.json"
EXCEL_FILE = "ruta/a/tu/archivo.xlsx"
```

### 2. Personalizar Selectores Web

Ajusta los selectores en `Registro de datos.py` según tu formulario:

```python
def fill_form(self, record):
    # Personaliza estos selectores según tu formulario
    fecha_field = self.driver.find_element(By.NAME, "fecha")
    op_field = self.driver.find_element(By.NAME, "cboOPF")
    # ... más campos
```

### 3. Estructura de Datos JSON

El sistema espera datos en el siguiente formato:

```json
[
  {
    "fecha": "25-03-31",
    "OP": 7027,
    "operario": "NELSON",
    "actividad": "PLANOS PLATAFORMAS Y ESCALERAS",
    "tiempo_ordinario": "3.0",
    "tiempo_extra": "0",
    "equipo": "30"
  }
]
```

---

## 🎯 Uso

### Uso Básico

```bash
# Ejecutar extracción de Excel a JSON
python Extractor de excel.py

# Ejecutar automatización web
python Registro de datos.py
```

---

## 📁 Estructura del Proyecto

```
Automatizacion-Ingenieria-SCP/
├── 📄 README.md
├── 📄 requirements.txt
├── 🐍 Registro de datos.py
├── 🐍 Extractor de excel.py
├── ⚙ .env
├── 📁 Formato/
│   └── 📄 Formato Horas Ingenieria.xlsx
└── 📁 output/
    └── 📊 dilan_eduardo_botello_ramirez_20250530_133855.json

```

---

## 🔧 Personalización

### Agregar Nuevos Campos

```python
def fill_form(self, record):
    # Campo existente
    fecha_field = self.driver.find_element(By.NAME, "fecha")
    fecha_field.send_keys(record["fecha"])
    
    # Nuevo campo personalizado
    nuevo_campo = self.driver.find_element(By.NAME, "nuevo_campo")
    nuevo_campo.send_keys(record["nuevo_valor"])
```

### Manejo de Dropdowns

```python
from selenium.webdriver.support.ui import Select

dropdown = Select(self.driver.find_element(By.NAME, "dropdown"))
dropdown.select_by_visible_text(record["opcion"])
```

### Elementos Dinámicos

```python
# Esperar elemento dinámico
element = WebDriverWait(self.driver, 10).until(
    EC.presence_of_element_located((By.ID, "dynamic-element"))
)
```

---

## 🐛 Solución de Problemas

### Problemas Comunes

| Problema | Solución |
|----------|----------|
| ChromeDriver no encontrado | Instalar `webdriver-manager` |
| Elemento no encontrado | Verificar selectores CSS/XPath |
| Timeout en carga | Aumentar tiempo de espera |
| Datos no cargados | Verificar formato JSON/Excel |

### Debugging

```python
# Habilitar logs detallados
import logging
logging.basicConfig(level=logging.DEBUG)

# Modo headless deshabilitado para debugging
chrome_options.add_argument("--headless")  # Comentar esta línea
```

## 📄 Licencia

Este proyecto está bajo la derechos de autor.

```
MIT License

Copyright (c) 2025 Jonatan Cantillo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

---

## 👤 Autor

**Jonatan Cantillo**
- GitHub: [@Jonatan1014](https://github.com/Jonatan1014)
- LinkedIn: [Jonatan Cantillo](https://www.linkedin.com/in/jonatan-cantillo/)
- Email: jcantillocompany@gmail.com

---

## 📞 Soporte

¿Necesitas ayuda? 

- 📧 [Contacto Directo](mailto:jcantillocompany@gmail.com)

---

## 🙏 Agradecimientos

- [Selenium WebDriver](https://selenium.dev/) por la excelente herramienta de automatización
- [Pandas](https://pandas.pydata.org/) por el procesamiento de datos
- [WebDriver Manager](https://github.com/SergeyPirogov/webdriver_manager) por simplificar la gestión de drivers
- Comunidad open source por las librerías y herramientas

---

## 📈 Estadísticas del Proyecto

![GitHub stars](https://img.shields.io/github/stars/Jonatan1014/Automatizacion-Ingenieria-SCP?style=social)
![GitHub forks](https://img.shields.io/github/forks/Jonatan1014/Automatizacion-Ingenieria-SCP?style=social)
![GitHub issues](https://img.shields.io/github/issues/Jonatan1014/Automatizacion-Ingenieria-SCP)
![GitHub pull requests](https://img.shields.io/github/issues-pr/Jonatan1014/Automatizacion-Ingenieria-SCP)

---

<div align="center">

**⭐ Si este proyecto te fue útil, no olvides darle una estrella ⭐**

Made with ❤️ by [Jonatan1014](https://github.com/Jonatan1014)

</div>