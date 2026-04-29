import pandas as pd
import streamlit as st
import sys
import os
from sqlalchemy import text
from constants import *
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
        temp_df["provincia_nombre"] = temp_df["provincia_iso"].map(DICCIONARIO_PROVINCIAS)
        temp_df["provincia_nombre"] = temp_df["provincia_nombre"].fillna(temp_df["provincia_iso"])
        return temp_df
@st.cache_data
def obtener_top_5(df_original, metrica="num_def"):
    top_5 = df_original.groupby("provincia_nombre")[metrica].sum().nlargest(5).reset_index()
    return top_5

@st.cache_data
def get_provincias_list(df_datos):
    """Obtiene la lista única de provincias para el sidebar"""
    nombres = sorted(df_datos["provincia_nombre"].unique().tolist())
    return ["Todas"] + nombres

# --- CARGA INICIAL DE DATOS ---
df = obtener_datos()
lista_provincias = get_provincias_list(df)

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
    df_filtrado = df[df["provincia_nombre"] == provincia_seleccionada].copy()
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
st.divider()
st.header("🏆 Análisis Comparativo (Top 5 Provincias)")

# Creamos dos columnas para poner dos gráficos de "queso"
col_izq, col_der = st.columns(2)

with col_izq:
    st.subheader("Top 5 en Defunciones")
    df_top_def = obtener_top_5(df, "num_def")
    fig_pie_def = px.pie(
        df_top_def,
        values="num_def",
        names="provincia_nombre",
        hole=0.4, # Esto lo convierte en un gráfico de "donnut", más moderno
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    st.plotly_chart(fig_pie_def, use_container_width=True)

with col_der:
    st.subheader("Top 5 en Hospitalizaciones")
    df_top_hosp = obtener_top_5(df, "num_hosp")
    fig_pie_hosp = px.pie(
        df_top_hosp,
        values="num_hosp",
        names="provincia_nombre",
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.Aggrnyl
    )
    st.plotly_chart(fig_pie_hosp, use_container_width=True)

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