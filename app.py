import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, date
import json
import os
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import plotly.io as pio

# Configuración de la página
st.set_page_config(
    page_title="Registro Ambiental - Hongos",
    page_icon="🍄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Archivo para almacenar datos
DATA_FILE = "datos_hongos.json"

# Funciones para gestión de datos
def cargar_datos():
    """Carga los datos desde el archivo JSON"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "invernaderos": ["Invernadero 1"],
        "registros": []
    }

def guardar_datos(datos):
    """Guarda los datos en el archivo JSON"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

# Inicializar session state
if 'datos' not in st.session_state:
    st.session_state.datos = cargar_datos()

# Funciones para invernaderos
def agregar_invernadero(nombre):
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
    st.session_state.datos["registros"] = [
        r for r in st.session_state.datos["registros"] 
        if r["id"] != registro_id
    ]
    guardar_datos(st.session_state.datos)

def editar_registro(registro_id, temp_max, temp_min, hr_max, hr_min, co2):
    for registro in st.session_state.datos["registros"]:
        if registro["id"] == registro_id:
            registro["temp_max"] = temp_max
            registro["temp_min"] = temp_min
            registro["hr_max"] = hr_max
            registro["hr_min"] = hr_min
            registro["co2"] = co2
            break
    guardar_datos(st.session_state.datos)

# Función para calcular promedios diarios
def calcular_promedios_diarios(invernadero=None):
    registros = st.session_state.datos["registros"]
    if invernadero:
        registros = [r for r in registros if r["invernadero"] == invernadero]
    
    if not registros:
        return pd.DataFrame()
    
    df = pd.DataFrame(registros)
    df['fecha'] = pd.to_datetime(df['fecha'])
    
    # Calcular promedios por día
    promedios = df.groupby('fecha').agg({
        'temp_max': 'mean',
        'temp_min': 'mean',
        'hr_max': 'mean',
        'hr_min': 'mean',
        'co2': 'mean'
    }).reset_index()
    
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
    
    # Humedad Relativa
    fig.add_trace(
        go.Scatter(
            x=datos['fecha'],
            y=datos['hr_promedio'],
            name="Humedad Relativa (%)",
            line=dict(color='blue', width=2),
            mode='lines+markers'
        ),
        secondary_y=True
    )
    
    # Configurar ejes
    fig.update_xaxis(title_text="Fecha")
    fig.update_yaxis(title_text="Temperatura (°C)", secondary_y=False)
    fig.update_yaxis(title_text="Humedad Relativa (%)", secondary_y=True)
    
    fig.update_layout(
        title=f"Climograma - {invernadero_nombre}",
        hovermode='x unified',
        height=500
    )
    
    return fig

# Función para crear gráfica de CO2
def crear_grafica_co2(datos, invernadero_nombre):
    if datos.empty:
        return None
    
    fig = go.Figure(data=[
        go.Bar(
            x=datos['fecha'],
            y=datos['co2'],
            name="CO₂ (ppm)",
            marker_color='green'
        )
    ])
    
    fig.update_layout(
        title=f"Concentración Promedio Diaria de CO₂ - {invernadero_nombre}",
        xaxis_title="Fecha",
        yaxis_title="CO₂ (ppm)",
        height=400
    )
    
    return fig

# Función para generar PDF
def generar_pdf(invernadero_nombre, datos, climograma_fig, co2_fig):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elementos = []
    
    # Estilos
    estilos = getSampleStyleSheet()
    estilo_titulo = ParagraphStyle(
        'CustomTitle',
        parent=estilos['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#2E7D32'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Título
    titulo = Paragraph(f"Reporte Ambiental - {invernadero_nombre}", estilo_titulo)
    elementos.append(titulo)
    elementos.append(Spacer(1, 0.2*inch))
    
    # Información general
    fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
    info = Paragraph(f"<b>Fecha de generación:</b> {fecha_actual}<br/><b>Invernadero:</b> {invernadero_nombre}", estilos['Normal'])
    elementos.append(info)
    elementos.append(Spacer(1, 0.3*inch))
    
    if not datos.empty:
        # Estadísticas resumen
        resumen_data = [
            ['Parámetro', 'Promedio', 'Mínimo', 'Máximo'],
            [
                'Temperatura (°C)',
                f"{datos['temp_promedio'].mean():.1f}",
                f"{datos['temp_promedio'].min():.1f}",
                f"{datos['temp_promedio'].max():.1f}"
            ],
            [
                'Humedad Relativa (%)',
                f"{datos['hr_promedio'].mean():.1f}",
                f"{datos['hr_promedio'].min():.1f}",
                f"{datos['hr_promedio'].max():.1f}"
            ],
            [
                'CO₂ (ppm)',
                f"{datos['co2'].mean():.0f}",
                f"{datos['co2'].min():.0f}",
                f"{datos['co2'].max():.0f}"
            ]
        ]
        
        tabla_resumen = Table(resumen_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        tabla_resumen.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E7D32')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elementos.append(Paragraph("<b>Resumen Estadístico</b>", estilos['Heading2']))
        elementos.append(Spacer(1, 0.1*inch))
        elementos.append(tabla_resumen)
        elementos.append(PageBreak())
        
        # Guardar gráficas como imágenes
        if climograma_fig:
            img_bytes = pio.to_image(climograma_fig, format='png', width=800, height=500)
            img_buffer = BytesIO(img_bytes)
            img = Image(img_buffer, width=6*inch, height=3.75*inch)
            elementos.append(Paragraph("<b>Climograma</b>", estilos['Heading2']))
            elementos.append(Spacer(1, 0.1*inch))
            elementos.append(img)
            elementos.append(PageBreak())
        
        if co2_fig:
            img_bytes = pio.to_image(co2_fig, format='png', width=800, height=400)
            img_buffer = BytesIO(img_bytes)
            img = Image(img_buffer, width=6*inch, height=3*inch)
            elementos.append(Paragraph("<b>Concentración de CO₂</b>", estilos['Heading2']))
            elementos.append(Spacer(1, 0.1*inch))
            elementos.append(img)
    else:
        elementos.append(Paragraph("No hay datos disponibles para este invernadero.", estilos['Normal']))
    
    doc.build(elementos)
    buffer.seek(0)
    return buffer

# INTERFAZ DE USUARIO

st.title("🍄 Registro de Parámetros Ambientales - Hongos Comestibles")

# Sidebar para navegación
st.sidebar.title("📋 Menú")
opcion = st.sidebar.radio(
    "Selecciona una opción:",
    ["📝 Nuevo Registro", "📊 Visualización", "🏭 Gestionar Invernaderos", "📥 Exportar Datos"]
)

# ===== NUEVO REGISTRO =====
if opcion == "📝 Nuevo Registro":
    st.header("Registrar Nuevos Parámetros")
    
    if not st.session_state.datos["invernaderos"]:
        st.warning("⚠️ Primero debes crear al menos un invernadero en la sección 'Gestionar Invernaderos'")
    else:
        with st.form("form_registro"):
            col1, col2 = st.columns(2)
            
            with col1:
                invernadero = st.selectbox("Invernadero", st.session_state.datos["invernaderos"])
                fecha_reg = st.date_input("Fecha", value=date.today())
                hora_reg = st.time_input("Hora", value=datetime.now().time())
            
            with col2:
                st.write("**Temperatura (°C)**")
                temp_max = st.number_input("Máxima", min_value=-10.0, max_value=60.0, value=25.0, step=0.1)
                temp_min = st.number_input("Mínima", min_value=-10.0, max_value=60.0, value=15.0, step=0.1)
            
            col3, col4 = st.columns(2)
            
            with col3:
                st.write("**Humedad Relativa (%)**")
                hr_max = st.number_input("Máxima", min_value=0.0, max_value=100.0, value=80.0, step=0.1, key="hr_max")
                hr_min = st.number_input("Mínima", min_value=0.0, max_value=100.0, value=60.0, step=0.1, key="hr_min")
            
            with col4:
                st.write("**CO₂ (ppm)**")
                co2 = st.number_input("Concentración", min_value=0.0, max_value=5000.0, value=800.0, step=10.0)
            
            submitted = st.form_submit_button("💾 Guardar Registro", use_container_width=True)
            
            if submitted:
                if temp_min > temp_max:
                    st.error("❌ La temperatura mínima no puede ser mayor que la máxima")
                elif hr_min > hr_max:
                    st.error("❌ La humedad mínima no puede ser mayor que la máxima")
                else:
                    agregar_registro(invernadero, fecha_reg, hora_reg, temp_max, temp_min, hr_max, hr_min, co2)
                    st.success("✅ Registro guardado exitosamente")
                    st.rerun()

# ===== VISUALIZACIÓN =====
elif opcion == "📊 Visualización":
    st.header("Visualización de Datos")
    
    if not st.session_state.datos["invernaderos"]:
        st.warning("⚠️ No hay invernaderos registrados")
    else:
        invernadero_sel = st.selectbox("Selecciona un invernadero", ["Todos"] + st.session_state.datos["invernaderos"])
        
        # Filtrar datos
        if invernadero_sel == "Todos":
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
            registros = st.session_state.datos["registros"]
            if invernadero_sel != "Todos":
                registros = [r for r in registros if r["invernadero"] == invernadero_sel]
            
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
                
                registro_actual = registros[registro_seleccionado]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    with st.expander("✏️ Editar Registro"):
                        with st.form(f"form_editar_{registro_actual['id']}"):
                            new_temp_max = st.number_input("Temp. Máxima", value=float(registro_actual['temp_max']), step=0.1)
                            new_temp_min = st.number_input("Temp. Mínima", value=float(registro_actual['temp_min']), step=0.1)
                            new_hr_max = st.number_input("HR Máxima", value=float(registro_actual['hr_max']), step=0.1)
                            new_hr_min = st.number_input("HR Mínima", value=float(registro_actual['hr_min']), step=0.1)
                            new_co2 = st.number_input("CO₂", value=float(registro_actual['co2']), step=10.0)
                            
                            if st.form_submit_button("💾 Guardar Cambios"):
                                editar_registro(
                                    registro_actual['id'],
                                    new_temp_max, new_temp_min,
                                    new_hr_max, new_hr_min, new_co2
                                )
                                st.success("✅ Registro actualizado")
                                st.rerun()
                
                with col2:
                    st.write("")
                    st.write("")
                    if st.button("🗑️ Eliminar Registro", type="secondary", use_container_width=True):
                        eliminar_registro(registro_actual['id'])
                        st.success("✅ Registro eliminado")
                        st.rerun()

# ===== GESTIONAR INVERNADEROS =====
elif opcion == "🏭 Gestionar Invernaderos":
    st.header("Gestión de Invernaderos")
    
    # Agregar nuevo invernadero
    with st.expander("➕ Agregar Nuevo Invernadero", expanded=True):
        with st.form("form_nuevo_invernadero"):
            nuevo_nombre = st.text_input("Nombre del invernadero")
            if st.form_submit_button("💾 Agregar"):
                if agregar_invernadero(nuevo_nombre):
                    st.success(f"✅ Invernadero '{nuevo_nombre}' agregado")
                    st.rerun()
                else:
                    st.error("❌ Nombre inválido o ya existe")
    
    # Lista de invernaderos existentes
    if st.session_state.datos["invernaderos"]:
        st.subheader("Invernaderos Existentes")
        
        for inv in st.session_state.datos["invernaderos"]:
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"🏭 **{inv}**")
            
            with col2:
                with st.popover("✏️ Editar"):
                    with st.form(f"form_editar_inv_{inv}"):
                        nuevo_nombre = st.text_input("Nuevo nombre", value=inv)
                        if st.form_submit_button("💾 Guardar"):
                            if editar_invernadero(inv, nuevo_nombre):
                                st.success("✅ Actualizado")
                                st.rerun()
                            else:
                                st.error("❌ Error al actualizar")
            
            with col3:
                if st.button("🗑️", key=f"del_{inv}"):
                    if len(st.session_state.datos["invernaderos"]) > 1:
                        eliminar_invernadero(inv)
                        st.success(f"✅ Invernadero '{inv}' eliminado")
                        st.rerun()
                    else:
                        st.error("❌ Debes tener al menos un invernadero")
    else:
        st.info("ℹ️ No hay invernaderos registrados")

# ===== EXPORTAR DATOS =====
elif opcion == "📥 Exportar Datos":
    st.header("Exportar Datos a PDF")
    
    if not st.session_state.datos["invernaderos"]:
        st.warning("⚠️ No hay invernaderos registrados")
    else:
        invernadero_exp = st.selectbox("Selecciona un invernadero", st.session_state.datos["invernaderos"])
        
        datos_prom = calcular_promedios_diarios(invernadero_exp)
        
        if datos_prom.empty:
            st.info("ℹ️ No hay datos para exportar de este invernadero")
        else:
            st.write(f"**Total de días registrados:** {len(datos_prom)}")
            st.write(f"**Período:** {datos_prom['fecha'].min().strftime('%d/%m/%Y')} - {datos_prom['fecha'].max().strftime('%d/%m/%Y')}")
            
            if st.button("📄 Generar PDF", type="primary", use_container_width=True):
                with st.spinner("Generando PDF..."):
                    fig_clima = crear_climograma(datos_prom, invernadero_exp)
                    fig_co2 = crear_grafica_co2(datos_prom, invernadero_exp)
                    
                    pdf_buffer = generar_pdf(invernadero_exp, datos_prom, fig_clima, fig_co2)
                    
                    st.download_button(
                        label="⬇️ Descargar PDF",
                        data=pdf_buffer,
                        file_name=f"Reporte_{invernadero_exp}_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                    
                    st.success("✅ PDF generado exitosamente")

# Footer
st.sidebar.markdown("---")
st.sidebar.info(f"📊 Total de registros: {len(st.session_state.datos['registros'])}")
st.sidebar.info(f"🏭 Invernaderos: {len(st.session_state.datos['invernaderos'])}")
