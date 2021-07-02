#!/usr/bin/python3
# -*- coding: utf-8 -*-
#+ Autor:	Ran#
#+ Creado:	02/07/2021 20:55:47
#+ Editado:	03/07/2021 00:48:36
#------------------------------------------------------------------------------------------------
from conexions import proxie
import sys
from bs4 import BeautifulSoup as bs
import os
import json
from datetime import datetime
#------------------------------------------------------------------------------------------------
lig = 'https://www.paxinasgalegas.es/resultados.aspx?tipo=0&texto='
num_pax = 0
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
        for ele in args[args.index('-b')+1].split():
            lig = lig + ele + '+'
            busqueda += ele + '+'
        lig = lig[:-1]
        lig += '&pagina='
        busqueda = busqueda[:-1]
    except:
        raise Exception('Non se proporcionou valor de búsqueda')

# se quero mensaxes
if '-v' in args:
    verbose = True
else:
    verbose = False
#------------------------------------------------------------------------------------------------
# garda un ficheiro en memoria en formato json e coa extensión dada no nome
def gardarJson(ficheiro, contido, sort=False):
    open(ficheiro, 'w').write(json.dumps(contido, indent=1, sort_keys=sort, ensure_ascii=False))

# función de print pero bonita para os dics e tal formato json
#def pjson(contido, indent=4, sort=False):
#    print(json.dumps(contido, indent=indent, sort_keys=sort)
#------------------------------------------------------------------------------------------------
# request inicial
req = proxie.porProxie(verbose=verbose, maxCons=20)
soup = bs(req.get(lig+str(num_pax), timeout=10),'html.parser')

# xFCR: está mal o das páxinas
# cambialo por número de restaurantes
# número máximo de páxinas
max_pax = int(soup.find(id='spnPagRango').get_text().split('-')[1].strip())
print('> Para a búsqueda {} hai un total de {} páxinas'.format(busqueda, max_pax))

# loop para tódalas páxinas dispoñibles
for i in range(num_pax, max_pax+1):
    print('> Sacando info da páxina {} de {}'.format(num_pax, max_pax))
    
    # nomes dos locais
    for ele in soup.find_all(class_="titulo font-large text-decoration-underline"):
        nome = ele.get_text().strip()

    # números de teléfono
    for ele in soup.find_all(class_='start valign-middle font-large'):
        tfno = ele.get('data-phone')
        if not tfno: tfno = 'Non dispoñible'

    restaurantes.append({'Nome': nome, 'Tfno': tfno})

    # nova páxina
    soup = bs(req.get(lig+str(num_pax), timeout=10), 'html.parser')

gardarJson(datetime.now().strftime('%Y-%m-%d %H.%M.%S')+'_'+busqueda+'.txt', restaurantes)
#------------------------------------------------------------------------------------------------
