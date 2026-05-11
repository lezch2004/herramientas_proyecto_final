import streamlit as st
import pandas as pd
import plotly.express as px

COLOR_PROFIT  = "#2E86AB"
COLOR_LOSS    = "#E84855"
COLOR_NEUTRAL = "#F4A261"
COLOR_BG      = "#F8F9FA"

st.set_page_config(
    page_title="Superstore Dashboard",
    page_icon="📦",
    layout="wide",
)


@st.cache_data
def load_data():
    df = pd.read_csv("superstore.csv", encoding="latin-1")
    df["Order Date"] = pd.to_datetime(df["Order Date"])
    df["Ship Date"]  = pd.to_datetime(df["Ship Date"])
    return df


df = load_data()

# ── Sidebar ──────────────────────────────────────────────────────────────────
st.sidebar.header("Filtros")

date_min = df["Order Date"].min().date()
date_max = df["Order Date"].max().date()

st.sidebar.markdown("**Rango de fechas**")
start_date = st.sidebar.date_input("Desde", value=date_min, min_value=date_min, max_value=date_max)
end_date   = st.sidebar.date_input("Hasta", value=date_max, min_value=date_min, max_value=date_max)

if start_date > end_date:
    st.sidebar.error("'Desde' debe ser anterior a 'Hasta'.")
    st.stop()

all_regions    = sorted(df["Region"].unique())
all_categories = sorted(df["Category"].unique())
all_segments   = sorted(df["Segment"].unique())

#filtrar por region,categoría o segmento
selected_regions    = st.sidebar.multiselect("Región",    all_regions,    default=all_regions)
selected_categories = st.sidebar.multiselect("Categoría", all_categories, default=all_categories)
selected_segments   = st.sidebar.multiselect("Segmento",  all_segments,   default=all_segments)

# ── Aplicar filtros ───────────────────────────────────────────────────────────

filtered_df = df[
    (df["Order Date"].dt.date >= start_date) &
    (df["Order Date"].dt.date <= end_date) &
    (df["Region"].isin(selected_regions)) &
    (df["Category"].isin(selected_categories)) &
    (df["Segment"].isin(selected_segments))
]

if filtered_df.empty:
    st.warning("No hay datos para la selección actual. Ajusta los filtros.")
    st.stop()

# ── Título principal ──────────────────────────────────────────────────────────
st.title("📦 Superstore — Rentabilidad vs. Descuentos")
st.caption("¿En qué áreas y productos los descuentos comprometen la rentabilidad?")

# ── Sección 1: KPIs ───────────────────────────────────────────────────────────

#cálculo de métricas
total_sales   = filtered_df["Sales"].sum()
total_profit  = filtered_df["Profit"].sum()
margin        = (total_profit / total_sales * 100) if total_sales else 0
total_orders  = filtered_df["Order ID"].nunique()
avg_discount  = filtered_df["Discount"].mean() * 100

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Total Ventas",       f"${total_sales:,.0f}")
col2.metric("Total Profit",       f"${total_profit:,.0f}", delta=f"${total_profit:,.0f}")
col3.metric("Margen Promedio",    f"{margin:.1f}%")
col4.metric("Órdenes Únicas",     f"{total_orders:,}")
col5.metric("Descuento Promedio", f"{avg_discount:.1f}%")

st.divider()

# ── Sección 2: Análisis Regional ──────────────────────────────────────────────
st.subheader("Las regiones más rentables no siempre son las de mayor volumen")

region_df = (
    filtered_df
    .groupby("Region")[["Sales", "Profit"]]
    .sum()
    .reset_index()
)

fig1 = px.bar(
    region_df,
    x="Region",
    y=["Sales", "Profit"],
    barmode="group",
    title="Análisis Regional de Ventas y Rentabilidad",
    color_discrete_sequence=["#9ba1a6", "#2c76a4"]
)

st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")

state_sales = df.groupby("State")["Sales"].sum().reset_index()

us_state_abbrev = {
    'Alabama': 'AL', 'Arizona': 'AZ', 'Arkansas': 'AR',
    'California': 'CA', 'Colorado': 'CO', 'Connecticut': 'CT',
    'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA',
    'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN',
    'Iowa': 'IA', 'Kansas': 'KS', 'Kentucky': 'KY',
    'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
    'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN',
    'Mississippi': 'MS', 'Missouri': 'MO', 'Montana': 'MT',
    'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH',
    'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY',
    'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH',
    'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA',
    'Rhode Island': 'RI', 'South Carolina': 'SC',
    'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX',
    'Utah': 'UT', 'Vermont': 'VT', 'Virginia': 'VA',
    'Washington': 'WA', 'West Virginia': 'WV',
    'Wisconsin': 'WI', 'Wyoming': 'WY'
}


# ── Sección 3: Tendencia Temporal ─────────────────────────────────────────────
st.subheader("Las ventas crecen, pero el profit no siempre acompaña el ritmo")

# TODO: Gráfico 2 — px.line con Sales y Profit agregados por mes (resample "ME")
#       Dos líneas: Sales (COLOR_NEUTRAL) y Profit (COLOR_PROFIT)
#       Eje X: fecha mensual; marcadores activados

st.divider()

# ── Sección 4: Categoría y Subcategoría ──────────────────────────────────────
st.subheader("Subcategorías con altas ventas son también las de mayor pérdida")

col_left, col_right = st.columns(2)

with col_left:
    # TODO: Gráfico 3 — px.treemap con path=[Category, Sub-Category]
    #       values="Sales", color="Profit"
    #       color_continuous_scale=[COLOR_LOSS, COLOR_NEUTRAL, COLOR_PROFIT]
    pass

with col_right:
    # TODO: Gráfico 4 — px.bar horizontal de Profit por Sub-Category
    #       Ordenar de mayor a menor; colorear barras: COLOR_PROFIT si Profit>0, COLOR_LOSS si <0
    pass

st.divider()

# ── Sección 5: Impacto de Descuentos ─────────────────────────────────────────
st.subheader("Descuentos superiores al 20 % sistemáticamente generan pérdidas")

col_left, col_right = st.columns(2)

with col_left:
    # TODO: Gráfico 5 — px.scatter Discount (eje X) vs Profit (eje Y)
    #       color="Category", size="Sales", opacity=0.6
    #       Línea de referencia horizontal en Profit=0
    pass

with col_right:
    # TODO: Gráfico 6 — px.box distribución de Discount por Category
    #       color="Category"; usar COLOR_PROFIT / COLOR_LOSS / COLOR_NEUTRAL por categoría
    pass

st.divider()

# ── Sección 6: Análisis Geográfico ───────────────────────────────────────────
st.subheader("Los estados del sur concentran las mayores pérdidas por descuentos")

state_sales["State Code"] = state_sales["State"].map(us_state_abbrev)
fig7 = px.choropleth(
    state_sales,
    locations="State Code",
    locationmode="USA-states",
    color="Sales",
    scope="usa",
    hover_name="State",
    color_continuous_scale="Blues",
    title="Volumen de Ventas por Estado"
)

st.plotly_chart(fig7)

st.markdown("---")