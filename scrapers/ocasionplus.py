# Este modulo sirve para importar las librerias y configurar el driver

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
import requests
import time
from bs4 import BeautifulSoup
import pandas as pd

'''
Este modulo recibe el driver, el tamaño que llevamos y la lista de los links obtenidos,
y obtiene los nuevos, ya que este codigo se ejecuta cuando se han cargado coches nuevos
'''

def treat_link(driver,last,hechos):
    
    links = []
    time.sleep(0.5)
    all_cars = driver.find_element(By.CLASS_NAME, 'filteredVehiclesList_containerList__h2ICi')
    cars_list = all_cars.find_elements(By.CLASS_NAME, 'cardVehicle_card__LwFCi')
    cars_list = cars_list[last:]
    
    for car in cars_list:
        link = car.find_element(By.TAG_NAME, 'a').get_attribute('href')
        if link not in hechos:
            with open('links_OcasionPlus.txt', 'a') as file:
                file.write(link + '\n')

            links.append(link)
                       
    return links

'''
Este modulo hace scroll, posiciona el navegador en el último elemento por cargar y hace click en "ver más",
luego dentro de un bucle while espera a que el número de coches cargados cambie, en ese momemnto sale del bucle y obtiene los links nuevos llamando a la función anterior
'''
        
def scroll(driver,wait,hechos):

    correct = False
    links = []

    try:
    
        all_cars = driver.find_element(By.CLASS_NAME, 'filteredVehiclesList_containerList__h2ICi')
        cars_list = all_cars.find_elements(By.CLASS_NAME, 'cardVehicle_card__LwFCi')
        presentes = len(cars_list)

        while True:
        
            try:
                elemento = wait.until(ec.presence_of_element_located((By.CLASS_NAME,'vehicleLoadingCard_loadingCard__QUeqv')))
                elemento = driver.find_elements(By.CLASS_NAME,'vehicleLoadingCard_loadingCard__QUeqv')[-1]
                location = elemento.location
                driver.execute_script(f"window.scrollTo({location['x']}, {location['y']});")
                ver_mas = wait.until(ec.element_to_be_clickable((By.CLASS_NAME,'seeMoreCars_container__3IAiQ')))
                ver_mas.click()

                if (len(links) + len(hechos)) % 100 == 0:
                    print('Llevamos: ',len(links) + len(hechos),' links')
        
            except:
                if len(hechos) > 5000:
                    print('Se han obtenido todos los coches')
                    correct = True
                
                break
            
            while True:
                
                all_cars = driver.find_element(By.CLASS_NAME, 'filteredVehiclesList_containerList__h2ICi')
                cars_list = all_cars.find_elements(By.CLASS_NAME, 'cardVehicle_card__LwFCi')
                presentes2 = len(cars_list)
        
                if presentes != presentes2:
                    presentes = presentes2
                    break
            
            new_links = treat_link(driver,len(links),hechos)
            links.extend(new_links)

    except:
        print('El servidor ha bloqueado la IP')
        
    return links,correct

'''
Este modulo sirve para abrir el driver, pulsar el aceptar cookies y llamar a las funciones anteriores para obtener todos los links. Por algun motivo a veces no salta la notificacion de las cookies,
por lo que utilizamos un wait largo de 8 segundos dentro de un try except, y luego disminuimos el wait a 2 segundos
'''

def get_links(links):

    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 8)    
    path ='https://www.ocasionplus.com/coches-ocasion'
    driver.get(path)
    driver.implicitly_wait(1)

    try:
        buton = wait.until(ec.element_to_be_clickable((By.XPATH,'//*[@id="CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"]')))
        buton.click()
        print('Se han pulsado las cookies')
        time.sleep(1)
    except:
        pass

    wait = WebDriverWait(driver, 2) 

    new_links,correct = scroll(driver,wait,links)
    links.extend(new_links)

    if correct:
        driver.quit()

    return links,correct


# FUNCIONES INDIVIDUALES PARA CADA ATRIBUTO:

'''
Estas funciones sirven para obtener las diferentes variables de cada coche, como la marca, nombre, pegatina ambiental...
'''

def sc_marca(sopa):
    elemento = sopa.find('div', class_='layout_breadcrumbsBackgroundContainer__3TPJ4')
    elemento = elemento.find('ul',class_='Breadcrumb_breadcrumb__w6hWb').find_all('li')
    return elemento[2].get_text()

def sc_nombre(sopa):
    elemento = sopa.find('div', class_='Tittle_container__QT9ed')
    elemento = elemento.find('h1',class_='Tittle_brand__9nRGz')
    return elemento.get_text()

def sc_pegatina(sopa):
    elemento = sopa.find('div', class_='Tittle_container__QT9ed')
    elemento = elemento.find('img', class_='icon_icon__EUcfw')
    pegatina = elemento.get('src')
    pegatina = pegatina.split('/')[3].split('.')[0]
    return pegatina

