import streamlit as st
import pandas as pd 
import plotly.express as px

#configurar la página
st.set_page_config(
    page_title="Superstore Giant Dashboard",
    page_icon="🚀",
    layout="wide"
)

st.markdown("""
<style>
span[data-baseweb="tag"] {
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
span[data-baseweb="tag"] {
    background-color: #2c76a4 !important;
}
</style>
""", unsafe_allow_html=True)

#titulo
st.title("Superstore Giant - Dashboard")
st.markdown("---")

#funcion para cargar datos
@st.cache_data
def cargar_datos():
    df = pd.read_csv("superstore.csv", encoding="latin1")
    df["Order Date"] = pd.to_datetime(df["Order Date"])
    df["Ship Date"]  = pd.to_datetime(df["Ship Date"])
    return df

#cargar
datos = cargar_datos()

st.sidebar.header("Filtros")

date_min = datos["Order Date"].min().date()
date_max = datos["Order Date"].max().date()

st.sidebar.markdown("**Rango de fechas**")
start_date = st.sidebar.date_input("Desde", value=date_min, min_value=date_min, max_value=date_max)
end_date   = st.sidebar.date_input("Hasta", value=date_max, min_value=date_min, max_value=date_max)

if start_date > end_date:
    st.sidebar.error("'Desde' debe ser anterior a 'Hasta'.")
    st.stop()

#seleccionar géneros
region = st.sidebar.multiselect(
    "Selecciona los géneros: ",
    options = sorted(datos["Region"].unique()),
    default = sorted(datos["Region"].unique())
)

#seleccionar categoría
categoria = st.sidebar.multiselect(
    "Selecciona las categorías: ",
    options = sorted(datos["Category"].unique()),
    default = sorted(datos["Category"].unique())
)

#Seleccionar 

filtered_data = datos[
    (datos["Region"].isin(region)) &
    (datos["Category"].isin(categoria))
]

st.header("Métricas Generales")

#calculo de metricas
sales = filtered_data["Sales"].sum()
avg_discount = filtered_data["Discount"].mean()
avg_discount *= 100
profit = filtered_data["Profit"].sum()
margin= (profit / sales * 100) if sales else 0
orders  = filtered_data["Order ID"].nunique()

#creacion de columnas
metric1, metric2, metric3, metric4, metric5 = st.columns(5)

#poner metricas
with metric1:
    st.metric(label = "Ventas Totales ($)", value=f"${sales:,.2f}")
with metric2:
    st.metric(label = "Ganancias Totales ($)", value=f"${profit:,.2f}")
with metric3:
    st.metric(label = "Average Discount (%)", value=f"{avg_discount:,.2f}%")
with metric4:
    st.metric(label = "Margen Promedio (%)", value = f"{margin:.1f}%")
with metric5:
    st.metric(label= "Descuento Promedio", value = f"{avg_discount:.1f}%")

st.markdown("---")
st.header("Ventas y Ganancia por Región")

region_df = (
    filtered_data
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

state_sales = datos.groupby("State")["Sales"].sum().reset_index()

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

st.header("Ventas por Región")
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

