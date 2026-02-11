 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/app.py b/app.py
index 9ba2d422f1f64dbb35289ca8067fd337f9b81cd1..bbf25b3e39bbe38a3e5eeefc67ba9f71c2ca1d6d 100644
--- a/app.py
+++ b/app.py
@@ -1,157 +1,176 @@
 import streamlit as st
 import pandas as pd
 import plotly.graph_objects as go
 from plotly.subplots import make_subplots
 from datetime import datetime, date
 import json
 import os
 from io import BytesIO
-from reportlab.lib.pagesizes import letter, A4
-from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
+from reportlab.lib.pagesizes import A4
+from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
 from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
 from reportlab.lib.units import inch
 from reportlab.lib import colors
-from reportlab.lib.enums import TA_CENTER, TA_LEFT
+from reportlab.lib.enums import TA_CENTER
 
 # Configuración de la página
 st.set_page_config(
     page_title="Registro Ambiental - Hongos",
     page_icon="🍄",
     layout="wide",
     initial_sidebar_state="expanded"
 )
 
 # Archivo para almacenar datos
 DATA_FILE = "datos_hongos.json"
+METRICAS = ('temp_max', 'temp_min', 'hr_max', 'hr_min', 'co2')
 
 # Funciones para gestión de datos
 def cargar_datos():