def sc_anyo(sopa):
    elemento = sopa.find('div', class_='characteristics_content__vqUuu characteristics_details__fYE8e')
    elemento = elemento.find('span', {'data-test':'span-registration-date'})
    anyo = elemento.get_text()
    anyo = int(anyo)
    return anyo

def sc_km(sopa):
    elemento = sopa.find('div', class_='characteristics_content__vqUuu characteristics_details__fYE8e')
    elemento = elemento.find('span', {'data-test':'span-km'})
    km = elemento.get_text()
    km = km.split()[0].replace('.','')
    km = int(km)
    return km

def sc_combustible(sopa):
    elemento = sopa.find('div', class_='characteristics_content__vqUuu characteristics_details__fYE8e')
    elemento = elemento.find('span', {'data-test':'span-fuel-type'})
    com = elemento.get_text()
    return com

def sc_cv(sopa):
    elemento = sopa.find('div', class_='characteristics_content__vqUuu characteristics_details__fYE8e')
    elemento = elemento.find('span', {'data-test':'span-engine-cv'})
    cv = elemento.get_text().split()[0]
    cv = int(cv)
    return cv

def sc_marchas(sopa):
    elemento = sopa.find('div', class_='characteristics_content__vqUuu characteristics_details__fYE8e')
    elemento = elemento.find('span', {'data-test':'span-engine-transmission'})
    m = elemento.get_text()
    return m

def sc_1owner(sopa):
    elemento = sopa.find('div', class_='characteristics_content__vqUuu characteristics_details__fYE8e')
    elemento = elemento.find('span', {'data-test':'span-onlyowner'})
    if elemento:
        return True
    else:
        return False

def sc_location(sopa):
    elemento = sopa.find('div', class_='Location_location__EIMAI')
    elemento = elemento.find('span',class_='Location_dealer__UX6kR')
    l = elemento.get_text().split()[0]
    return l

def sc_largo(sopa):
    elemento = sopa.find('div', class_='MeasuresInfo_container__BlbGX')
    elemento = elemento.find('div', class_='Measures_measuresImage__MbdYm')
    elemento = elemento.find('p', class_='Measures_measuresImage_column_value__6Y_Fr')
    l = elemento.get_text()[:-1].replace(',','.')
    l = float(l)
    return l

def sc_ancho(sopa):
    elemento = sopa.find('div', class_='MeasuresInfo_container__BlbGX')
    elemento = elemento.find('div', class_='Measures_measuresImage_column_height__V3Nlf')
    elemento = elemento.find('p', class_='Measures_measuresImage_column_value__6Y_Fr')
    ancho = elemento.get_text()[:-1].replace(',','.')
    ancho = float(ancho)
    return ancho

def sc_alto(sopa):
    elemento = sopa.find('div', class_='MeasuresInfo_container__BlbGX')
    elemento = elemento.find('div', class_='Measures_measuresImage_column_height__V3Nlf')
    elemento = elemento.find('p', class_='Measures_measuresImage_column_height_value__GGN7W')
    alto = elemento.get_text()[:-1].replace(',','.')
    alto = float(alto)
    return alto

def sc_peso(sopa):
    elemento = sopa.find('div', class_='Measures_measuresCapacity__nJr3H')
    elemento = elemento.find_all('p', class_='Measures_measuresCapacity_value__i4Gep')
    kg = elemento[0].get_text().split()[0].replace('.','')
    kg = int(kg)
    return kg

def sc_maletero(sopa):
    elemento = sopa.find('div', class_='Measures_measuresCapacity__nJr3H')
    elemento = elemento.find_all('p', class_='Measures_measuresCapacity_value__i4Gep')
    L = elemento[1].get_text()[:-1]
    return L

def sc_deposito(sopa):
    elemento = sopa.find('div', class_='Measures_measuresCapacity__nJr3H')
    elemento = elemento.find_all('p', class_='Measures_measuresCapacity_value__i4Gep')
    e = elemento[2].get_text()
    return e

def sc_Vmax(sopa):
    elemento = sopa.find('div', class_='Performance_measures__0y6vO')
    elemento = elemento.find_all('div', class_='Performance_measure__e35L8')
    elemento = elemento[0]
    elemento = elemento.find('span', class_='CircleMeasurement_label__s3TbX')
    V = elemento.get_text()
    V = int(V)
    return V

def sc_ceroAcien(sopa):
    elemento = sopa.find('div', class_='Performance_measures__0y6vO')
    elemento = elemento.find_all('div', class_='Performance_measure__e35L8')
    elemento = elemento[1]
    elemento = elemento.find('span', class_='CircleMeasurement_label__s3TbX')
    v = elemento.get_text()
    v = float(v)
    return v

def sc_consumo(sopa):
    elemento = sopa.find('div', class_='Performance_measures__0y6vO')
    elemento = elemento.find_all('div', class_='Performance_measure__e35L8')
    elemento = elemento[2]
    elemento = elemento.find('span', class_='CircleMeasurement_label__s3TbX')
    c = elemento.get_text()
    c = float(c)
    return c

