#!/usr/bin/python3
# -*- encoding:utf-8 -*-

import os
import shutil
import logging
import argparse

__author__ = 'Carlos Añorve'
__version__ = '1.0'

parser = argparse.ArgumentParser()
parser.add_argument("-l", "--log", type=str, choices=['debug', 'info', 'warning'],
                    help="Define el nivel del log", default='debug')
parser.add_argument('--install', action="store_true",
                    help="Si se pasa como argumento intalla el programa.")
parser.add_argument("-p", type=str, help='Ruta de la carpeta donde esta el ejecutable en caso de no '
                                         'estar en la misma carpeta de ete archivo')
args = parser.parse_args()

LEVEL_LOG = {'debug': logging.DEBUG, 'info': logging.INFO,
             'warning': logging.WARNING, 'error': logging.ERROR}


logging.basicConfig(level=LEVEL_LOG[args.log],
                    format='%(asctime)s - %(levelname)s - %(name)s - %(lineno)d: %(message)s')

__all__ = []


def get_path_scripts():
    enviroment_variables = os.environ
    for enviroment in dict(enviroment_variables):
        for e in dict(enviroment_variables)[enviroment].split(';'):
            if 'python' in e.lower():
                if 'scripts' in e.lower():
                    return e
    return None


def main():
    if args.install:
        path_script = get_path_scripts()
        name_program = 'Manager_cli.exe'
        if path_script:
            program = os.path.join(os.getcwd(), name_program)
            destino = os.path.join(path_script, name_program)
            try:
                shutil.copyfile(program, destino)
            except Exception as details:
                logging.error('Errro al intalar el programa.\n'
                              'Detamlles: {}'.format(details))


if __name__ == '__main__':
    main()
