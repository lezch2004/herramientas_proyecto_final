import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio

# ── Paleta corporativa──────────────────────────────────────
COLOR_PROFIT  = "#2E86AB"   # azul  → ventas altas / profit positivo
COLOR_LOSS    = "#E84855"   # rojo  → pérdidas
COLOR_NEUTRAL = "#F4A261"   # naranja → ventas / dato secundario
COLOR_BG      = "#F8F9FA"   # gris claro → fondos

# Template global
pio.templates.default = "plotly_white"

# ── Configuración de página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Superstore Dashboard",
    page_icon="📦",
    layout="wide",
)

# ── Estilos CSS personalizados ───────────────────────────────────────────────
st.markdown("""
<style>
span[data-baseweb="tag"] {
    background-color: #2E86AB !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# ── Carga de datos ───────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("superstore.csv", encoding="latin-1")
    df["Order Date"] = pd.to_datetime(df["Order Date"])
    df["Ship Date"]  = pd.to_datetime(df["Ship Date"])
    return df

df = load_data()

# ── Sidebar: filtros ─────────────────────────────────────────────────────────
st.sidebar.header("🔎 Filtros")

# Rango de fechas
date_min = df["Order Date"].min().date()
date_max = df["Order Date"].max().date()
st.sidebar.markdown("**Rango de fechas**")
start_date = st.sidebar.date_input("Desde", value=date_min, min_value=date_min, max_value=date_max)
end_date   = st.sidebar.date_input("Hasta", value=date_max, min_value=date_min, max_value=date_max)

if start_date > end_date:
    st.sidebar.error("'Desde' debe ser anterior a 'Hasta'.")
    st.stop()

# Filtros múltiples
selected_regions    = st.sidebar.multiselect(
    "Región", sorted(df["Region"].unique()), default=sorted(df["Region"].unique())
)
selected_categories = st.sidebar.multiselect(
    "Categoría", sorted(df["Category"].unique()), default=sorted(df["Category"].unique())
)
selected_segments   = st.sidebar.multiselect(
    "Segmento", sorted(df["Segment"].unique()), default=sorted(df["Segment"].unique())
)

# Slider de descuento
discount_range = st.sidebar.slider(
    "Rango de Descuento (%)", min_value=0, max_value=100,
    value=(0, 100), step=1
)

# ── Aplicar filtros ──────────────────────────────────────────────────────────
filtered_df = df[
    (df["Order Date"].dt.date >= start_date) &
    (df["Order Date"].dt.date <= end_date) &
    (df["Region"].isin(selected_regions)) &
    (df["Category"].isin(selected_categories)) &
    (df["Segment"].isin(selected_segments)) &
    (df["Discount"] * 100 >= discount_range[0]) &
    (df["Discount"] * 100 <= discount_range[1])
]

if filtered_df.empty:
    st.warning("⚠️ No hay datos para la selección actual. Ajusta los filtros.")
    st.stop()

# ── Título principal ─────────────────────────────────────────────────────────
st.title("📦 Superstore Giant — Rentabilidad vs. Descuentos")
st.caption("¿En qué áreas y productos los descuentos están comprometiendo la rentabilidad?")
st.divider()

# ── Sección 1: KPIs ──────────────────────────────────────────────────────────
st.subheader("📊 Indicadores Clave")

total_sales   = filtered_df["Sales"].sum()
total_profit  = filtered_df["Profit"].sum()
margin        = (total_profit / total_sales * 100) if total_sales else 0
total_orders  = filtered_df["Order ID"].nunique()
avg_discount  = filtered_df["Discount"].mean() * 100

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("💰 Total Ventas",       f"${total_sales:,.0f}")
col2.metric("📈 Total Profit",       f"${total_profit:,.0f}")
col3.metric("📉 Margen Promedio",    f"{margin:.1f}%")
col4.metric("🛒 Órdenes Únicas",     f"{total_orders:,}")
col5.metric("🏷️ Descuento Promedio", f"{avg_discount:.1f}%")

st.info(
    "💡 Un margen bajo con descuento alto es la señal de alerta central del análisis. "
    "Usa los filtros del panel izquierdo para explorar el impacto por región, categoría o período."
)
st.divider()

# ── Sección 2: Análisis Regional ─────────────────────────────────────────────
st.subheader("🗺️ El Oeste lidera en ventas, pero el Sur sacrifica rentabilidad con descuentos")

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
    title="Ventas vs. Profit por Región",
    color_discrete_map={"Sales": COLOR_NEUTRAL, "Profit": COLOR_PROFIT},
    labels={"value": "USD", "variable": "Indicador"}
)
fig1.update_layout(legend_title_text="Indicador")
st.plotly_chart(fig1, use_container_width=True)

st.markdown(
    "> **Hallazgo:** Identifica las regiones donde la brecha entre ventas y profit es mayor — "
    "esas son las zonas donde los descuentos probablemente están erosionando el margen."
)
st.divider()

# ── Sección 3: Tendencia Temporal ────────────────────────────────────────────
st.subheader("📅 Las ventas crecen año a año, pero el profit no sigue el mismo ritmo")

monthly_df = (
    filtered_df
    .resample("ME", on="Order Date")[["Sales", "Profit"]]
    .sum()
    .reset_index()
)

fig2 = px.line(
    monthly_df,
    x="Order Date",
    y=["Sales", "Profit"],
    markers=True,
    title="Evolución Mensual de Ventas y Ganancia",
    color_discrete_map={"Sales": COLOR_NEUTRAL, "Profit": COLOR_PROFIT},
    labels={"Order Date": "Mes", "value": "USD", "variable": "Indicador"}
)
fig2.update_layout(hovermode="x unified", legend_title_text="Indicador")
st.plotly_chart(fig2, use_container_width=True)

st.markdown(
    "> **Hallazgo:** Observa si en los meses con picos de ventas el profit también sube, "
    "o si al contrario cae — lo que indicaría campañas de descuento agresivas."
)
st.divider()

# ── Sección 4: Categoría y Subcategoría ──────────────────────────────────────
st.subheader("📦 Furniture vende mucho pero genera las mayores pérdidas operativas")

col_left, col_right = st.columns(2)

with col_left:
    fig3 = px.treemap(
        filtered_df,
        path=["Category", "Sub-Category"],
        values="Sales",
        color="Profit",
        color_continuous_scale=[COLOR_LOSS, COLOR_BG, COLOR_PROFIT],
        color_continuous_midpoint=0,
        title="Volumen de Ventas coloreado por Rentabilidad"
    )
    fig3.update_layout(coloraxis_colorbar_title="Profit (USD)")
    st.plotly_chart(fig3, use_container_width=True)

with col_right:
    subcat_profit = (
        filtered_df
        .groupby("Sub-Category")["Profit"]
        .sum()
        .reset_index()
        .sort_values("Profit", ascending=True)
    )
    subcat_profit["color"] = subcat_profit["Profit"].apply(
        lambda x: COLOR_PROFIT if x > 0 else COLOR_LOSS
    )
    fig4 = px.bar(
        subcat_profit,
        x="Profit",
        y="Sub-Category",
        orientation="h",
        title="Profit por Subcategoría (Top y Bottom)",
        color="color",
        color_discrete_map="identity",
        labels={"Profit": "USD", "Sub-Category": "Subcategoría"}
    )
    fig4.add_vline(x=0, line_dash="dash", line_color="black")
    fig4.update_layout(showlegend=False)
    st.plotly_chart(fig4, use_container_width=True)

st.markdown(
    "> **Hallazgo:** Las subcategorías en rojo son las candidatas a revisar su política de precios "
    "o descuentos. Un alto volumen de ventas con profit negativo indica un problema estructural."
)
st.divider()

# ── Sección 5: Impacto de Descuentos ─────────────────────────────────────────
st.subheader("🏷️ Descuentos superiores al 20% destruyen el margen de forma sistemática")

col_left, col_right = st.columns(2)

with col_left:
    fig5 = px.scatter(
        filtered_df,
        x="Discount",
        y="Profit",
        color="Category",
        size="Sales",
        opacity=0.6,
        title="Descuento vs. Profit por Categoría",
        color_discrete_map={
            "Furniture":       COLOR_NEUTRAL,
            "Office Supplies": COLOR_PROFIT,
            "Technology":      COLOR_LOSS
        },
        hover_data=["Product Name", "Sales"],
        labels={"Discount": "Descuento (%)", "Profit": "Profit (USD)"}
    )
    fig5.add_hline(y=0, line_dash="dash", line_color="black", annotation_text="Punto de quiebre")
    st.plotly_chart(fig5, use_container_width=True)

with col_right:
    fig6 = px.box(
        filtered_df,
        x="Category",
        y="Discount",
        color="Category",
        title="Distribución de Descuentos por Categoría",
        color_discrete_map={
            "Furniture":       COLOR_NEUTRAL,
            "Office Supplies": COLOR_PROFIT,
            "Technology":      COLOR_LOSS
        },
        labels={"Discount": "Descuento (%)", "Category": "Categoría"}
    )
    fig6.update_layout(showlegend=False)
    st.plotly_chart(fig6, use_container_width=True)

st.markdown(
    "> **Hallazgo:** El scatter muestra claramente cómo a mayor descuento el profit cae a territorio "
    "negativo. El box plot revela qué categoría recibe descuentos más altos y dispersos — "
    "esa es la categoría que requiere intervención inmediata."
)
st.divider()

# ── Sección 6: Análisis Geográfico ───────────────────────────────────────────
st.subheader("🗺️ Texas y Pennsylvania concentran las mayores pérdidas del país")

US_STATE_ABBREV = {
    "Alabama": "AL", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
    "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "Florida": "FL",
    "Georgia": "GA", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN",
    "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA",
    "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI",
    "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO", "Montana": "MT",
    "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ",
    "New Mexico": "NM", "New York": "NY", "North Carolina": "NC",
    "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR",
    "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT",
    "Vermont": "VT", "Virginia": "VA", "Washington": "WA",
    "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY",
}

state_df = (
    filtered_df
    .groupby("State")[["Sales", "Profit"]]
    .sum()
    .reset_index()
)
state_df["code"] = state_df["State"].map(US_STATE_ABBREV)

fig7 = px.choropleth(
    state_df,
    locations="code",
    locationmode="USA-states",
    color="Profit",
    scope="usa",
    color_continuous_scale=[COLOR_LOSS, COLOR_BG, COLOR_PROFIT],
    color_continuous_midpoint=0,
    hover_name="State",
    hover_data={"Sales": ":$,.0f", "Profit": ":$,.0f", "code": False},
    labels={"Profit": "Profit (USD)"},
    title="Profit por Estado — Rojo = pérdidas, Azul = ganancias"
)
fig7.update_layout(paper_bgcolor=COLOR_BG)
st.plotly_chart(fig7, use_container_width=True)

st.markdown(
    "> **Hallazgo:** Los estados en rojo son mercados donde el negocio opera en pérdida. "
    "Cruzar esta información con el nivel de descuentos por estado permitiría diseñar "
    "una política de precios diferenciada por mercado."
)
st.divider()
