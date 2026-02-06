# 🍄 Sistema de Registro de Parámetros Ambientales para Hongos Comestibles

Aplicación web para el registro y monitoreo de condiciones ambientales en invernaderos de producción de hongos comestibles.

## 📋 Características

- ✅ **Gestión de Invernaderos**: Crear, editar y eliminar invernaderos
- ✅ **Registro de Parámetros**: Temperatura (max/min), Humedad Relativa (max/min) y CO₂
- ✅ **Múltiples registros diarios**: Posibilidad de registrar varias veces al día
- ✅ **Climograma automático**: Gráfica combinada de temperatura y humedad promedio
- ✅ **Gráfica de CO₂**: Visualización de concentración diaria
- ✅ **Exportación a PDF**: Reportes profesionales con gráficas y estadísticas
- ✅ **Persistencia de datos**: Toda la información se guarda automáticamente
- ✅ **Responsive**: Optimizado para usar desde el teléfono móvil

## 🚀 Instalación en Streamlit Cloud (RECOMENDADO)

Esta es la forma más fácil de tener tu app funcionando sin necesidad de instalar nada en tu computadora.

### Paso 1: Crear cuenta en GitHub
1. Ve a [github.com](https://github.com) y crea una cuenta gratuita si no tienes una
2. Verifica tu correo electrónico

### Paso 2: Crear un nuevo repositorio
1. Haz clic en el botón "+" en la esquina superior derecha y selecciona "New repository"
2. Nombre del repositorio: `hongos-registro` (o el nombre que prefieras)
3. Marca la opción "Public"
4. Marca "Add a README file"
5. Haz clic en "Create repository"

### Paso 3: Subir los archivos
1. En tu repositorio, haz clic en "Add file" > "Upload files"
2. Arrastra estos 3 archivos:
   - `app.py`
   - `requirements.txt`
   - `README.md`
3. Escribe un mensaje como "Subir aplicación" en el cuadro de commit
4. Haz clic en "Commit changes"

### Paso 4: Desplegar en Streamlit Cloud
1. Ve a [share.streamlit.io](https://share.streamlit.io)
2. Inicia sesión con tu cuenta de GitHub
3. Haz clic en "New app"
4. Selecciona:
   - Repository: `tu-usuario/hongos-registro`
   - Branch: `main`
   - Main file path: `app.py`
5. Haz clic en "Deploy"
6. ¡Espera 2-3 minutos y tu app estará lista!

### Paso 5: Acceder desde tu teléfono
1. Streamlit te dará una URL como: `https://tu-app.streamlit.app`
2. Guarda esta URL en los favoritos de tu navegador móvil
3. Ahora puedes acceder desde cualquier dispositivo

## 📱 Uso de la Aplicación

### 1. Gestionar Invernaderos
- Ve a la sección "🏭 Gestionar Invernaderos"
- Agrega tus invernaderos (ej: "Invernadero A", "Invernadero B")
- Puedes editar nombres o eliminar invernaderos cuando quieras

### 2. Registrar Datos Diarios
- Ve a "📝 Nuevo Registro"
- Selecciona el invernadero
- Ingresa fecha y hora
- Registra:
  - Temperatura máxima y mínima (°C)
  - Humedad relativa máxima y mínima (%)
  - Concentración de CO₂ (ppm)
- Haz clic en "💾 Guardar Registro"
- Puedes hacer varios registros en el mismo día sin problemas

### 3. Visualizar Gráficas
- Ve a "📊 Visualización"
- Selecciona un invernadero o "Todos"
- Verás:
  - **Climograma**: Temperatura y humedad promedio por día
  - **Gráfica de CO₂**: Concentración promedio diaria
  - **Tabla de datos**: Todos tus registros detallados
- Puedes editar o eliminar registros desde aquí

### 4. Exportar Reportes
- Ve a "📥 Exportar Datos"
- Selecciona el invernadero
- Haz clic en "📄 Generar PDF"
- Descarga tu reporte con:
  - Estadísticas resumen
  - Climograma
  - Gráfica de CO₂
  - Listo para imprimir o añadir a presentaciones

## 💾 Persistencia de Datos

Los datos se guardan automáticamente en un archivo `datos_hongos.json` que Streamlit Cloud mantiene entre sesiones. Sin embargo, es importante hacer respaldos periódicos.

### Hacer respaldo manual:
1. Los datos se guardan en el servidor de Streamlit
2. Para mayor seguridad, exporta PDFs regularmente
3. También puedes descargar el archivo JSON desde el repositorio de GitHub

## 🔧 Instalación Local (Opcional)

Si prefieres correr la app en tu computadora:

```bash
# 1. Instalar Python 3.8 o superior
# Descargar desde: https://www.python.org/downloads/

# 2. Clonar el repositorio
git clone https://github.com/tu-usuario/hongos-registro.git
cd hongos-registro

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar la aplicación
streamlit run app.py
```

La app se abrirá en tu navegador en `http://localhost:8501`

## 📊 Estructura de Datos

Los datos se organizan así:

```json
{
  "invernaderos": ["Invernadero 1", "Invernadero 2"],
  "registros": [
    {
      "id": "20240206153045123456",
      "invernadero": "Invernadero 1",
      "fecha": "2024-02-06",
      "hora": "15:30",
      "temp_max": 25.5,
      "temp_min": 18.2,
      "hr_max": 85.0,
      "hr_min": 65.0,
      "co2": 850
    }
  ]
}
```

## 🎯 Casos de Uso

### Ejemplo 1: Registro normal
- Registras datos una vez al día, siempre a las 8 AM
- La gráfica muestra la evolución diaria

### Ejemplo 2: Múltiples registros
- Lunes: registras a las 8 AM y 6 PM
- Martes: solo registras a las 2 PM
- Miércoles: no registras nada
- Las gráficas calculan automáticamente los promedios donde hay datos

### Ejemplo 3: Reporte anual
- Registras datos durante todo el año
- Al final generas un PDF con el climograma anual completo
- Listo para presentar en tu trabajo

## ⚠️ Notas Importantes

1. **Validación de datos**: La app valida que temp_min ≤ temp_max y hr_min ≤ hr_max
2. **Días sin datos**: No afectan las gráficas, solo se muestran los días con registros
3. **Múltiples registros**: Los promedios se calculan automáticamente
4. **Eliminación**: Al eliminar un invernadero, se borran también todos sus registros

## 🆘 Solución de Problemas

### La app no carga
- Verifica que subiste los 3 archivos correctamente
- Revisa que el archivo se llame exactamente `app.py`
- Espera 2-3 minutos después del deploy

### Los datos desaparecieron
- Streamlit Cloud puede reiniciar ocasionalmente
- Exporta PDFs regularmente como respaldo
- Considera hacer commits al repositorio con los datos

### No puedo exportar PDF
- Verifica que tengas datos registrados
- Asegúrate de que `kaleido` esté en requirements.txt
- Espera a que la app termine de cargar completamente

## 📞 Soporte

Si tienes problemas:
1. Revisa esta guía completa
2. Verifica la [documentación de Streamlit](https://docs.streamlit.io)
3. Revisa que todos los archivos estén correctamente subidos a GitHub

## 📝 Licencia

Este proyecto es de código abierto y está disponible para uso personal y comercial.

---

**¡Listo para empezar a registrar tus datos ambientales! 🍄📊**
