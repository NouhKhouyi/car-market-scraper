import os
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px 
import requests
import random
from bs4 import BeautifulSoup

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

#Para las imagenes usamos la API de Unsplash (opcional).
#La clave se lee de .streamlit/secrets.toml o de la variable de entorno UNSPLASH_ACCESS_KEY.
def leer_clave_unsplash():
    try:
        return st.secrets["UNSPLASH_ACCESS_KEY"]
    except Exception:
        return os.environ.get("UNSPLASH_ACCESS_KEY")

key = leer_clave_unsplash()

# Función para cargar y estandarizar datos desde varios CSV
def cargar_datos(archivos_csv):
    dataframes = []
    for archivo, nombre in archivos_csv.items():
        try:
            st.write(f"⌚ Procesando archivo: {nombre}")
            df = pd.read_csv(archivo)

            if nombre == "MotorES":
                df = df.rename(columns={"Marca": "Brand", "Modelo": "Model", "Kilómetros": "KM", "Precio": "Price"})
                df = df[["Brand", "Model", "KM", "Price"]]
                df["URL"] = df.apply(lambda x: f"https://www.motor.es/{x['Brand'].lower()}-{'-'.join(x['Model'].split()).lower()}-segunda-mano/" if pd.notna(x["Brand"]) and pd.notna(x["Model"]) else None, axis=1)
            elif nombre == "OcasionPlus":
                df = df.rename(columns={"KM": "KM", "Name": "Model", "Brand": "Brand", "Price": "Price"})
                df = df[["Brand", "Model", "KM", "Price"]]
                df["URL"] = df.apply(lambda x: f"https://www.ocasionplus.com/coches-segunda-mano?v2&orderBy=lastPublished&brand={x['Brand'].lower()}&model={'_'.join(x['Model'].split()[:2])}+{'+'.join(x['Model'].split()[2:])}" if pd.notna(x["Brand"]) and pd.notna(x["Model"]) else None, axis=1)
            elif nombre == "AutoScout":
                df = df.rename(columns={"Marca": "Brand", "Modelo": "Model", "Kilometraje (Km)": "KM", "Precio": "Price", "Enlace_Compra": "URL"})
                df = df[["Brand", "Model", "KM", "Price", "URL"]]

            df["Pagina"] = nombre
            
            df = df[["Brand", "Model", "KM", "Price", "Pagina", "URL"]]

            st.write(f"🚗 {nombre}: {df.shape[0]} filas cargadas. 🚗")
            dataframes.append(df)
        except Exception as e:
            st.warning(f"No se pudo procesar {nombre}: {str(e)}")

    if not dataframes:
        st.error("No se pudieron cargar datos de los archivos proporcionados.")
    return pd.concat(dataframes, ignore_index=True) if dataframes else pd.DataFrame(columns=["Brand", "Model", "KM", "Price", "Pagina", "URL"])

# Función para filtrar datos según los criterios del usuario
# Función para filtrar datos según los criterios del usuario
def filtrar_datos(data, marca=None, km_max=None, modelo=None, precio_min=None, precio_max=None):
    if marca:
        data = data[data["Brand"].str.contains(marca, case=False, na=False)]
    if modelo:
        data = data[data["Model"].str.contains(modelo, case=False, na=False)]  # Filtrar por modelo
    if km_max is not None:
        data = data[data["KM"].fillna(float('inf')) <= km_max]
    if precio_min is not None and precio_max is not None:
        data = data[(data["Price"] >= precio_min) & (data["Price"] <= precio_max)]
    return data


# Función para obtener todos los coches ordenados por precio
def obtener_mas_baratos(data):
    if data.empty:
        st.warning("No hay datos disponibles para ordenar los coches por precio.")
        return data
    # Ordenar todos los coches por precio de menor a mayor
    return data.sort_values(by="Price", ascending=True)

