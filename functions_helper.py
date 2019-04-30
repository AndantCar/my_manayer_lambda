#!/usr/bin/python3
# -*- encoding:utf-8 -*-


import os
import re
import sys
import json
import zipfile
import logging

import boto3
from tqdm import tqdm

try:
    import zlib
    compression = zipfile.ZIP_DEFLATED
except:
    compression = zipfile.ZIP_STORED


logger = logging.getLogger('Functions_helper')


def get_path_work(args):
    try:
        path = args.p
    except Exception as details:
        try:
            path = args.PATH
        except Exception:
            logging.error('Error al recuperar la ruta del projecto\n'
                          'Detalles: {}'.format(details))
            sys.exit(1)
    if not os.path.exists(path):
        logging.error('La ruta espesificada no existe.')
        sys.exit(1)
    return path


def make_zip(path, config):
    """

    :param path:
    :param config:
    :return:
    """
    try:
        name = config['FunctionName']
    except (KeyError, Exception):
        logger.error('Error al intetar recuperar el nombre de la funcion del archivo de configuracion.\n'
                     'asegurate de agregar la llave "FunctionName" al archivo de configuracion')
        sys.exit(1)
    name += '.zip'
    zip_path = os.path.join(path, name)
    try:
        with zipfile.ZipFile(zip_path, mode='w') as fantasy_zip:
            logger.info('Creando el archivo zip')
            for folder, subfolders, files in os.walk(path):
                for ii in tqdm(range(len(files))):
                    file = files[ii]
                    if file != name:
                        fantasy_zip.write(os.path.join(folder, file),
                                          os.path.relpath(os.path.join(folder, file), path),
                                          compress_type=zipfile.ZIP_DEFLATED)
    except Exception as details:
        logger.error('Error al intentar crcear el archivo {}\n'
                     'Detalles: {}'.format(name, details))
        sys.exit(1)
    return zip_path


def get_config(path):
    """

    :param path:
    :return:
    """
    nombre_archivo = os.path.split(path)[-1]
    try:
        with open(path, 'r') as cf:
            config = json.loads(cf.read())
    except (FileNotFoundError, Exception) as details:
        logger.error('No fue posible leer el archivo de configuracion {}\n'
                     'Detalles: {}'.format(nombre_archivo, details))
        sys.exit(1)
    return config


def get_all_nasme_lambda(client):
    paginator = client.get_paginator('list_functions')
    functions = [function_aws for function_aws in paginator.paginate()]
    if len(functions) == 1:
        functions = functions[0]
        try:
            functions = functions['Functions']
        except Exception as details:
            logger.warning('No fue posible obtener informacion de las lambdas.')
    all_functions = {}
    for i in tqdm(range(len(functions))):
        try:
            arn_function = functions[i]['FunctionArn']
            name_function = functions[i]['FunctionName']
        except (KeyError, Exception) as details:
            logger.warning('Problema al obtener informacion\nDetalles: {}'.format(details))
        else:
            all_functions[name_function] = arn_function
    return all_functions


def exist_lambda(name_new_lamdba, aws_access_key_id=None, aws_secret_access_key=None, region_name=None):
    logger.info('Verificando si existe la lambda {}'.format(name_new_lamdba))
    client = make_client('lambda', aws_access_key_id, aws_secret_access_key, region_name)
    all_lambdas = get_all_nasme_lambda(client)
    return name_new_lamdba in all_lambdas


def make_client(service, aws_access_key_id=None, aws_secret_access_key=None, region_name=None):
    """

    :param service:
    :param aws_access_key_id:
    :param aws_secret_access_key:
    :param region_name:
    :return:
    """
    try:
        logger.info(f'Try create client {service}')
        if aws_access_key_id and aws_secret_access_key and region_name:
            client = boto3.client(service,
                                  aws_access_key_id=aws_access_key_id,
                                  aws_secret_access_key=aws_secret_access_key,
                                  region_name=region_name)
        elif aws_access_key_id and aws_secret_access_key:
            client = boto3.client(service,
                                  aws_access_key_id=aws_access_key_id,
                                  aws_secret_access_key=aws_secret_access_key)
        else:
            client = boto3.client(service)
    except Exception as details:
        logger.error('Error to try make client(\'{}\')\n'
              'Details: {}'.format(service, details))
        sys.exit(1)
    else:
        logger.info(f'Se creo correctamente el cliente {service}')
        return client


