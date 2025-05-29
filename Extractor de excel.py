import pandas as pd
import json
from openai import OpenAI
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class ExcelProductionProcessor:
    def __init__(self, api_key, equipo_value="30"):
        """
        Procesador mejorado para hojas de producción Excel
        
        Args:
            api_key (str): API Key de OpenAI
            equipo_value (str): Valor del equipo por defecto
        """
        self.client = OpenAI(api_key=api_key)
        self.equipo_value = equipo_value
        
    def read_excel_sheets(self, file_path):
        """
        Lee todas las hojas de un archivo Excel
        
        Args:
            file_path (str): Ruta del archivo Excel
            
        Returns:
            dict: Diccionario con los datos de todas las hojas
        """
        try:
            # Leer todas las hojas
            excel_data = pd.read_excel(file_path, sheet_name=None, header=None)
            
            sheets_text = {}
            for sheet_name, df in excel_data.items():
                # Convertir DataFrame a texto preservando estructura
                sheet_content = []
                
                for index, row in df.iterrows():
                    row_data = []
                    for cell in row:
                        if pd.notna(cell):
                            row_data.append(str(cell).strip())
                        else:
                            row_data.append("")
                    
                    # Solo agregar filas que no estén completamente vacías
                    if any(cell for cell in row_data):
                        sheet_content.append("\t".join(row_data))
                
                if sheet_content:
                    sheets_text[sheet_name] = "\n".join(sheet_content)
            
            return sheets_text
            
        except Exception as e:
            print(f"❌ Error al leer Excel: {e}")
            return {}
    
    def process_sheet_with_openai(self, sheet_text, sheet_name):
        """
        Procesa una hoja con OpenAI usando prompt mejorado
        
        Args:
            sheet_text (str): Contenido de la hoja
            sheet_name (str): Nombre de la hoja
            
        Returns:
            list: Datos extraídos y procesados
        """
        
        prompt = f"""Analiza esta hoja de producción Excel y extrae los datos según las siguientes reglas:

CONTENIDO DE LA HOJA:
{sheet_text}

REGLAS DE EXTRACCIÓN:

1. FECHA: 
   - Busca patrones como "FECHA: DIA/MES/AÑO" 
   - Convierte a formato YY-MM-DD (ej: 2025-04-03 → 25-04-03)

2. OPERARIO:
   - Busca "NOMBRE:" seguido del nombre:
   - Extrae solo el nombre (ej: "NELSON RANGEL")

3. OPs y DATOS:
   - Busca líneas con OP, DESCRIPCION, TIEMPO
   - Si una OP tiene múltiples números separados por "-" (ej: 7027-7028-7029), crear un registro separado para cada OP
   - Cada OP debe tener: número, descripción, tiempo

4. DISTRIBUCIÓN DE TIEMPO:
   - Si hay múltiples OPs que comparten tiempo, distribuir equitativamente
   - IMPORTANTE: Los tiempos deben ser en incrementos de 0.5 (0.5, 1, 1.5, 2, 2.5, etc.)
   - Ejemplos:
     * Tiempo 8.5 con 3 OPs → 2.5, 2.5, 3 
     * Tiempo 1.5 con 3 OPs → 0.5, 0.5, 0.5 
IMPORTANTE - DISTRIBUCIÓN DE TIEMPO: Los tiempos deben redistribuirse en incrementos de 0.5 horas únicamente.
   - Si el tiempo total es 8.5 y hay 3 OPs: distribuir como 2, 2, 4.5 (no 2.83 cada una)
   - Siempre usar valores como: 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, etc.
   - Priorizar distribución equilibrada pero ajustada a incrementos de 0.5
   - La suma de las horas de cada OP debe ser el total de horas dadas ejemplo: Tiempo 8.5, 2 OPs → 4, 4.5 total = 8.5
   
   EJEMPLOS DE DISTRIBUCIÓN:
   - Tiempo 8.5, 3 OPs → 2, 2, 4.5
   - Tiempo 7, 2 OPs → 3.5, 3.5
   - Tiempo 9, 4 OPs → 2, 2, 2.5, 2.5
   - Tiempo 5.5, 3 OPs → 1.5, 2, 2

5. CAMPOS REQUERIDOS:
   - fecha: formato YY-MM-DD
   - OP: número de la OP (int → ejemplo: 3 : no debe ser 3.0)
   - operario: nombre en formato "Nombre completo"
   - actividad: descripción de la actividad
   - tiempo_ordinario: tiempo en formato string con incrementos de 0.5
   - tiempo_extra: "0" si no hay tiempo extra especificado
   - equipo: "{self.equipo_value}"

EJEMPLO DE PROCESAMIENTO:
Si encuentras: "7027/7028/7029 REUNION DE SEGUIMIENTO ECOPETROL 1,5"
Debes crear 3 registros separados, cada uno con tiempo 0.5 (mínimo por OP)

FORMATO DE RESPUESTA (JSON válido):
[
  {{
    "fecha": "25-04-03",
    "OP": 7027,
    "operario": "Nelson Rangel",
    "actividad": "REUNION DE SEGUIMIENTO ECOPETROL",
    "tiempo_ordinario": "0.5",
    "tiempo_extra": "0",
    "equipo": "{self.equipo_value}"
  }},
  {{
    "fecha": "25-04-03", 
    "OP": 7028,
    "operario": "Nelson Rangel",
    "actividad": "REUNION DE SEGUIMIENTO ECOPETROL",
    "tiempo_ordinario": "0.5",
    "tiempo_extra": "0",
    "equipo": "{self.equipo_value}"
  }}
]

Responde ÚNICAMENTE con el JSON válido, sin texto adicional."""

        try:
            response = self.client.chat.completions.create(
                #model="o4-mini-2025-04-16",  # Modelo más reciente y eficiente
                model="gpt-4.1-2025-04-14",  # Modelo más reciente y eficiente
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=2000
            )
            
            json_response = response.choices[0].message.content.strip()
            
            # Limpiar respuesta
            if json_response.startswith("```json"):
                json_response = json_response.replace("```json", "").replace("```", "").strip()
            if json_response.startswith("```"):
                json_response = json_response.replace("```", "").strip()
            
            # Parsear JSON
            try:
                data = json.loads(json_response)
                return self.validate_and_fix_times(data)
            except json.JSONDecodeError as e:
                print(f"❌ Error JSON en hoja '{sheet_name}': {e}")
                print(f"Respuesta: {json_response}")
                return []
                
        except Exception as e:
            print(f"❌ Error con OpenAI en hoja '{sheet_name}': {e}")
            return []
    
    def validate_and_fix_times(self, data):
        """
        Valida y corrige los tiempos para que estén en incrementos de 0.5
        
        Args:
            data (list): Lista de registros
            
        Returns:
            list: Registros con tiempos corregidos
        """
        for record in data:
            try:
                tiempo = float(record.get('tiempo_ordinario', 0))
                # Redondear a incrementos de 0.5, mínimo 0.5
                tiempo_corregido = max(0.5, round(tiempo * 2) / 2)
                record['tiempo_ordinario'] = str(tiempo_corregido)
                
                # Asegurar que tiempo_extra sea string
                if 'tiempo_extra' not in record:
                    record['tiempo_extra'] = "0"
                
                # Validar OP como entero
                if 'OP' in record:
                    record['OP'] = int(record['OP'])
                    
            except (ValueError, TypeError):
                record['tiempo_ordinario'] = "0.5"
                record['tiempo_extra'] = "0"
        
        return data
    
    def save_results(self, all_data, operario_name, output_dir="output"):
        """
        Guarda los resultados en archivo JSON
        
        Args:
            all_data (list): Todos los datos procesados
            operario_name (str): Nombre del operario
            output_dir (str): Directorio de salida
            
        Returns:
            str: Ruta del archivo guardado
        """
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{operario_name.lower().replace(' ', '_')}_{timestamp}.json"
        file_path = os.path.join(output_dir, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)
        
        return file_path
    
    def process_excel_file(self, file_path):
        """
        Procesa archivo Excel completo
        
        Args:
            file_path (str): Ruta del archivo Excel
            
        Returns:
            dict: Resultados del procesamiento
        """
        print(f"🚀 Procesando archivo: {os.path.basename(file_path)}")
        
        # Leer hojas
        sheets_data = self.read_excel_sheets(file_path)
        
        if not sheets_data:
            return {"success": False, "error": "No se pudieron leer las hojas del Excel"}
        
        print(f"📄 Hojas encontradas: {list(sheets_data.keys())}")
        
        all_results = []
        operario_name = "desconocido"
        
        # Procesar cada hoja
        for sheet_name, sheet_text in sheets_data.items():
            print(f"⚙️ Procesando: {sheet_name}")
            
            sheet_results = self.process_sheet_with_openai(sheet_text, sheet_name)
            
            if sheet_results:
                all_results.extend(sheet_results)
                
                # Extraer nombre del operario
                if operario_name == "desconocido" and sheet_results:
                    operario_name = sheet_results[0].get('operario', 'desconocido')
                
                print(f"✅ {sheet_name}: {len(sheet_results)} registros extraídos")
            else:
                print(f"⚠️ {sheet_name}: Sin datos extraídos")
        
        if not all_results:
            return {"success": False, "error": "No se extrajeron datos de ninguna hoja"}
        
        # Guardar resultados
        json_file = self.save_results(all_results, operario_name)
        
        # Estadísticas
        total_ops = len(all_results)
        unique_ops = len(set(record['OP'] for record in all_results))
        total_tiempo = sum(float(record['tiempo_ordinario']) for record in all_results)
        fechas_procesadas = list(set(record['fecha'] for record in all_results))
        
        results = {
            "success": True,
            "operario": operario_name,
            "total_registros": total_ops,
            "ops_unicas": unique_ops,
            "tiempo_total": total_tiempo,
            "fechas_procesadas": fechas_procesadas,
            "hojas_procesadas": len(sheets_data),
            "archivo_json": json_file,
            "datos": all_results
        }
        
        print(f"\n🎉 PROCESAMIENTO COMPLETADO")
        print(f"   👤 Operario: {operario_name}")
        print(f"   📊 Registros: {total_ops} ({unique_ops} OPs únicas)")
        print(f"   ⏱️ Tiempo total: {total_tiempo} horas")
        print(f"   📅 Fechas: {', '.join(fechas_procesadas)}")
        print(f"   💾 Guardado en: {json_file}")
        
        return results

