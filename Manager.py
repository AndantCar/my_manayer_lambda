#!/usr/bin/python3
# -*- encoding:utf-8 -*-

import os
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5 import QtWidgets

import functions_helper as fh

__author__ = 'Carlos Añorve'
__version__ = '1.0'


class Example(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(Example, self).__init__(*args, **kwargs)
        self.__vbox = QtWidgets.QVBoxLayout()
        self.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
        self.initUI()
        self.__work_path = None

    def confirmation(self, nombre_confirmacion, pregunta):
        buttonReply = QtWidgets.QMessageBox.question(self, nombre_confirmacion, pregunta,
                                                     QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                     QtWidgets.QMessageBox.No)

        if buttonReply == QtWidgets.QMessageBox.Yes:
            return True
        else:
            return False

    def buscar_archivo(self):
        file, _ = QtWidgets.QFileDialog.getOpenFileName(self,
                                                        'selecciones el archivo de configuración',
                                                        os.getcwd(), "All Files (*);;Text Files (*.txt)")
        if file:
            self.__work_path = file
            config = fh.get_config(self.__work_path)
            if self.confirmation('Nueva lambda', 'Esta seguro que queire '
                                                 'crear la lambda: {}?'.format(config['FunctionName'])):
                fh.check_code(os.path.split(self.__work_path)[0], config)
                config['Code'] = fh.make_zip(os.path.split(self.__work_path)[0], config)
                self.statusBar().showMessage('Ready')
                self.statusBar().showMessage('Cargando...')
                fh.make_new_lambda(config)
                self.statusBar().showMessage('Carga exitosa.')

    def initUI(self):
        # Opciones de menu
        new_lmd_act = QtWidgets.QAction(QIcon('new.png'), '&New Lambda', self)
        exit_act = QtWidgets.QAction(QIcon('exit.ico'), '&Exit', self)

        exit_act.setShortcut('Ctrl+W')
        exit_act.setStatusTip('Exit application')
        exit_act.triggered.connect(QtWidgets.qApp.quit)
        new_lmd_act.setShortcut('Ctrl+n')
        new_lmd_act.setStatusTip('Crear una nueva lambda')
        new_lmd_act.triggered.connect(self.buscar_archivo)

        # status bar
        self.statusBar()

        # Barra de menu
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(new_lmd_act)
        fileMenu.addAction(exit_act)

        # Botones

        self.setMaximumSize(300, 320)
        self.setMinimumSize(300, 320)
        self.setWindowTitle("Manager Lambdas")
        self.statusBar().showMessage('Ready')
        self.show()


def main_gui():
    app = QtWidgets.QApplication(sys.argv)
    dialig = Example()
    dialig.show()
    sys.exit(app.exec_())