def sc_emisiones(sopa):
    elemento = sopa.find('div', class_='Performance_measures__0y6vO')
    elemento = elemento.find_all('div', class_='Performance_measure__e35L8')
    elemento = elemento[3]
    elemento = elemento.find('span', class_='CircleMeasurement_label__s3TbX')
    e = elemento.get_text()
    e = int(e)
    return e

def sc_keys(sopa):
    elemento = sopa.find('div', class_='BasicData_container__mGhW5')
    elemento = elemento.find_all('div', class_='BasicData_element__DpM13')
    elemento = elemento[3]
    elemento = elemento.find('span', class_='BasicData_description__byjx4')
    elemento = elemento.find('span', class_='BasicData_value__KNbk4')
    k = elemento.get_text()
    k = int(k)
    return k

def sc_ext_num(sopa):
    elemento = sopa.find('div', class_='specs_dropdownContainer__RI6Ro specs_transition_active__dWfqy')
    elemento = elemento.find('div', class_='dropdown_listContainer__YH6Un')
    elemento = elemento.find('ul', class_='dropdown_listStyle__GokCt')
    elemento = elemento.find_all('li')
    return len(elemento)

def sc_price(sopa):
    elemento = sopa.find('div', class_='Promotions_promotion__O_Dhy')
    if elemento:
        elemento = elemento.find('div',class_='Promotions_containerDescription__RvHc_')
        elemento = elemento.find_all('div',class_='Promotions_description__1H7gD')
        elemento = elemento[1]
        elemento = elemento.find_all('span',class_='Promotions_descriptionDiscount__NbMD2')
    
    else:
        elemento = sopa.find('div', class_='NotPromotion_containerDescription__408Tq')
        elemento = elemento.find('div',class_='NotPromotion_description__h_CE4')
        elemento = elemento.find_all('span',class_='NotPromotion_descriptionDiscount__Qs7oX')
        
    e = elemento[1].get_text()
    e = e[:-1].replace('.','')
    e = int(e)
    return e

def sc_carfax(sopa):
    try:
        el = sopa.find('div', class_='card_card__LpZF7 card_padded__2M_qi')
        el2 = el.find('a', class_='button_button__HOmVR button_link__am7Rj HistoryOption_itemBtn__EQq13')
        new_link = el2['href']
        return hash(new_link)
    except:
        return None

'''
Dada la url del coche, utilizando requests y beautifulsoup, llamamos a las funciones anteriores y almacenamos todas las variables del coche en un diccionario,
si ocurre un error obteniendo alguna variable, o el valor es -, se pone el valor como nulo
'''

def link_info(url):

    response = requests.get(url)
    
    if response.status_code not in [200,202]:
        return None
        
    response_url = response.url

    if response_url != url:
        return None
        
    soup = BeautifulSoup(response.text, 'html.parser')
    
    result = {}
    
    operations = {
        "Brand": sc_marca,
        "Name": sc_nombre,
        "Sticker": sc_pegatina,
        "Year": sc_anyo,
        "KM": sc_km,
        "Fuel": sc_combustible,
        "CV": sc_cv,
        "Transmission": sc_marchas,
        "One_owner": sc_1owner,
        "Location": sc_location,
        "Length": sc_largo,
        "Width": sc_ancho,
        "Height": sc_alto,
        "Weight": sc_peso,
        "Trunk": sc_maletero,
        "Tank": sc_deposito,
        "Vmax": sc_Vmax,
        "0to100": sc_ceroAcien,
        "Consumption": sc_consumo,
        "Emissions": sc_emisiones,
        "Keys_num": sc_keys,
        "Extras_num": sc_ext_num,
        "Price": sc_price,
        "Carfax_id":sc_carfax}

    for var,operation in operations.items():
        try:
            value = operation(soup)
            if value == '-':
                value = None
        except:
            value = None

        result[var] = value

    return result

'''
Este es el programa main que utiliza todos los modulos anteriores para obtener todos los datos de todos los coches y pasarlos a un dataframe en csv,
el programa se vuelve a ejecutar si ocurre algun error siempre y cuando no se hayan obtenido almenos 6000 coches, ya que a veces bloqueaban la ip
'''

def main():

    inicio = time.time()

    print('Iniciando programa')
    print()

    links = []
    correct = False

    while correct == False:
        new_links,correct = get_links(links)
        links.extend(new_links)

        if len(links) >6000:
            correct = True
    
    links = set(links)
    links = list(links)
    
    fin = time.time()

    print('Se han obtenido todos los links posibles: ',len(links),' en ',fin-inicio,' segundos')
    print()
    print('Sacando información de los links')

    
    info = []

    for link in links:
        result = link_info(link)
        if result:
            info.append(result)
        
        if len(info) % 100 == 0:
            print('Se han obtenido ',len(info),' coches')

    fin2 = time.time()  
    
    print('Se ha obtenido la información de ',len(info),' coches en ',fin2-fin,' segundos')
    
    df = pd.DataFrame(info)
    df.to_csv('OcasionPlusData.csv')
    print('Se ha guardado el archivo OcasionPlusData.csv')

if __name__ == '__main__':
    main()

    
