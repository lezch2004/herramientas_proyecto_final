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
    return df

#cargar
datos = cargar_datos()

st.sidebar.header("Filtros")

#seleccionar géneros
gender = st.sidebar.multiselect(
    "Selecciona los géneros: ",
    options = sorted(datos["Region"].unique()),
    default = sorted(datos["Region"].unique())
)

#seleccionar categoría
categoria = st.sidebar.multiselect(
    "Selecciona los géneros: ",
    options = sorted(datos["Category"].unique()),
    default = sorted(datos["Category"].unique())
)

filtered_data = datos[
    (datos["Region"].isin(gender)) &
    (datos["Category"].isin(categoria))
]

st.header("Métricas Generales")

#calculo de metricas
sales = filtered_data["Sales"].sum()
avg_discount = filtered_data["Discount"].mean()
avg_discount *= 100
profit = filtered_data["Profit"].sum()

#creacion de columnas
metric1, metric2, metric3 = st.columns(3)

#poner metricas
with metric1:
    st.metric(label = "Ventas Totales ($)", value=f"${sales:,.2f}")
with metric2:
    st.metric(label = "Ganancias Totales ($)", value=f"${profit:,.2f}")
with metric3:
    st.metric(label = "Average Discount (%)", value=f"{avg_discount:,.2f}%")

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

