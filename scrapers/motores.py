import requests
from bs4 import BeautifulSoup
import pandas as pd


'''
Dada la url de la página devuelve la lista de todos los links de los coches de dicha página, haciendo un get y obteniendo la soup de beautifulsoup
'''

def switch_page(url, headers):
    response = requests.get(url, headers=headers)

    if response.status_code in [200,201]:

        soup = BeautifulSoup(response.text, 'html.parser')
        container = soup.find('div', class_='js-results-lists listado-ofertas')
        links_elements = container.find_all('a', class_='elemento-segunda-mano__link coche-link')
        links = [link['href'] for link in links_elements]
        return links
    
    else:
        return None

'''
Este modulo, dado el nombre de las variables y la url de cada coche, devuelve un diccionario con el valor de todas las variables
que hemos seleccionado de cada coche
'''

def get_info(url, headers, columns):
    result = {}
    response = requests.get(url, headers=headers)

    if response.status_code in [200,201]:
        soup = BeautifulSoup(response.text, 'html.parser')
        ficha = soup.find('section', class_='zona-contenido ficha ancho-principal')
        divs = ficha.find_all('div')

        for div in divs:
            try:
                var = div.find('dt').text
                if var in columns:
                    value = div.find('dd').text
                    result[var] = value
            except:
                pass
        
        return result
    
    else:
        return None

'''
Este modulo llama a las funciones anteriores y va obteniendo todos los coches de todas las páginas (50) de la web
'''

def get_data(url_main,headers,columns):

    info = []

    for i in range(1,51):

        url = url_main + str(i)
        links = switch_page(url, headers)
        if links:
            for link in links:
                result = get_info(link, headers, columns)
                if result:
                    info.append(result)
        
        print('Página', i, 'completada')

    return info

'''
Este modulo sirve para transformar las variables que necesitan algun cambio del dataframe, por ejemplo pasar algunas a numérico y cambiarle el nombre a alguna columna
'''

def clean_data(df):


    df = df.replace('-',pd.NA)

    df = df.rename(columns={'Matriculación': 'Año Matriculación',
                            'Precio al contado': 'Precio',
                            'Potencia': 'Potencia (CV)',
                            'Garantía': 'Meses Garantía'})

    df['Precio'] = pd.to_numeric(df['Precio'].str.replace(' €', '').str.replace('.', ''), errors='coerce').fillna(pd.NA)
    df['Potencia (CV)'] = pd.to_numeric(df['Potencia (CV)'].str.replace(' CV', ''), errors='coerce').fillna(pd.NA)
    df['Año Matriculación'] = pd.to_numeric(df['Año Matriculación'].str.split('/').str[1], errors='coerce').fillna(pd.NA)
    df['Meses Garantía'] = pd.to_numeric(df['Meses Garantía'].str.split(' ').str[0], errors='coerce').fillna(0)
    df['Kilómetros'] = pd.to_numeric(df['Kilómetros'].str.replace(' Km (Verificar)', '').str.replace('.', ''), errors='coerce').fillna(pd.NA)


    return df

'''
Llama a las funciones anteriores para dejar una base limpia con todos la información de todos los coches, y lo guarda como csv
'''

def main():
    userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6.1 Safari/605.1.15'
    url_main = 'https://www.motor.es/coches-segunda-mano/coches/?pagina='
    headers = {'User-Agent': userAgent}

    columns = ['Precio al contado','Marca','Modelo','Versión','Combustible',
           'Potencia','Kilómetros','Carrocería','Matriculación','Cambio',
           'Garantía','Plazas','Puertas','Color exterior']

    info = get_data(url_main, headers, columns)

    df = pd.DataFrame(columns=columns, data=info)

    df = clean_data(df)

    df.to_csv('MotorES.csv')

if __name__ == '__main__':
    main()
