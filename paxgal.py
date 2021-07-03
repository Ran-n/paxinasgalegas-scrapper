#!/usr/bin/python3
# -*- coding: utf-8 -*-
#+ Autor:	Ran#
#+ Creado:	02/07/2021 20:55:47
#+ Editado:	03/07/2021 14:24:47
#------------------------------------------------------------------------------------------------
import conexions
import sys
from bs4 import BeautifulSoup as bs
import os
import json
from datetime import datetime
#------------------------------------------------------------------------------------------------
timeout = 10
lig = 'https://www.paxinasgalegas.es/resultados.aspx?tipo=0&texto='
pax_num = 0
busqueda = ''
restaurantes = []
#------------------------------------------------------------------------------------------------
args = sys.argv[1:]

# axuda
if any(['-a' in args, '-h' in args, '?' in args, len(args) == 0]):
    print('> Axuda :')
    print('-a/-h/?\t→ Esta mensaxe')
    print('-b\t→ Catex da búsqueda a realizar (con comiñas se usas espazos)')
    sys.exit()

# palabras de búsqueda
if '-b' in args:
    try:
        lig += '+'.join(args[args.index('-b')+1].split())+'&pagina='
        busqueda = ' '.join(args[args.index('-b')+1].split())
    except:
        raise Exception('Non se proporcionou valor de búsqueda')

# se quero mensaxes
if '-v' in args:
    verbose = True
else:
    verbose = False

# a carpeta de saida:
if '-o' in args:
    try:
        carpeta = args[args.index('-o')+1]
        if not os.path.exists(carpeta):
            raise Exception('A ruta especificada non existe')
    except:
        raise Exception('Non se proporcionou un valor para o path da carpeta')
    finally:
        if not carpeta.endswith('/'):
            carpeta += '/'
else:
    carpeta = './'
#------------------------------------------------------------------------------------------------
# garda un ficheiro en memoria en formato json e coa extensión dada no nome
def gardarJson(ficheiro, contido, sort=False):
    open(ficheiro, 'w').write(json.dumps(contido, indent=1, sort_keys=sort, ensure_ascii=False))

# función de print pero bonita para os dics e tal formato json
#def pjson(contido, indent=4, sort=False):
#    print(json.dumps(contido, indent=indent, sort_keys=sort)

# modifica un catex para que esté riscado
def riscar(texto):
    return ''.join([u'\u0336{}'.format(c) for c in texto])
#------------------------------------------------------------------------------------------------
# request inicial
req = conexions.porProxie(verbose=verbose, maxCons=20)

soup = bs(req.get(lig+str(pax_num), timeout=timeout),'html.parser')
result_num = int(soup.find(id='spnPagRango').get_text().split('-')[1].strip())
result_max = int(soup.find(id='spnPagTotRes').get_text())

while True:
    print('> Sacando info da páxina {}'.format(pax_num))
    print('> {} de {} resultados\n'.format(result_num, result_max))
    
    # saca lista de datos interesantes
    nomes = soup.find_all(class_="titulo font-large text-decoration-underline")
    tfnos = soup.find_all(class_='start valign-middle font-large')
    ruas =  soup.find_all(class_='calle')
    municipios = soup.find_all(class_='municipio font-weight-bold')
    descripcions = soup.find_all(class_='contenido color-text-3')
    webs = soup.find_all(class_='pie border-dotted-top-default overflow-hidden')

    for nome, tfno, rua, municipio, descripcion, web in zip(nomes, tfnos, ruas, municipios, descripcions, webs):

        nome = nome.get_text().strip()
        tfno = tfno.get('data-phone')
        tfno = tfno if tfno else 'Non dispoñible'
        rua = rua.get_text().strip()+' - '+municipio.get_text()

        try:
            web = web.find(class_='enlace_web valign-middle font-normal font-weight-bold overflow-hidden').get_text().strip()
        except:
            web = 'Non dispoñible'

        if 'Esta empresa ha cesado su actividad' in descripcion.get_text().strip():
            nome = riscar(nome)
            tfno = riscar(tfno)
            rua = riscar(rua)
            web = riscar(web)

        restaurantes.append({
            'Nome local': nome,
            'Teléfono': tfno,
            'Dirección': rua,
            'Páxina web': web
            })

    # novo request para seguinte páxina
    pax_num += 1
    if result_num != result_max:
        soup = bs(req.get(lig+str(pax_num), timeout=timeout),'html.parser')
        result_num = int(soup.find(id='spnPagRango').get_text().split('-')[1].strip())
    else:
        print('> Fin do raspado')
        break

gardarJson(carpeta+datetime.now().strftime('%Y-%m-%d %H.%M.%S')+' '+busqueda+'.txt', restaurantes)
#------------------------------------------------------------------------------------------------
