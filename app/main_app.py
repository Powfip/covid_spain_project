import pandas as pd
import streamlit as st
import sys
import os
from sqlalchemy import text
import plotly.express as px

# 1. AJUSTE DE RUTAS PARA IMPORTAR database_mgr
# Esto permite que la carpeta 'app' vea a 'src' o a la raíz
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.database_mgr import get_engine

# 2. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(
    page_title="COVID-19 Spain Dashboard",
    layout="wide"
)

# Inicio la conexion con la base de datos
engine = get_engine()

# 3. FUNCIONES DE CARGA DE DATOS (Caché para rendimiento)
@st.cache_data
def obtener_datos():
    """Trae los datos crudos por provincia para poder filtrar en la App"""
    query = text("""
    SELECT fecha, provincia_iso, num_casos, num_hosp, num_uci, num_def
    FROM daily_stats
    ORDER BY fecha ASC
    """)
    with engine.connect() as conn:
        temp_df = pd.read_sql(query, con=conn)
        # Conversión crítica a datetime
        temp_df["fecha"] = pd.to_datetime(temp_df["fecha"])
        return temp_df

@st.cache_data
def get_provincias_list():
    """Obtiene la lista única de provincias para el sidebar"""
    query = text("SELECT DISTINCT provincia_iso FROM daily_stats ORDER BY provincia_iso")
    with engine.connect() as conn:
        res_df = pd.read_sql(query, con=conn)
    return ["Todas"] + res_df["provincia_iso"].tolist()

# --- CARGA INICIAL DE DATOS ---
df = obtener_datos()
lista_provincias = get_provincias_list()

# 4. SIDEBAR (CONFIGURACIÓN)
st.sidebar.title("🛠️ Configuración")

# Selector de provincia
provincia_seleccionada = st.sidebar.selectbox(
    "Seleccione una Provincia",
    options=lista_provincias
)

# Selector de fechas (Límites dinámicos basados en el dataframe)
fecha_min = df["fecha"].min().to_pydatetime()
fecha_max = df["fecha"].max().to_pydatetime()

rango_fechas = st.sidebar.slider(
    "Rango de fechas",
    min_value=fecha_min,
    max_value=fecha_max,
    value=(fecha_min, fecha_max)
)

# 5. LÓGICA DE FILTRADO (El "Cerebro" de la App)
if provincia_seleccionada != "Todas":
    # Filtramos por la provincia elegida
    df_filtrado = df[df["provincia_iso"] == provincia_seleccionada].copy()
else:
    # Si es "Todas", agrupamos por fecha y sumamos los valores de todas las provincias
    df_filtrado = df.groupby("fecha").sum(numeric_only=True).reset_index()

# Aplicamos el filtro de rango de fechas del slider
df_filtrado = df_filtrado[
    (df_filtrado["fecha"] >= rango_fechas[0]) &
    (df_filtrado["fecha"] <= rango_fechas[1])
]

# 6. VISUALIZACIÓN (DASHBOARD)
st.title("📊 COVID-19 Spain Dashboard")
st.markdown(f"Mostrando datos para: **{provincia_seleccionada}**")

# Métricas rápidas (KPIs)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Casos", f"{int(df_filtrado['num_casos'].sum()):,}")
with col2:
    st.metric("Total Hospitalizados", f"{int(df_filtrado['num_hosp'].sum()):,}")
with col3:
    st.metric("Total Defunciones", f"{int(df_filtrado['num_def'].sum()):,}")

st.divider()

# Gráfico de Líneas Principal
st.subheader("Evolución Temporal")
# Usamos Plotly para que sea interactivo (zoom, hover)
fig = px.line(
    df_filtrado,
    x="fecha",
    y="num_casos",
    title=f"Curva de contagios: {provincia_seleccionada}",
    labels={"num_casos": "Casos Diarios", "fecha": "Fecha"}
)
st.plotly_chart(fig, use_container_width=True)

# Tabla de datos (opcional para inspección)
with st.expander("Ver datos brutos"):
    st.dataframe(df_filtrado)