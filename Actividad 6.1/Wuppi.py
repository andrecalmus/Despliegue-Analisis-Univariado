###############################################################
# Importamos librerías
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import io
import plotly.express as px

###############################################################
# Configuración de la página
st.set_page_config(
    page_title="Wuupi Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

###############################################################
# Definimos la instancia
@st.cache_resource
# Creamos la función de carga de datos
def load_data():
    dfc = pd.read_csv('DataAnalyticsCat.csv')
    dfn = pd.read_csv('DataAnalyticsNum.csv')
    dfc['usuario'] = dfc['usuario'].str.title()
    dfc['administrador'] = dfc['administrador'].str.title()
    categoricas = ['presionó botón correcto', 'mini juego', 'color presionado', 'dificultad', 'juego', 'auto push']
    numericas = ['tiempo de interacción', 'número de interacción por lección', 'tiempo de lección', 'tiempo de sesión']
    usuarios = dfc['usuario'].unique()
    return dfc, dfn, categoricas, numericas, usuarios

###################################################################
# Cargo los datos obtenidos de la función "load_data"
dfc, dfn, categoricas, numericas, usuarios = load_data()

################################################################
# CREACIÓN DEL DASHBOARD

# Barra lateral
st.sidebar.image('wuupi.png', width=200)
st.sidebar.title('Wuupi Dashboard')

# Checkbox para todos los usuarios
todos_usuarios = st.sidebar.checkbox("Todos los Usuarios")

if todos_usuarios:
    dfc = dfc
    dfn = dfn
else:
    usuario = st.sidebar.selectbox(label="Usuario", options=usuarios)
    dfc = dfc[dfc['usuario'] == usuario]
    dfn = dfn[dfn['usuario'] == usuario]

# Selectbox para tipo de análisis
View = st.sidebar.selectbox(label="Tipo de Análisis", options=[
    "Extracción de Características", "Regresión Lineal", "Regresión No Lineal", "Regresión Logística", "ANOVA"
])

# CONTENIDO DE LA VISTA 1
if View == "Extracción de Características":
    # Selectbox de variable categórica
    Variable_Cat = st.sidebar.selectbox(label="Variables", options=categoricas)

    # Tabla de frecuencias
    Tabla_frecuencias = dfc[Variable_Cat].value_counts().reset_index()
    Tabla_frecuencias.columns = ['categorias', 'frecuencia']

    # Diccionarios de colores personalizados
    color_maps = {
        'auto push': {'Si': '#65b832', 'No': '#cc3234'},
        'color presionado': {
            'red': '#cc3234', 'blue': '#136698', 'green': '#65b832',
            'yellow': '#fdcb12', 'violet': 'purple'
        },
        'presionó botón correcto': {'Si': '#65b832', 'No': '#cc3234'},
        'dificultad': {'Episodio 1': 'lightgreen', 'Episodio 2': 'orange', 'Episodio 3': 'crimson', 'Episodio 4': 'blue'},
        'juego': {'Astro': 'skyblue', 'Cadetes': 'violet'},
        'mini juego': {'Sí': 'dodgerblue', 'No': 'gray'}
    }

    color_map = color_maps.get(Variable_Cat, {})

    # KPIs
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.metric("📈 Categoría más frecuente", Tabla_frecuencias.iloc[0]['categorias'], f"{Tabla_frecuencias.iloc[0]['frecuencia']} ocurrencias")
    with col2:
        dfc_total = load_data()[0]
        tiempo_promedio_global = round(dfc_total['tiempo de interacción'].mean(), 2)
        tiempo_promedio_usuario = round(dfc['tiempo de interacción'].mean(), 2)
        diferencia = round(tiempo_promedio_usuario - tiempo_promedio_global, 2)
        if diferencia > 0:
            delta_texto = f"+{diferencia} seg"
            delta_color = "inverse"
        elif diferencia < 0:
            delta_texto = f"{diferencia} seg"
            delta_color = "inverse"
        else:
            delta_texto = "0 seg"
            delta_color = "off"
        st.metric("⏱️ Tiempo promedio de interacción", f"{tiempo_promedio_usuario} segundos", delta=delta_texto, delta_color=delta_color)
    with col3:
        sesiones_completadas = (dfc['tiempo de sesión'] != 0).sum()
        st.metric("🧩 Sesiones completadas", sesiones_completadas)

    # Fila 1: Gráfico de barras y pastel
    Contenedor_A, Contenedor_B = st.columns(2)
    with Contenedor_A:
        figure1 = px.bar(
            data_frame=Tabla_frecuencias,
            x='frecuencia',
            y='categorias',
            title=f'Frecuencia por {Variable_Cat.title()}',
            color='categorias',
            color_discrete_map=color_map,
            orientation='h'
        )
        figure1.update_layout(height=500, yaxis_title=Variable_Cat.title(), xaxis_title='Frecuencia')
        st.plotly_chart(figure1, use_container_width=True)

    with Contenedor_B:
        figure2 = px.pie(
            data_frame=Tabla_frecuencias,
            values='frecuencia',
            names='categorias',
            title='Frecuencia por Categoría',
            color='categorias',
            color_discrete_map=color_map
        )
        figure2.update_traces(textposition='inside', textinfo='percent+label')
        figure2.update_layout(height=500)
        st.plotly_chart(figure2, use_container_width=True)

    # Fila 2 : Gráfico de líneas y boxplot
    Contenedor_C, Contenedor_D = st.columns(2)
    with Contenedor_C:
        dfc['fecha'] = pd.to_datetime(dfc['fecha'])
        df_promedio_diario = dfc.groupby(dfc['fecha'].dt.date)['tiempo de interacción'].mean().reset_index()
        figure_line = px.line(
            df_promedio_diario,
            x='fecha',
            y='tiempo de interacción',
            title='Tiempo Promedio de Interacción por Día',
            labels={'fecha': 'Fecha', 'tiempo de interacción': 'Tiempo Promedio de Interacción (s)'},
            line_shape='spline',
            render_mode='svg',
            markers=True,
            color_discrete_sequence=['#6ce5c3']

        )
        figure_line.update_layout(
            height=500,
            xaxis_title='Fecha',
            yaxis_title='Tiempo Promedio de Interacción (s)',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(figure_line, use_container_width=True)

    with Contenedor_D:
        figure_box = px.box(
            dfc,
            x=Variable_Cat,
            y='tiempo de interacción',
            color=Variable_Cat,
            title=f'Distribución del Tiempo de Interacción por {Variable_Cat.title()}',
            color_discrete_map=color_map
        )
        st.plotly_chart(figure_box, use_container_width=True)

    # Fila 3: Visualización adaptativa de evolución del tiempo
    st.markdown("### 📊 Análisis Temporal del Comportamiento")
    dfc['fecha'] = pd.to_datetime(dfc['fecha'])
    dfc = dfc.sort_values('fecha')

    if todos_usuarios:
        df_filtrado = dfc[dfc['tiempo de lección'] > 0]
        fig_scatter_all = px.scatter(
            df_filtrado,
            x='tiempo de interacción',
            y='tiempo de lección',
            size='tiempo de interacción',
            color='usuario',
            title="📍 Interacciones por Usuario (Lecciones Completas)",
            labels={
                'tiempo de interacción': 'Tiempo de Interacción (s)',
                'tiempo de lección': 'Tiempo de Lección (s)',
                'usuario': 'Usuario'
            },
            hover_data=['fecha', 'usuario']
        )
        fig_scatter_all.update_layout(height=450, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_scatter_all, use_container_width=True)

    else:
        df_usuario = dfc[dfc['tiempo de lección'] > 0]
        fig_scatter_user = px.scatter(
            df_usuario,
            x='tiempo de interacción',
            y='tiempo de lección',
            size='tiempo de interacción',
            color='fecha',
            title=f"📍 Interacciones del Usuario {usuario}",
            labels={
                'tiempo de interacción': 'Tiempo de Interacción (s)',
                'tiempo de lección': 'Tiempo de Lección (s)',
                'fecha': 'Fecha'
            },
            hover_data=['fecha']
        )
        fig_scatter_user.update_layout(height=450, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_scatter_user, use_container_width=True)

