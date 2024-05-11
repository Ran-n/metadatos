#! /usr/bin/python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#+ Autor:  	Ran#
#+ Creado:	18/10/2021 13:50:54
#+ Editado:	2024/05/11 15:13:16.161454
# -----------------------------------------------------------------------------

#* Reescrito do script "metadata" de 2019

# -----------------------------------------------------------------------------

import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Union

# -----------------------------------------------------------------------------
# UTILS
# -----------------------------------------------------------------------------

def save_file(
        fname: str,
        content: Union[str, List[str]],
        encoding='utf-8-sig'
    ) -> bool:
    """
    Saves a file to memory once given its name, with or without a path. Without
    a path its saved to the current folder, otherwise where pointed to.

    @in:
    ├─ fname
    │  └ Name of the file, with extension and path.
    ├─ in_lines
    │  ├ True: Load in an list each line of the file as a String.
    │  └ False: Load the whole file as one String.
    └─ encoding
       └ Indicates the type of encoding to use.

    @out:
    ├─ List[String]
    │  └ Contents of the file in a list divided by line.
    └─ String
       └ Contents of the file as one single string.
    """

    # create the path if non existant
    """
    It can be done using the parent attr since the last element of the pathname
    is the name of the file itself.

    If it has no previous path (like ./file.txt or file.txt) it wont create anything
    but otherwise the path will be created if needed (like on ./test/test1/file.txt the
    folder structure created will be ./test/test1 if its non previously existant).
    """
    Path(fname).parent.mkdir(parents=True, exist_ok=True)

    with open(fname, 'w', encoding=encoding) as f:
        f.writelines('%s\n' % line for line in content)
# -----------------------------------------------------------------------------

def load_file(
        fname: Union[str, List[str]],
        in_lines: Optional[bool] =True,
        encoding: Optional[str] ='utf-8-sig'
    ) -> Union[str, List[str]]:
    """
    Given a filename as a string loads the contents in a list, line by line.

    @in:
    ├─ fname
    │  └ Name of the file, with extension and path.
    ├─ in_lines
    │  ├ True: Load in an list each line of the file as a String.
    │  └ False: Load the whole file as one String.
    └─ encoding
       └ Indicates the type of encoding to use.


    @out:
    ├─ List[String]
    │  └ Contents of the file in a list divided by line.
    └─ String
       └ Contents of the file as one single string.
    """

    if not Path(fname).is_file():
        raise Exception(f'O ficheiro {fname} non existe')

    with open(fname, 'r', encoding=encoding) as f:
        if in_lines:
            return f.read().splitlines()
        else:
            return f.read()
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
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

def trocear_prime_linha(prime_linha):
    if type(prime_linha) == list:
        return prime_linha[0], ' '+prime_linha[1]
    return prime_linha, ''

# -----------------------------------------------------------------------------

def mostrar(fich, tipo_fich, prime_linha, vars_esteticas):
    prime_linha, _ = trocear_prime_linha(prime_linha)
    simb_comen = prime_linha.split('!')[0]
    contido = [ele2 for ele2 in [ele.rstrip() for ele in load_file(fich)] if ele2.startswith(simb_comen+vars_esteticas['indicador'], 0)]

    for linha in contido:
        print(linha)

# -----------------------------------------------------------------------------

def editar(fich, tipo_fich, prime_linha, vars_esteticas):
    prime_linha, simb_fin_comen = trocear_prime_linha(prime_linha)
    simb_comen = prime_linha.split('!')[0]
    contido = load_file(fich)

    agora = str(datetime.now()).replace('-', vars_esteticas['sep_datas'])
    agora = agora.replace(':', vars_esteticas['sep_horas'])
    if vars_esteticas['micro_s']:
        agora = agora.replace('.', vars_esteticas['sep_micro_s'])
    else:
        agora = agora.split('.')[0]

    for index, linha in enumerate(contido):
        if linha.startswith(simb_comen+vars_esteticas['indicador']+' Editado:', 0):
            contido[index] = simb_comen+vars_esteticas['indicador']+' Editado:\t'+agora+simb_fin_comen

    save_file(fich, contido)

# -----------------------------------------------------------------------------

def crear(fich, tipo_fich, prime_linha, vars_esteticas):
    prime_linha, simb_fin_comen = trocear_prime_linha(prime_linha)
    simb_comen  = prime_linha.split('!')[0]
    contido = load_file(fich)

    agora = str(datetime.now()).replace('-', vars_esteticas['sep_datas'])
    agora = agora.replace(':', vars_esteticas['sep_horas'])
    if vars_esteticas['micro_s']:
        agora = agora.replace('.', vars_esteticas['sep_micro_s'])
    else:
        agora = agora.split('.')[0]

    insertar = [
        simb_comen+' '+vars_esteticas['coding_simb']+' coding: '+vars_esteticas['coding']+' '+vars_esteticas['coding_simb']+simb_fin_comen,
        simb_comen+' -------------------------------------------------------------------------------'[:-len(simb_comen)]+simb_fin_comen,
        simb_comen+vars_esteticas['indicador']+' Autor:  \t'+vars_esteticas['autor']+simb_fin_comen,
        simb_comen+vars_esteticas['indicador']+' Creado: \t'+agora+simb_fin_comen,
        simb_comen+vars_esteticas['indicador']+' Editado:\t'+agora+simb_fin_comen,
        simb_comen+' -------------------------------------------------------------------------------'[:-len(simb_comen)]+simb_fin_comen,
        '',
    ]

    # crear un campo en vars_esteticas en lugar de facer hardcode
    if '!' in prime_linha: insertar.insert(0, prime_linha)

    # se o ficheiro non ten ningún contido
    if not contido:
            contido = insertar.copy()
    else:
        for index, insertable in enumerate(insertar):
            try:
                if insertable != contido[index]:
                    contido.insert(index, insertable)
            except IndexError:
                contido.insert(index, insertable)

    save_file(fich, contido)

# -----------------------------------------------------------------------------

def suprimir(fich, tipo_fich, prime_linha, vars_esteticas):
    prime_linha, _ = trocear_prime_linha(prime_linha)
    simb_comen = prime_linha.split('!')[0]
    contido_ini = load_file(fich)

    contido = []
    for linha in contido_ini:
        if not linha.startswith(simb_comen+vars_esteticas['indicador'], 0):
            contido.append(linha)

    save_file(fich, contido)

# -----------------------------------------------------------------------------

def executar(flag, fich, x_tipo_fich, vars_esteticas):
    opcions = {
        '-m': mostrar,
        '-e': editar,
        '-c': crear,
        '-s': suprimir
    }

    tipo_fich = '.'+fich.split('.')[-1]
    opcions[flag](fich, tipo_fich, x_tipo_fich.get(tipo_fich, '#'), vars_esteticas)

# -----------------------------------------------------------------------------

def main():
    # Linha inicial para a execución do ficheiro.
    # Se non, precisa ponher o simbolo de comentario.
    x_tipo_fich = {
        '.py':      '#! /usr/bin/env python3',
        '.sh':      '#! /bin/sh',
        '.bash':    '#! /bin/bash',
        '.rs':      '//',
        '.md':      ['[//]: # (', ')'],
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