def main():
    """Función principal"""
    print("🔧 PROCESADOR DE HOJAS DE PRODUCCIÓN")
    print("=" * 50)
    
    # Configuración - DEBES AGREGAR TU API KEY AQUÍ
    
    api_key = os.getenv("api_key")
    
    if not api_key or api_key == "tu-api-key-aqui":
        print("❌ ERROR: Debes configurar tu API Key de OpenAI")
        print("Edita la línea 'api_key = \"tu-api-key-aqui\"' con tu clave real")
        return
    
    # Archivo a procesar
    file_path = input("📁 Ruta del archivo Excel (o Enter para usar archivo por defecto): ").strip()
    if not file_path:
        file_path = "HOJA DE PRODUCCION ADMON 31-03 AL 23-05 NELSON RANGEL.xlsx"
    
    if not os.path.exists(file_path):
        print(f"❌ Archivo no encontrado: {file_path}")
        return
    
    # Valor del equipo
    equipo_value = input("⚙️ Valor del equipo (Enter para usar '30'): ").strip()
    if not equipo_value:
        equipo_value = "30"
    
    # Procesar
    processor = ExcelProductionProcessor(api_key, equipo_value)
    results = processor.process_excel_file(file_path)
    
    if not results["success"]:
        print(f"❌ Error: {results.get('error', 'Error desconocido')}")
        return
    
    # Mostrar muestra de datos
    print(f"\n📋 MUESTRA DE DATOS PROCESADOS:")
    for i, record in enumerate(results["datos"][:5], 1):
        print(f"   {i}. OP {record['OP']}: {record['operario']} - {record['actividad'][:50]}... ({record['tiempo_ordinario']}h)")
    
    if len(results["datos"]) > 5:
        print(f"   ... y {len(results['datos']) - 5} registros más")
    
    print(f"\n💾 Archivo JSON completo: {results['archivo_json']}")

if __name__ == "__main__":
    main()