def zip2byte(path):
    """

    :param path:
    :return:
    """
    try:
        logger.debug('leyendo archivo zip')
        with open(path, 'rb') as zfb:
            return zfb.read()
    except (FileNotFoundError, Exception) as error:
        logger.error('No fue posible leer el archivo zip {}\n'
                     'Detalles: {}'.format(path, error))


def make_new_lambda(kwargs):
    """

    :param kwargs:
    :return:
    """
    try:
        code = kwargs['Code']
        aws_access_key_id = kwargs['aws_access_key_id']
        aws_secret_access_key = kwargs['aws_secret_access_key']
        region_name = kwargs['region_name']
        del kwargs['aws_access_key_id']
        del kwargs['aws_secret_access_key']
        del kwargs['region_name']
    except Exception as details:
        print(details)
        return None
    if exist_lambda(kwargs['FunctionName'], aws_access_key_id, aws_secret_access_key, region_name):
        logger.warning('Ya existe ua lambda con el nombre {}'.format(kwargs['FunctionName']))
        sys.exit(1)
    kwargs['Code'] = {"ZipFile": zip2byte(code)}
    client = make_client('lambda', aws_access_key_id, aws_secret_access_key, region_name)
    try:
        response = client.create_function(**kwargs)
    except Exception as details:
        logger.error('Error al intetnar crear la funcion lambda.\n'
                     'Detalles: {}'.format(details))
        sys.exit(1)
    return response['FunctionArn']


def call_lambda(arn, event, type_invoke='Event',
                aws_access_key_id=None, aws_secret_access_key=None,
                region_name=None):
    """Call any lambda for testing.

    Use this function to test the behavior of the
    lambda function.
    Rememeber that you should have saved the configuration and
    the aws_access_key_id and the aws_secret_access_key in some
    configuration file in .aws path

    Args:
        arn (str): This is the Amazon resource Name (ARM) of your Lambda Function.
        event (dict): This is the param pased to the lambda usually a json object.
        type_invoke (str):
        aws_access_key_id (str):
        aws_secret_access_key (str):
        region_name (str):

    Returns:
        Anything that return the lambda function.
    """
    client = make_client('lambda', aws_access_key_id, aws_secret_access_key, region_name)
    # noinspection PyBroadException
    try:
        result = client.invoke(FunctionName=arn,
                               InvocationType=type_invoke,
                               Payload=json.dumps(event))

    except Exception as details:
        print(f'Error to try invoke the lambda function.\n'
              f'Detalles: {details}')
        return None
    print('Function call_lambda finish successful.')
    return result['Payload'].read()


def update_code_lambda(**kwargs):
    try:
        function_name = kwargs['FunctionName']
        code = kwargs['Code']
        aws_access_key_id = kwargs['aws_access_key_id']
        aws_secret_access_key = kwargs['aws_secret_access_key']
        region_name = kwargs['region_name']
    except KeyError as details:
        logger.error('Error al intetar recuperr la llave {} asegurate '
                     'de agregarla al archivo de configuracion'.format(details))
        return None
    code = zip2byte(code)
    client = make_client('lambda', aws_access_key_id, aws_secret_access_key, region_name)
    client.update_function_code(FunctionName=function_name, ZipFile=code)


def check_code(work_path, config):
    """

    :param work_path:
    :param config:
    :return:
    """
    try:
        handler = config['Handler']
    except (KeyError, Exception):
        logger.error('Error al intentar recuperar el Handler del archivo de configuracion.')
        sys.exit(1)
    try:
        module, function_handler = handler.split('.')
    except (ValueError, Exception) as details:
        logger.error('Error en el archivo de configuracion, el campo "Handler" no esta bien definodo\n'
                     'Detalles: {}'.format(details))
        sys.exit(1)
    module += '.py'
    re_function = re.compile(r'(def {}\()'.format(function_handler))
    try:
        with open(os.path.join(work_path, module), 'r') as python_file:
            code = python_file.read()
            if not re_function.findall(code):
                logger.error('No se encontro la funcion {} en el modulo principal.'.format(function_handler))
                sys.exit(1)
    except (FileNotFoundError, Exception) as details:
        logger.error('Problemas al encontrar el arhivo principal {}\n Detalles: {}'.format(module, details))
        sys.exit(1)


def finish_process(work_path, config):
    name = config['FunctionName']
    name += '.zip'
    try:
        os.remove(os.path.join(work_path, name))
    except Exception:
        logging.warning('No fue posible eliminar el archivo zip despues de cargar al servicio.')
    else:
        logger.info('El proceso de carga de lambda termino exitosamente.')
