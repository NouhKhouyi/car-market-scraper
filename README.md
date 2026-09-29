# Car Market Scraper

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Selenium](https://img.shields.io/badge/Scraping-Selenium%20%7C%20BeautifulSoup-green.svg)](https://www.selenium.dev/)
[![Streamlit](https://img.shields.io/badge/App-Streamlit-red.svg)](https://streamlit.io/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-lightgrey.svg)](LICENSE)

**Car Market Scraper** extrae los anuncios de coches de segunda mano de varios portales españoles, los unifica en una sola base de datos y los ofrece en un **buscador web** para encontrar el coche más barato según marca, modelo, kilometraje y precio.

Proyecto de la asignatura **Adquisición y Tratamiento de Datos (ATD)** del Grado en Ciencia de Datos de la Universitat Politècnica de València (curso 2024-25).

---

## Qué hace

1. **Scraping** de 4 fuentes: 3 portales de venta y 1 de historiales de vehículos.
2. **Limpieza y unificación** de los datos: nombres de columnas, tipos y marcas/modelos emparejados entre portales.
3. **Comparativa** de precio, año y kilometraje medios por modelo en cada portal.
4. **Buscador en Streamlit** con filtros, gráficos y enlace directo al anuncio original.

## Datos obtenidos

| Fuente | Tipo | Anuncios | Variables | Técnica |
|---|---|---:|---:|---|
| [OcasionPlus](https://www.ocasionplus.com) | Venta | 8.866 | 24 | Selenium + `requests` + BeautifulSoup |
| [AutoScout24](https://www.autoscout24.es) | Venta | 3.755 | 10 | Selenium + BeautifulSoup |
| [Motor.es](https://www.motor.es) | Venta | 1.100 | 15 | `requests` + BeautifulSoup |
| [Carfax](https://www.carfax.eu) | Historial | 1.338 | 10 | Selenium (enlazado con OcasionPlus) |

**En total, más de 13.700 anuncios**, con precio, kilometraje, año, combustible, potencia, cambio, ubicación, dimensiones, consumo, emisiones y, en el caso de Carfax, número de inspecciones y registros del vehículo.

<details>
<summary>Variables por fuente</summary>

**OcasionPlus**: marca, modelo, etiqueta ambiental, año, km, combustible, CV, cambio, único propietario, ubicación, dimensiones (largo/ancho/alto), peso, maletero, velocidad máxima, 0-100 km/h, consumo, emisiones de CO₂, número de llaves y precio.

**Carfax**: identificador enlazado con OcasionPlus, número de inspecciones y de registros, carrocería, cilindrada, puertas, asientos, carga máxima y distancia entre ejes.

**AutoScout24**: marca, modelo, precio, año, km, combustible, CV, cambio, lugar de venta y enlace de compra.

**Motor.es**: precio, marca, modelo, versión, combustible, CV, km, carrocería, año de matriculación, cambio, meses de garantía, plazas, puertas y color.

</details>

---

## Arquitectura

```text
 OcasionPlus ─┐
 AutoScout24 ─┼─► scrapers/ ─► data/*.csv ─► cleaning/ ─► resumen.csv
 Motor.es    ─┤                    │          (unificación y
 Carfax      ─┘                    │           comparativa por modelo)
                                   ▼
                              app/app.py  (buscador en Streamlit)
```

### 1. Scrapers (`scrapers/`)
- **Páginas estáticas** (Motor.es): peticiones HTTP y análisis del HTML con BeautifulSoup, recorriendo el listado página a página y después la ficha de cada coche.
- **Páginas dinámicas** (OcasionPlus, AutoScout24, Carfax): Selenium para renderizar el contenido cargado con JavaScript y BeautifulSoup para extraer los campos, con pausas entre peticiones para no saturar el servidor.
- Los informes de Carfax se obtienen desde los enlaces que publica cada anuncio de OcasionPlus, lo que añade el **historial** del vehículo (inspecciones y registros) al anuncio.

### 2. Limpieza y unificación (`cleaning/`)
- Normalización de nombres de columnas y tipos entre portales.
- Emparejamiento aproximado de marca y modelo entre fuentes (`difflib`).
- Tabla `resumen.csv`: **108 modelos** con año, kilometraje y precio medios en cada portal, para comparar dónde sale más barato el mismo coche.

### 3. Buscador (`app/app.py`)
- Carga y estandariza los tres portales de venta en un único conjunto de datos.
- Filtros por marca, modelo, kilometraje máximo y rango de precio.
- Tabla ordenada por precio, gráficos de distribución por portal (Plotly) y tarjetas de los 3 coches más baratos con enlace al anuncio.
- Imágenes opcionales mediante la API de Unsplash.

---

## Cómo ejecutarlo

```bash
pip install -r requirements.txt
streamlit run app/app.py
```

**Opcional:** para ver las imágenes de Unsplash, copia `.streamlit/secrets.toml.example` como `.streamlit/secrets.toml` y añade tu clave, o define la variable de entorno `UNSPLASH_ACCESS_KEY`. Sin clave, la app funciona igual y muestra imágenes por defecto.

Los scrapers de Selenium necesitan Chrome y su ChromeDriver. La ruta al driver se ajusta dentro de cada notebook.

> Los datos se obtuvieron en diciembre de 2024. Los portales cambian su HTML con frecuencia, así que puede que haya que adaptar los selectores para volver a ejecutar los scrapers.

---

## Estructura

```text
scrapers/   ocasionplus.py · motores.py · autoscout24.ipynb · carfax.ipynb
data/       CSV obtenidos de cada portal
cleaning/   procesamiento_datos.ipynb · resumen.csv
app/        app.py (buscador en Streamlit)
```

## Equipo

- **Nouh Khouyi**: scrapers de AutoScout24 y Carfax, y buscador en Streamlit.
- **Pablo Gandía**: scrapers de OcasionPlus y Motor.es.
- **Pablo Alpuente**: fusión y limpieza de los datos.

## Aviso

Proyecto académico sin ánimo de lucro. Los datos pertenecen a sus respectivos portales y se incluyen solo con fines educativos.
