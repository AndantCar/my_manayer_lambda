#!/usr/bin/python3
# -*- encoding:utf-8 -*-

import os
import sys
import time
import logging
import argparse
import functions_helper as fh

from Manager import main_gui

__author__ = 'Carlos Añorve'
__version__ = '1.0'

usage = f'''\r{f"Version {__version__}".ljust(len("usage:"))}\nExample: Manager_cli --new --name my_function'''
parser = argparse.ArgumentParser(prog=usage, usage=usage)
parser.add_argument("--level_log",
                    type=str, choices=['debug', 'info', 'warning'], help="Define el nivel del log", default='debug')
parser.add_argument('--file_log',
                    action="store_true", help="Si se pasa como argumento genera un archivo de log.")
parser.add_argument("--update",
                    action="store_true", help='Si se pasa como argumento actualiza el codigo de una lambda.')
parser.add_argument("--new",
                    action="store_true", help='Si se pasa como argumento crea una nueva lambda.')
parser.add_argument("--gui",
                    action="store_true", help='Si se pasa como argumento inicia una gui.')
parser.add_argument("--version",
                    action="store_true", help="devuelve la version del programa.")
parser.add_argument("-p", "--PATH",
                    type=str, help='Ruta de la carpeta donde esta el proyecto', default=os.getcwd())
parser.add_argument("--FILE_CONFIG",
                    type=str, help="Define el nombre del archivo de configuracion", default="config.json")

args = parser.parse_args()

LEVEL_LOG = {'debug': logging.DEBUG, 'info': logging.INFO,
             'warning': logging.WARNING, 'error': logging.ERROR}

if args.file_log:
    logging.basicConfig(level=LEVEL_LOG[args.level_log],
                        format='%(asctime)s - %(levelname)s - %(name)s - %(lineno)d: %(message)s',
                        filename='%(prog)s.log'.format(time.strftime('%Y-%m-%d')))
else:
    logging.basicConfig(level=LEVEL_LOG[args.level_log],
                        format='%(message)s')


def main_cli(work_path, config_aws):
    if args.new:
        fh.make_new_lambda(config_aws)
    if args.update:
        print('update lambda')
    fh.finish_process(work_path, config_aws)



if __name__ == '__main__':
    if args.version:
        print(__version__)
        sys.exit(0)
    path = fh.get_path_work(args.PATH)
    config = fh.get_config(os.path.join(path, args.FILE_CONFIG))
    fh.check_code(path, config)
    config['Code'] = fh.make_zip(path, config)
    if args.gui:
        main_gui()
    else:
        main_cli(path, config)
