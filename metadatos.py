#! /usr/bin/python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#+ Autor:  	Ran#
#+ Creado:	18/10/2021 13:50:54
#+ Editado:	2021/10/24 16:17:21.506357
# -----------------------------------------------------------------------------

#* Reescrito do script "metadata" de 2019

# -----------------------------------------------------------------------------

import sys
from datetime import datetime

from uteis import ficheiro as uf

# -----------------------------------------------------------------------------

def print_axuda():
    print()
    print('Axuda ------------------------------')
    print('?/-h/-a\t-> Para esta mensaxe')
    print('-m fich\t-> Mostrar os metadatos')
    print('-e fich\t-> Editar os metadatos')
    print('-c fich\t-> Crear os metadatos')
    print('-s fich\t-> Eliminar os metadatos')
    print('------------------------------------')
    print()

# -----------------------------------------------------------------------------

def ler_entrada():
    __args = sys.argv[1:]
    flags_axuda = ['-a', '-h', '?', '-?', '--axuda', '--help']  # Definición dos flags de axuda
    flags_opcions = ['-m', '-e', '-c', '-s']

    """
    Isto fagoo así pq sei que a entrada sempre vai ser a flag e o ficheiro nesa orde
    """
    try:
        flag = __args[0]
        fich = __args[1]
    except IndexError:
        print()
        print('ERRO: Faltan argumentos no comando')
        print_axuda()
        sys.exit()  # Pechase o programa

    # Se pide axuda ou non pon argumentos ou mete flag inexistente
    if __args in flags_axuda or len(__args) == 0 or flag not in flags_opcions:
        print_axuda()
        sys.exit()  # Pechase o programa

    return flag, fich

# -----------------------------------------------------------------------------

def mostrar(fich, tipo_fich, prime_linha, vars_esteticas):
    simb_comen = prime_linha.split('!')[0]
    contido = [ele2 for ele2 in [ele.rstrip() for ele in uf.cargarFich(fich)] if ele2.startswith(simb_comen+vars_esteticas['indicador'], 0, 4)]

    for linha in contido:
        print(linha)

# -----------------------------------------------------------------------------

def editar(fich, tipo_fich, prime_linha, vars_esteticas):
    simb_comen = prime_linha.split('!')[0]
    contido = uf.cargarFich(fich)

    agora = str(datetime.now()).replace('-', vars_esteticas['sep_datas'])
    agora = agora.replace(':', vars_esteticas['sep_horas'])
    if vars_esteticas['micro_s']:
        agora = agora.replace('.', vars_esteticas['sep_micro_s'])
    else:
        agora = agora.split('.')[0]

    for index, linha in enumerate(contido):
        if linha.startswith(simb_comen+vars_esteticas['indicador']+' Editado:', 0, 12):
            contido[index] = simb_comen+vars_esteticas['indicador']+' Editado:\t'+agora

    uf.gardarFich(fich, contido)

# -----------------------------------------------------------------------------

def crear(fich, tipo_fich, prime_linha, vars_esteticas):
    simb_comen  = prime_linha.split('!')[0]
    contido = uf.cargarFich(fich)

    agora = str(datetime.now()).replace('-', vars_esteticas['sep_datas'])
    agora = agora.replace(':', vars_esteticas['sep_horas'])
    if vars_esteticas['micro_s']:
        agora = agora.replace('.', vars_esteticas['sep_micro_s'])
    else:
        agora = agora.split('.')[0]

    insertar = [
        prime_linha,
        simb_comen+' '+vars_esteticas['coding_simb']+' coding: '+vars_esteticas['coding']+' '+vars_esteticas['coding_simb'],
        simb_comen+' -------------------------------------------------------------------------------'[:-len(simb_comen)],
        simb_comen+vars_esteticas['indicador']+' Autor:  \t'+vars_esteticas['autor'],
        simb_comen+vars_esteticas['indicador']+' Creado: \t'+agora,
        simb_comen+vars_esteticas['indicador']+' Editado:\t'+agora,
        simb_comen+' -------------------------------------------------------------------------------'[:-len(simb_comen)]+'\n'
    ]

    # se o ficheiro non ten ningún contido
    if not contido:
        if len(prime_linha) < 4:
            contido = insertar[1:].copy()
        else:
            contido = insertar.copy()
    else:
        if len(prime_linha) < 4:
            insertar = insertar[1:]
        for index, insertable in enumerate(insertar):
            if insertable[:5] != contido[index][:5]:
                contido.insert(index, insertable)

    uf.gardarFich(fich, contido)

# -----------------------------------------------------------------------------

def suprimir(fich, tipo_fich, prime_linha, vars_esteticas):
    simb_comen = prime_linha.split('!')[0]
    contido_ini = uf.cargarFich(fich)

    contido = []
    for linha in contido_ini:
        if not linha.startswith(simb_comen+vars_esteticas['indicador'], 0, 4):
            contido.append(linha)

    uf.gardarFich(fich, contido)

# -----------------------------------------------------------------------------

def executar(flag, fich, x_tipo_fich, vars_esteticas):
    opcions = {
        '-m': mostrar,
        '-e': editar,
        '-c': crear,
        '-s': suprimir
    }

    tipo_fich = '.'+fich.split('.')[-1]
    opcions[flag](fich, tipo_fich, x_tipo_fich.get(tipo_fich, '#!'), vars_esteticas)

# -----------------------------------------------------------------------------

def main():
    # Linha inicial para a execución do ficheiro, se non precisa ponher o simbolo de comentario
    x_tipo_fich = {
        '.py':      '#! /usr/bin/env python3',
        '.sh':      '#! /bin/sh',
        '.bash':    '#! /bin/bash',
        '.rs':      '//',
    }

    #
    vars_esteticas= {
            'autor':        'Ran#',
            'coding':       'utf-8',
            'coding_simb':  '-*-',
            'indicador':    '+',    # Coidado ó cambiar isto pq non funcionará o editar sobre indicadores antigos
            'sep_datas':    '/',
            'sep_horas':    ':',
            'micro_s':      True,
            'sep_micro_s':  '.'
    }

    flag, fich = ler_entrada()
    executar(flag, fich, x_tipo_fich, vars_esteticas)

# -----------------------------------------------------------------------------

if __name__ == '__main__':
    main()

# -----------------------------------------------------------------------------
