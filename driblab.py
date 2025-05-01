import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
from io import BytesIO

st.set_page_config(page_title="Análisis Driblab", layout="wide")

# ======================
# 🧼 LIMPIEZA Y CARGA
# ======================
@st.cache_data
def cargar_datos():
    df_fisico = pd.read_excel("Driblab_Argentina_2025_Fisico.xlsx")
    df_eventos = pd.read_excel("Driblab_Argentina_2025.xlsx")

    df_fisico.columns = df_fisico.columns.str.strip()
    df_eventos.columns = df_eventos.columns.str.strip()

    df_fisico = df_fisico.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    df_eventos = df_eventos.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    mapa_macro = {
        "GK": "Arquero", "DC": "Defensor Central", "DL": "Lateral Izquierdo", "DR": "Lateral Derecho",
        "DMC": "Mediocampista Defensivo", "MC": "Mediocampista Mixto", "ML": "Mediocampista Mixto",
        "MR": "Mediocampista Mixto", "AMC": "Mediocampista Ofensivo", "AML": "Extremo", "AMR": "Extremo",
        "FW": "Delantero", "CF": "Delantero", "ST": "Delantero"
    }

    df_fisico["Macroposición"] = df_fisico["Posición"].map(mapa_macro)
    df_eventos["Macroposición"] = df_eventos["Posición"].map(mapa_macro)

    return df_fisico, df_eventos

df_fisico, df_eventos = cargar_datos()

# ======================
# 🎛️ INTERFAZ
# ======================
st.title("🔎 Análisis de Jugadores – Driblab")

seccion = st.sidebar.radio("Seleccionar sección", ["Datos físicos", "Eventos"])
df = df_fisico if seccion == "Datos físicos" else df_eventos

macro_disponibles = df["Macroposición"].dropna().unique().tolist()
if not macro_disponibles:
    st.sidebar.selectbox("Macroposición", ["Sin datos"])
    st.warning("⚠️ No hay jugadores con minutos válidos en esta categoría.")
    st.stop()

macroposicion = st.sidebar.selectbox("Macroposición", sorted(macro_disponibles))
df_filtrado = df[df["Macroposición"] == macroposicion].copy()

df_filtrado["Minutos"] = pd.to_numeric(df_filtrado["Minutos"], errors="coerce")
df_filtrado = df_filtrado[df_filtrado["Minutos"] >= 0]

if df_filtrado.empty:
    st.warning("⚠️ No hay jugadores con minutos válidos en esta categoría.")
    st.stop()

# ======================
# 🎯 FILTROS Y MÉTRICA
# ======================
min_min = int(df_filtrado["Minutos"].min())
max_min = int(df_filtrado["Minutos"].max())
rango_min = st.sidebar.slider("Rango de minutos jugados", min_min, max_min, (min_min, max_min))
df_filtrado = df_filtrado[(df_filtrado["Minutos"] >= rango_min[0]) & (df_filtrado["Minutos"] <= rango_min[1])]

jugadores = df_filtrado["Nombre"].dropna().unique().tolist()
jugador_destacado = st.sidebar.selectbox("Destacar", sorted(jugadores))

columnas_excluir = ["Nombre", "Equipo", "Edad", "Minutos", "Macroposición"]
columnas_metricas = [col for col in df_filtrado.columns if col not in columnas_excluir and pd.api.types.is_numeric_dtype(df_filtrado[col])]
metrica = st.sidebar.selectbox("Seleccionar métrica", sorted(columnas_metricas))

# ======================
# 📊 VISUALIZACIÓN
# ======================

valores = pd.to_numeric(df_filtrado[metrica], errors="coerce")
p25, p75 = np.nanpercentile(valores.dropna(), [25, 75])

def asignar_color(valor, nombre):
    if nombre == jugador_destacado:
        return "black"
    elif valor <= p25:
        return "#e74c3c"
    elif valor >= p75:
        return "#2ecc71"
    else:
        return "#f1c40f"

df_filtrado["ColorInterior"] = df_filtrado.apply(lambda row: asignar_color(row[metrica], row["Nombre"]), axis=1)
df_filtrado["Tamanio"] = df_filtrado["Nombre"].apply(lambda x: 15 if x == jugador_destacado else 9)
df_filtrado["Borde"] = df_filtrado["Equipo"].apply(lambda eq: "purple" if eq == "River Plate" else "rgba(0,0,0,0)")

fig = go.Figure(data=go.Scatter(
    x=df_filtrado[metrica],
    y=np.random.uniform(-0.5, 0.5, size=len(df_filtrado)),
    mode='markers',
    marker=dict(
        color=df_filtrado["ColorInterior"],
        size=df_filtrado["Tamanio"],
        line=dict(color=df_filtrado["Borde"], width=2)
    ),
    text=df_filtrado["Nombre"],
    hovertemplate="<b>%{text}</b><br>" + f"{metrica}: %{{x:.2f}}" + "<extra></extra>",
))

fig.update_layout(
    xaxis_title=metrica,
    yaxis=dict(showticklabels=False),
    height=400,
    plot_bgcolor="white"
)

st.plotly_chart(fig, use_container_width=True)

# ======================
# 📋 TABLA DE DATOS
# ======================
st.dataframe(df_filtrado[["Nombre", "Equipo", "Minutos", metrica]].sort_values(by=metrica, ascending=False), use_container_width=True)