-    """Carga los datos desde el archivo JSON"""
-    if os.path.exists(DATA_FILE):
-        with open(DATA_FILE, 'r', encoding='utf-8') as f:
-            return json.load(f)
-    return {
+    """Carga los datos desde el archivo JSON."""
+    datos_iniciales = {
         "invernaderos": ["Invernadero 1"],
         "registros": []
     }
 
+    if not os.path.exists(DATA_FILE):
+        return datos_iniciales
+
+    try:
+        with open(DATA_FILE, 'r', encoding='utf-8') as f:
+            datos = json.load(f)
+    except (json.JSONDecodeError, OSError):
+        return datos_iniciales
+
+    if not isinstance(datos, dict):
+        return datos_iniciales
+
+    datos.setdefault("invernaderos", ["Invernadero 1"])
+    datos.setdefault("registros", [])
+
+    if not datos["invernaderos"]:
+        datos["invernaderos"] = ["Invernadero 1"]
+
+    return datos
+
 def guardar_datos(datos):
     """Guarda los datos en el archivo JSON"""
     with open(DATA_FILE, 'w', encoding='utf-8') as f:
         json.dump(datos, f, ensure_ascii=False, indent=2)
 
+def obtener_registros(invernadero=None):
+    """Obtiene los registros, opcionalmente filtrados por invernadero."""
+    registros = st.session_state.datos["registros"]
+    if invernadero:
+        return [r for r in registros if r["invernadero"] == invernadero]
+    return registros
+
 # Inicializar session state
 if 'datos' not in st.session_state:
     st.session_state.datos = cargar_datos()
 
 # Funciones para invernaderos
 def agregar_invernadero(nombre):
+    nombre = nombre.strip()
     if nombre and nombre not in st.session_state.datos["invernaderos"]:
         st.session_state.datos["invernaderos"].append(nombre)
         guardar_datos(st.session_state.datos)
         return True
     return False
 
 def eliminar_invernadero(nombre):
     if nombre in st.session_state.datos["invernaderos"]:
         st.session_state.datos["invernaderos"].remove(nombre)
         # Eliminar también los registros asociados
         st.session_state.datos["registros"] = [
             r for r in st.session_state.datos["registros"] 
             if r["invernadero"] != nombre
         ]
         guardar_datos(st.session_state.datos)
         return True
     return False
 
 def editar_invernadero(nombre_viejo, nombre_nuevo):
+    nombre_nuevo = nombre_nuevo.strip()
     if nombre_nuevo and nombre_nuevo not in st.session_state.datos["invernaderos"]:
         idx = st.session_state.datos["invernaderos"].index(nombre_viejo)
         st.session_state.datos["invernaderos"][idx] = nombre_nuevo
         # Actualizar registros
         for registro in st.session_state.datos["registros"]:
             if registro["invernadero"] == nombre_viejo:
                 registro["invernadero"] = nombre_nuevo
         guardar_datos(st.session_state.datos)
         return True
     return False
 
 # Funciones para registros
 def agregar_registro(invernadero, fecha, hora, temp_max, temp_min, hr_max, hr_min, co2):
     registro = {
         "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
         "invernadero": invernadero,
         "fecha": fecha.strftime("%Y-%m-%d"),
         "hora": hora.strftime("%H:%M"),
         "temp_max": temp_max,
         "temp_min": temp_min,
         "hr_max": hr_max,
         "hr_min": hr_min,
         "co2": co2
     }
     st.session_state.datos["registros"].append(registro)
     guardar_datos(st.session_state.datos)
 
 def eliminar_registro(registro_id):
-    st.session_state.datos["registros"] = [
-        r for r in st.session_state.datos["registros"] 
-        if r["id"] != registro_id
-    ]
-    guardar_datos(st.session_state.datos)
+    registros = st.session_state.datos["registros"]
+    nuevos_registros = [r for r in registros if r["id"] != registro_id]
+    if len(nuevos_registros) != len(registros):
+        st.session_state.datos["registros"] = nuevos_registros
+        guardar_datos(st.session_state.datos)
 
 def editar_registro(registro_id, temp_max, temp_min, hr_max, hr_min, co2):
     for registro in st.session_state.datos["registros"]:
         if registro["id"] == registro_id:
             registro["temp_max"] = temp_max
             registro["temp_min"] = temp_min
             registro["hr_max"] = hr_max
             registro["hr_min"] = hr_min
             registro["co2"] = co2
+            guardar_datos(st.session_state.datos)
             break
-    guardar_datos(st.session_state.datos)
 
 # Función para calcular promedios diarios
 def calcular_promedios_diarios(invernadero=None):
-    registros = st.session_state.datos["registros"]
-    if invernadero:
-        registros = [r for r in registros if r["invernadero"] == invernadero]
+    registros = obtener_registros(invernadero)
     
     if not registros:
         return pd.DataFrame()
     
-    df = pd.DataFrame(registros)
+    df = pd.DataFrame.from_records(registros)
     df['fecha'] = pd.to_datetime(df['fecha'])
     
     # Calcular promedios por día
-    promedios = df.groupby('fecha').agg({
-        'temp_max': 'mean',
-        'temp_min': 'mean',
-        'hr_max': 'mean',
-        'hr_min': 'mean',
-        'co2': 'mean'
-    }).reset_index()
+    promedios = df.groupby('fecha')[list(METRICAS)].mean().reset_index()
     
     # Calcular temperatura promedio y HR promedio
     promedios['temp_promedio'] = (promedios['temp_max'] + promedios['temp_min']) / 2
     promedios['hr_promedio'] = (promedios['hr_max'] + promedios['hr_min']) / 2
     
     return promedios.sort_values('fecha')
 
 # Función para crear climograma
 def crear_climograma(datos, invernadero_nombre):
     if datos.empty:
         return None
     
     fig = make_subplots(specs=[[{"secondary_y": True}]])
     
     # Temperatura
     fig.add_trace(
         go.Scatter(
             x=datos['fecha'],
             y=datos['temp_promedio'],
             name="Temperatura (°C)",
             line=dict(color='red', width=2),
             mode='lines+markers'
         ),
         secondary_y=False
     )
@@ -379,53 +398,51 @@ elif opcion == "📊 Visualización":
             datos_prom = calcular_promedios_diarios()
             titulo_inv = "Todos los Invernaderos"
         else:
             datos_prom = calcular_promedios_diarios(invernadero_sel)
             titulo_inv = invernadero_sel
         
         if datos_prom.empty:
             st.info("ℹ️ No hay datos registrados para este invernadero")
         else:
             # Climograma
             st.subheader("Climograma")
             fig_clima = crear_climograma(datos_prom, titulo_inv)
             if fig_clima:
                 st.plotly_chart(fig_clima, use_container_width=True)
             
             # Gráfica CO2
             st.subheader("Concentración de CO₂")
             fig_co2 = crear_grafica_co2(datos_prom, titulo_inv)
             if fig_co2:
                 st.plotly_chart(fig_co2, use_container_width=True)
             
             # Tabla de datos
             st.subheader("Datos Detallados")
             
             # Mostrar todos los registros
-            registros = st.session_state.datos["registros"]
-            if invernadero_sel != "Todos":
-                registros = [r for r in registros if r["invernadero"] == invernadero_sel]
+            registros = obtener_registros(None if invernadero_sel == "Todos" else invernadero_sel)
             
             if registros:
                 df_registros = pd.DataFrame(registros)
                 df_registros = df_registros.sort_values(['fecha', 'hora'], ascending=[False, False])
                 
                 st.dataframe(
                     df_registros[['fecha', 'hora', 'invernadero', 'temp_max', 'temp_min', 'hr_max', 'hr_min', 'co2']],
                     use_container_width=True,
                     hide_index=True
                 )
                 
                 # Opciones de edición y eliminación
                 st.subheader("Editar/Eliminar Registros")
                 
                 # Crear opciones más legibles
                 opciones_registros = [
                     f"{r['fecha']} {r['hora']} - {r['invernadero']}" 
                     for r in registros
                 ]
                 
                 registro_seleccionado = st.selectbox(
                     "Selecciona un registro",
                     range(len(registros)),
                     format_func=lambda x: opciones_registros[x]
                 )
 
EOF
)
