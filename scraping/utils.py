import requests

from bs4 import BeautifulSoup

import random

import time



def scrape_coto(producto):

    """Scraping real de Coto Digital"""

    try:

        url = f"https://www.cotodigital3.com.ar/sitios/cdigi/browse?Ntt={producto}"

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

        

        response = requests.get(url, headers=headers, timeout=10)

        soup = BeautifulSoup(response.text, 'html.parser')

        

        # Buscar el primer producto

        producto_div = soup.find('div', class_='product_info_container')

        if producto_div:

            nombre_elem = producto_div.find('a', class_='descrip_full')

            precio_elem = producto_div.find('span', class_='atg_store_newPrice')

            

            if nombre_elem and precio_elem:

                nombre = nombre_elem.text.strip()

                precio_texto = precio_elem.text.strip().replace('$', '').replace('.', '').replace(',', '.')

                try:

                    precio = float(precio_texto)

                    return {'nombre': nombre, 'precio': precio, 'encontrado': True}

                except:

                    pass

        

        return {'nombre': producto, 'precio': None, 'encontrado': False}

    except Exception as e:

        print(f"Error scraping Coto: {e}")

        return {'nombre': producto, 'precio': None, 'encontrado': False}



def scrape_dia(producto):

    """Scraping simulado de Día (tienen anti-scraping fuerte)"""

    # Simulación porque Día tiene Cloudflare

    time.sleep(0.5)

    precio = round(random.uniform(800, 4000), 2)

    return {

        'nombre': producto,

        'precio': precio,

        'encontrado': True,

        'nota': 'Precio estimado'

    }



def scrape_carrefour(producto):

    """Scraping simulado de Carrefour"""

    time.sleep(0.5)

    precio = round(random.uniform(900, 4500), 2)

    return {

        'nombre': producto,

        'precio': precio,

        'encontrado': True,

        'nota': 'Precio estimado'

    }



def comparar_precios(nombre_producto):

    """Función principal que compara precios"""

    resultados = []

    

    # Coto (scraping real)

    coto = scrape_coto(nombre_producto)

    if coto['encontrado']:

        resultados.append({

            'supermercado': 'Coto Digital',

            'precio': coto['precio'],

            'url': f"https://www.cotodigital3.com.ar/sitios/cdigi/browse?Ntt={nombre_producto}",

            'real': True

        })

    

    # Día (simulado)

    dia = scrape_dia(nombre_producto)

    if dia['encontrado']:

        resultados.append({

            'supermercado': 'Día',

            'precio': dia['precio'],

            'url': 'https://diaonline.supermercadosdia.com.ar/',

            'real': False,

            'nota': dia.get('nota', '')

        })

    

    # Carrefour (simulado)

    carrefour = scrape_carrefour(nombre_producto)

    if carrefour['encontrado']:

        resultados.append({

            'supermercado': 'Carrefour',

            'precio': carrefour['precio'],

            'url': 'https://www.carrefour.com.ar/',

            'real': False,

            'nota': carrefour.get('nota', '')

        })

    

    # Encontrar el mejor precio

    mejor_precio = None

    if resultados:

        precios_validos = [r['precio'] for r in resultados if r['precio']]

        if precios_validos:

            mejor_precio = min(precios_validos)

    

    return {

        'producto': nombre_producto,

        'resultados': resultados,

        'mejor_precio': mejor_precio,

        'total_encontrados': len(resultados)

    }

