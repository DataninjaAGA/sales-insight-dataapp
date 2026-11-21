"""Sales Insight: aplicación interactiva para analizar ventas desde CSV o Excel."""

from io import BytesIO
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# Contrato de datos: una fila representa una venta o transacción.
COLUMNAS_REQUERIDAS = [
    "Fecha", "Region", "Vendedor", "Producto", "Cantidad", "Precio_Unitario"
]

st.set_page_config(
    page_title="Sales Insight | Dashboard de Ventas",
    page_icon="📊",
    layout="wide",
)


@st.cache_data(show_spinner=False)
def leer_archivo(contenido: bytes, nombre_archivo: str) -> pd.DataFrame:
    """Lee un CSV UTF-8 o la primera hoja de un Excel .xlsx."""
    archivo = BytesIO(contenido)

    if nombre_archivo.lower().endswith(".csv"):
        return pd.read_csv(archivo, encoding="utf-8-sig")
    if nombre_archivo.lower().endswith(".xlsx"):
        return pd.read_excel(archivo, engine="openpyxl")

    raise ValueError("El archivo debe tener extensión .csv o .xlsx")


def preparar_datos(datos: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Valida columnas, descarta filas inválidas y calcula las ventas."""
    df = datos.copy()
    df.columns = df.columns.astype(str).str.strip()

    faltantes = [col for col in COLUMNAS_REQUERIDAS if col not in df.columns]
    if faltantes:
        raise ValueError(f"Faltan columnas obligatorias: {', '.join(faltantes)}")

    df = df[COLUMNAS_REQUERIDAS].copy()
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df["Cantidad"] = pd.to_numeric(df["Cantidad"], errors="coerce")
    df["Precio_Unitario"] = pd.to_numeric(df["Precio_Unitario"], errors="coerce")

    for columna in ("Region", "Vendedor", "Producto"):
        df[columna] = df[columna].astype("string").str.strip()

    # No se asumen ventas positivas si la fila contiene datos incompletos.
    campos_texto = df[["Region", "Vendedor", "Producto"]]
    sin_texto = campos_texto.isna().any(axis=1) | campos_texto.eq("").any(axis=1)
    invalidas = (
        df[["Fecha", "Cantidad", "Precio_Unitario"]].isna().any(axis=1)
        | sin_texto
        | (df["Cantidad"] <= 0)
        | (df["Precio_Unitario"] < 0)
    )

    descartadas = int(invalidas.sum())
    df = df.loc[~invalidas].copy()
    df["Ventas"] = df["Cantidad"] * df["Precio_Unitario"]
    return df, descartadas


# 1. Entrada de datos: archivo del usuario o demostración incluida.
st.title("📊 Sales Insight")
st.caption("Análisis interactivo de ventas para apoyar decisiones comerciales.")

with st.sidebar:
    st.header("Datos y filtros")
    archivo_subido = st.file_uploader(
        "Sube tus ventas (CSV o Excel)", type=["csv", "xlsx"]
    )

try:
    if archivo_subido is not None:
        nombre = archivo_subido.name
        contenido = archivo_subido.getvalue()
        st.success(f"Archivo cargado: {nombre}")
    else:
        ruta_demo = Path(__file__).parent / "data" / "ventas_demo.csv"
        nombre = ruta_demo.name
        contenido = ruta_demo.read_bytes()
        st.info("Mostrando datos de demostración. Sube un archivo para analizar tus ventas.")

    datos_originales = leer_archivo(contenido, nombre)
    datos, filas_descartadas = preparar_datos(datos_originales)
except Exception as error:
    st.error(f"No se pudo procesar el archivo: {error}")
    st.stop()

if filas_descartadas:
    st.warning(f"Se omitieron {filas_descartadas} filas con datos inválidos o incompletos.")
if datos.empty:
    st.warning("No hay registros válidos para analizar.")
    st.stop()


# 2. Filtros en barra lateral: región, vendedor y rango de fechas.
with st.sidebar:
    regiones = sorted(datos["Region"].unique().tolist())
    vendedores = sorted(datos["Vendedor"].unique().tolist())

    filtro_regiones = st.multiselect("Región", regiones, default=regiones)
    filtro_vendedores = st.multiselect("Vendedor", vendedores, default=vendedores)

    fecha_minima = datos["Fecha"].min().date()
    fecha_maxima = datos["Fecha"].max().date()
    filtro_fechas = st.date_input(
        "Intervalo de fechas",
        value=(fecha_minima, fecha_maxima),
        min_value=fecha_minima,
        max_value=fecha_maxima,
        format="YYYY-MM-DD",
    )

if not isinstance(filtro_fechas, tuple) or len(filtro_fechas) != 2:
    st.info("Selecciona una fecha de inicio y una fecha de fin.")
    st.stop()

inicio, fin = filtro_fechas
filtrados = datos.loc[
    datos["Region"].isin(filtro_regiones)
    & datos["Vendedor"].isin(filtro_vendedores)
    & datos["Fecha"].dt.date.between(inicio, fin)
].copy()

if filtrados.empty:
    st.warning("No existen ventas para los filtros seleccionados.")
    st.stop()


# 3. Indicadores ejecutivos calculados únicamente con los datos filtrados.
ventas_totales = filtrados["Ventas"].sum()
transacciones = len(filtrados)
ticket_promedio = ventas_totales / transacciones
unidades_vendidas = filtrados["Cantidad"].sum()

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Ventas totales", f"${ventas_totales:,.2f}")
kpi2.metric("Transacciones", f"{transacciones:,}")
kpi3.metric("Ticket promedio", f"${ticket_promedio:,.2f}")
kpi4.metric("Unidades vendidas", f"{unidades_vendidas:,.0f}")
st.caption("Moneda: USD. Cada fila del archivo equivale a una transacción.")


# 4. Tendencia mensual.
st.subheader("Evolución de las ventas")
por_mes = (
    filtrados.assign(Mes=filtrados["Fecha"].dt.to_period("M").dt.to_timestamp())
    .groupby("Mes", as_index=False)["Ventas"]
    .sum()
)
fig_mes = px.line(por_mes, x="Mes", y="Ventas", markers=True)
fig_mes.update_layout(xaxis_title="Mes", yaxis_title="Ventas (USD)")
st.plotly_chart(fig_mes, width="stretch")


# 5. Comparaciones por región y vendedor.
col_izquierda, col_derecha = st.columns(2)

with col_izquierda:
    st.subheader("Ventas por región")
    por_region = (
        filtrados.groupby("Region", as_index=False)["Ventas"]
        .sum().sort_values("Ventas", ascending=False)
    )
    fig_region = px.bar(por_region, x="Region", y="Ventas", color="Region")
    fig_region.update_layout(showlegend=False, yaxis_title="Ventas (USD)")
    st.plotly_chart(fig_region, width="stretch")

with col_derecha:
    st.subheader("Ventas por vendedor")
    por_vendedor = (
        filtrados.groupby("Vendedor", as_index=False)["Ventas"]
        .sum().sort_values("Ventas", ascending=True)
    )
    fig_vendedor = px.bar(
        por_vendedor, x="Ventas", y="Vendedor", orientation="h"
    )
    fig_vendedor.update_layout(xaxis_title="Ventas (USD)")
    st.plotly_chart(fig_vendedor, width="stretch")


# 6. Detalle descargable para auditoría y trabajo fuera de la app.
st.subheader("Detalle de transacciones")
st.dataframe(filtrados.sort_values("Fecha", ascending=False),
             hide_index=True, width="stretch")
st.download_button(
    label="Descargar datos filtrados (CSV)",
    data=filtrados.to_csv(index=False).encode("utf-8-sig"),
    file_name="ventas_filtradas.csv",
    mime="text/csv",
)