# Aplicación Streamlit
def main():
    st.set_page_config(page_title="Buscador de Coches", layout="wide")  # Activa el modo ancho

    st.title("🔎 Buscador de Coches Más Baratos")
    
    # Agregar una pequeña descripción
    st.markdown("""
    En esta aplicación podrás buscar coches de diferentes páginas web y ordenarlos por precio, kilometraje y marca.
    Utiliza los filtros de búsqueda para encontrar el coche que mejor se adapte a tus necesidades.
    """)

    # Archivos CSV y sus nombres
    archivos_csv = {
        DATA_DIR / "MotorES.csv": "MotorES",
        DATA_DIR / "OcasionPlusData.csv": "OcasionPlus",
        DATA_DIR / "AutoScout24.csv": "AutoScout"
    }

    # Cargar datos
    datos = cargar_datos(archivos_csv)

    if datos.empty:
        st.error("No se pudieron cargar datos de los archivos proporcionados. Por favor, verifica los archivos.")
        return

    # Filtros
    st.sidebar.header("Filtros de búsqueda")

    # Filtro dinámico por Marca
    marca = st.sidebar.text_input("Buscar por Marca", "")
    
    # Filtro de Kilometraje máximo con barra deslizante
    km_max = st.sidebar.slider("Kilometraje máximo", min_value=0, max_value=1000000, value=200000, step=1000)

    # Filtro dinámico por Modelo
    modelo = st.sidebar.text_input("Buscar por Modelo", "")



    # Filtro de rango de precio con barra deslizante y entrada manual
    st.sidebar.markdown("### Rango de Precio (€)")
    precio_min = st.sidebar.number_input("Precio mínimo", min_value=0, max_value=1000000, value=0, step=500)
    precio_max = st.sidebar.number_input("Precio máximo", min_value=0, max_value=1000000, value=30000, step=500)

    # Asegurar que el mínimo no sea mayor que el máximo
    if precio_min > precio_max:
        st.sidebar.error("El precio mínimo no puede ser mayor que el precio máximo.")

    # Alternativa con slider para selección rápida
    rango_precio = st.sidebar.slider("Rango de precio", min_value=0, max_value=1000000, value=(precio_min, precio_max), step=500)

    # Usar el valor del slider para ajustar los valores en las cajas de entrada
    precio_min, precio_max = rango_precio

    
    # Mostrar los filtros de manera dinámica
    st.sidebar.markdown("---")
    st.sidebar.write(f"Marca buscada: {marca}")
    st.sidebar.write(f"Kilometraje máximo: {km_max} km")
    
    # Aplicar filtros
    datos_filtrados = filtrar_datos(datos, marca=marca, km_max=km_max, modelo=modelo, precio_min=precio_min, precio_max=precio_max)

    # Obtener los coches más baratos (ordenados por precio)
    mas_baratos = obtener_mas_baratos(datos_filtrados)

    # Mostrar resultados
    if mas_baratos.empty:
        st.write("No se encontraron resultados con los filtros aplicados.")
    else:
        st.write(f"**Coches más baratos encontrados: {len(mas_baratos)}**")
        
        # Mostrar solo las primeras 500 filas para mejorar el rendimiento
        mas_baratos_mostrar = mas_baratos.head(500)

        if mas_baratos_mostrar.empty:
            st.write("No se encontraron resultados con los filtros aplicados.")
        else:
            st.write(f"**Coches más baratos encontrados: {len(mas_baratos)}**")

            # Alternativa más eficiente con st.data_editor
            st.data_editor(
                mas_baratos_mostrar,
                use_container_width=True,
                height=500  # Fija la altura para evitar lag en desplazamiento
            )

    st.write("# 📊 Analíticas:")

    # Contar cantidad de coches por página
    conteo_paginas = datos_filtrados["Pagina"].value_counts().reset_index()
    conteo_paginas.columns = ["Pagina", "Cantidad"]

    # Ajustar la distribución de las columnas (más espacio para el histograma)
    col1, col2 = st.columns([2.5, 2.5])  # 2/5 para pastel, 3/5 para histograma

    # Gráfico de pastel
    with col1:
        st.write("### Distribución de coches según la página web")
        fig_pie = px.pie(conteo_paginas, values="Cantidad", names="Pagina",
                        title="Distribución de Coches por Página",
                        color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig_pie, use_container_width=True)  # Expande al 100% del contenedor

    # Histograma (Gráfico de barras)
    with col2:
        st.write("### Distribución en histograma")
        fig_bar = px.bar(conteo_paginas, x="Pagina", y="Cantidad", 
                        title="Cantidad de coches por página",
                        color="Pagina",
                        text="Cantidad",
                        color_discrete_sequence=px.colors.qualitative.Set2)
        
        fig_bar.update_layout(xaxis_title="Página Web", yaxis_title="Cantidad de Coches")
        st.plotly_chart(fig_bar, use_container_width=True)  # Expande al 100% del contenedor

    # Simulación de URLs de imágenes si no tienes una en el dataset
    def obtener_imagen_por_defecto(brand, model, pagina):
        try:  
            if not key:
                raise ValueError("Sin clave de Unsplash: se usa la imagen por defecto")
            API_KEY = key
            url = f"https://api.unsplash.com/search/photos?query={brand}+{model}+&client_id={API_KEY}&per_page=1"

            response = requests.get(url)
            data = response.json()
            
            if data["results"]:
                imagen_aleatoria = random.choice(data["results"])
                return imagen_aleatoria["urls"]["regular"]  # URL de la imagen
            else:
                return "https://via.placeholder.com/500x300?text=No+Image"
        except:
            if pagina == 'OcasionPlus':
                return f'https://images.grupoocasionplus.com/PyxVXcE12KBTCIyFPvrBuIAFX-QAUGwAeJOPke6tRfE/mobilex2/czM6Ly9nYWxsZXJ5LWRlYWxlcnMvYmFyY2Vsb25hLWxsaXNzYS12YWxsL29jYXNpb25wbHVzLWJhcmNlbG9uYS1sbGlzc2EtdmFsbF9mdWxsc2NyZWVuLmpwZw'
            elif pagina == 'MotorES':
                return f'https://www.motor.es/imagenes/motorpuntoes-home.jpg'
            else:
                return f'https://cdn-1.webcatalog.io/catalog/autoscout24/autoscout24-social-preview.png?v=1736142840810'

    # Seleccionar los 3 coches más baratos con imágenes
    top_coches = mas_baratos.head(3)

    if "Image_URL" not in top_coches.columns:
        top_coches["Image_URL"] = top_coches.apply(lambda x: obtener_imagen_por_defecto(x["Brand"], x["Model"], x['Pagina']), axis=1)

    # Agregar sección de imágenes
    st.subheader("📸 Imágenes de los Coches Más Baratos")

    # Tamaño fijo para las imágenes (en píxeles)
    image_width = 400

    # Mostrar las 3 imágenes en columnas con un enlace clicable
    cols = st.columns(3)  # Crear 3 columnas

    for col, (_, row) in zip(cols, top_coches.iterrows()):
        with col:
            if row['Pagina'] == 'OcasionPlus':
                # Definir la URL de la imagen y el enlace
                url_imagen = row["Image_URL"]
                url_destino = row["URL"]  # Reemplaza con el enlace correcto

                # Crear un enlace HTML para la imagen
                html_code = f"""
                <a href="{url_destino}" target="_blank">
                    <img src="{url_imagen}" width=f"{image_width}" />
                </a>
                
                <a href="{url_destino}"> {row['Model'].split()[0]} {' '.join(row['Model'].split(' ')[1:])}
                """
                st.markdown(html_code, unsafe_allow_html=True)
                st.write(f"Precio: €{row['Price']:.2f}")
            else:
                # Definir la URL de la imagen y el enlace
                url_imagen = row["Image_URL"]
                url_destino = row["URL"]  # Reemplaza con el enlace correcto

                # Crear un enlace HTML para la imagen
                html_code = f"""
                <a href="{url_destino}" target="_blank">
                    <img src="{url_imagen}" width=f"{image_width}" />
                </a>
                
                <a href="{url_destino}"> {row['Brand']} {row['Model']} <a>
                """
                st.markdown(html_code, unsafe_allow_html=True)
                st.write(f"Precio: €{row['Price']:.2f}")
if __name__ == "__main__":
    main()
