import os
import re
import unidecode
import importlib_resources
from .utils import create_key_and_request, check_password_match_to_key, if_file_exists, check_cert_match_key
from .utils import if_file_is_cert, create_pkcs12
from .cemaim import CeMaIm, get_mail_client_names, get_mail_client_shortcut
from PyQt5 import QtWidgets, uic, QtCore, QtGui
from pathlib import Path
#from PyQt5.QtCore import *
#from PyQt5.QtGui import *


class Gui:
    '''
    This class is for using GUI to
        - import certificates to email client
        - create request and key certificate
        - create pkcs12 certificate
    '''
    def __init__(self, config_map = None, debug = False):
        self.debug = debug
        self.app = QtWidgets.QApplication([])
        self.window = QtWidgets.QDialog()
        self.window.setMaximumWidth(521)
        self.window.setMaximumHeight(561)
        with importlib_resources.open_text('cemaim', 'cemaim.ui') as f:
            self.window = uic.loadUi(f)
#        with open('cemaim.ui', encoding='utf-8') as f:
#            uic.loadUi(f, self.window)
        self.config_map = config_map
        self.message = ""
        self.status_code = 0

        self.imp_user_cert_path = [Path("")]
        self.p12_user_cert_path = [Path("")]
        self.p12_user_key_path = [Path("")]

        self.__import_form__()
        self.__p12_form__()
        self.__create_request_form__()

        if self.config_map != None:
            self.__set_values_by_config_map__()
            self.__set_mail_client_by_config_map__()
        else:
            self.config_map = {}
            self.config_map['imp_mail'] = 'thb'

    def __set_mail_client_by_config_map__(self):
        '''
        Set comboBox of mail client by selected one from config file
        '''
        counter = 0
        for i in get_mail_client_names():
            if get_mail_client_shortcut(i) == self.config_map['imp_mail']:
                self.imp_mail.setCurrentIndex(counter)
                break
            counter += 1

    def __set_values_by_config_map__(self):
        '''
        Set values by what were readed from config file
        '''
        key_config_mapping  = {
            'req_country' : self.req_sub_C,
            'req_state_province' : self.req_sub_ST,
            'req_location' : self.req_sub_L,
            'req_organization' : self.req_sub_O,
            'req_folder' : self.req_location_path,
            'imp_ca' : self.imp_ca_path,
            'imp_folder' : self.imp_folder_path,
            'imp_user_cert' : self.imp_user_cert_butt,
            'p12_pem' : self.p12_user_cert,
            'p12_key' : self.p12_user_key
        }
        key_path_config_mapping = {
            'p12_pem' : self.p12_user_cert_path,
            'p12_key' : self.p12_user_key_path,
            'imp_user_cert' : self.imp_user_cert_path,
        }
        for (key,value) in self.config_map.items():
            if key in key_config_mapping.keys():
                if type(key_config_mapping[key]) == QtWidgets.QPushButton:
                    # Parse file
                    file_path = Path(value)
                    key_config_mapping[key].setText(file_path.name)
                else:
                    key_config_mapping[key].setText(value)
            if key in key_path_config_mapping.keys():
                key_path_config_mapping[key][0] = Path(value)
#                print(key, value)
#        self.req_sub_C.setText( self.config_map['req_country'])

    def errorMessage(self, text):
        '''
        Set warning error message when some error happen
        '''
        self.message = text
        self.status_code = 1
        if (self.debug == False):
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setWindowTitle("Message box")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.setText(text)
            retval = msg.exec()
        else:
            print(self.message)
            print(self.status_code)

    def get_file(self, folder_location_object, file_path, suffixes):
        '''
        File dialog menu and path will be stored at specified variable
        '''
        dialog = QtWidgets.QFileDialog(self.window, 'Open file', str(Path(file_path[0]).absolute()), suffixes)
        dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            file_path[0] = Path(dialog.selectedFiles()[0])
            folder_location_object.setText(Path(file_path[0]).name)

    def get_file_write_line(self, folder_location_object, suffixes):
        '''
        File dialog and path is stored to label
        '''
        dialog = QtWidgets.QFileDialog(self.window, 'Open file', str(Path(folder_location_object.text()).absolute()), suffixes)
        dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            file_path = Path(dialog.selectedFiles()[0])
            folder_location_object.setText(str(file_path))

    def get_folder(self, folder_location_object):
        '''
        File dialog to choose store folder
        '''
        dialog = QtWidgets.QFileDialog(self.window, 'Storage of certificate and key', folder_location_object.text())
        dialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            folder_location_object.setText(dialog.selectedFiles()[0])

    def __create_request_form__(self):
        '''
        Init request tab. Search button and set buttons methods
        '''
        self.req_name = self.window.findChild(QtWidgets.QLineEdit, 'req_name')
        self.req_surname = self.window.findChild(QtWidgets.QLineEdit, 'req_surname')
        self.req_location = self.window.findChild(QtWidgets.QPushButton, 'req_location')
        self.req_location_path = self.window.findChild(QtWidgets.QLabel, 'req_location_path')

        self.req_location.clicked.connect(lambda:self.get_folder(self.req_location_path))

        self.req_password = self.window.findChild(QtWidgets.QLineEdit, 'req_password')
        self.req_password_confirm = self.window.findChild(QtWidgets.QLineEdit, 'req_password_confirm')
        self.req_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.req_password_confirm.setEchoMode(QtWidgets.QLineEdit.Password)

        self.req_sub_C = self.window.findChild(QtWidgets.QLineEdit, 'req_sub_C')
        self.req_sub_ST = self.window.findChild(QtWidgets.QLineEdit, 'req_sub_ST')
        self.req_sub_L = self.window.findChild(QtWidgets.QLineEdit, 'req_sub_L')
        self.req_sub_O = self.window.findChild(QtWidgets.QLineEdit, 'req_sub_O')
        self.req_sub_EA = self.window.findChild(QtWidgets.QLineEdit, 'req_sub_EA')


        self.req_OK = self.window.findChild(QtWidgets.QPushButton, 'req_OK')
        self.req_OK.clicked.connect(lambda:self.preprocess_create_key_and_request())


    def preprocess_create_key_and_request(self):
        '''
        Do some check and run method to create key and request
        '''
        ## TODO check if password and confirm match
        name = unidecode.unidecode(self.req_name.text())
        name = re.sub('[ ]*$', '', name)
        name = re.sub('^[ ]*', '', name)
        surname = unidecode.unidecode(self.req_surname.text())
        surname = re.sub('[ ]*$', '', surname)
        surname = re.sub('^[ ]*', '', surname)

        if name == "" and surname == "":
            self.errorMessage("Name and surname are empty.")
            return
        if self.req_password.text() != self.req_password_confirm.text():
            self.errorMessage("Password and confirm password do not match.")
            return
        if self.req_password.text() == "" :
            self.errorMessage("Password is empty. Type some password.")
            return
        ## Check folder
        if os.path.exists(self.req_location_path.text()) == False:
            self.errorMessage("Path to this folder does not exist. Choose another one.")


        subject_dict = {}
        if self.req_sub_C.text() != "":
            subject_dict['C'] = self.req_sub_C.text()
        if self.req_sub_ST.text() != "":
            subject_dict['ST'] = self.req_sub_ST.text()
        if self.req_sub_L.text() != "":
            subject_dict['L'] = self.req_sub_L.text()
        if self.req_sub_O.text() != "":
            subject_dict['O'] = self.req_sub_O.text()
        if self.req_sub_EA.text() != "":
            subject_dict['emailAddress'] = self.req_sub_EA.text()

        ## TODO confirm message?

#        print(name, surname, self.req_password.text(), subject_dict, self.req_location_path.text())
        create_key_and_request(name, surname, self.req_password.text(), subject_dict, self.req_location_path.text())
        self.message = ""
        self.status_code = 0


    def __import_form__(self):
        '''
        Init import form for email client
        '''
        self.imp_mail = self.window.findChild(QtWidgets.QComboBox, 'imp_mail')
#        self.imp_ca_location = self.window.findChild(QtWidgets.QComboBox, 'imp_ca_location')
        self.imp_ca_path = self.window.findChild(QtWidgets.QLineEdit, 'imp_ca_path')
        self.imp_ca_butt = self.window.findChild(QtWidgets.QPushButton, 'imp_ca_butt')
#        self.imp_folder_location = self.window.findChild(QtWidgets.QComboBox, 'imp_folder_location')
        self.imp_folder_path = self.window.findChild(QtWidgets.QLineEdit, 'imp_folder_path')
        self.imp_folder_butt = self.window.findChild(QtWidgets.QPushButton, 'imp_folder_butt')
        self.imp_user_cert = self.window.findChild(QtWidgets.QLabel, 'imp_user_cert')
        self.imp_user_cert_butt = self.window.findChild(QtWidgets.QPushButton, 'imp_user_cert_butt')
        self.imp_password = self.window.findChild(QtWidgets.QLineEdit, 'imp_password')

        # Config Mail
        self.imp_mail.addItems(get_mail_client_names())
        self.imp_mail.currentIndexChanged.connect(lambda:self.mail_changed(self.imp_mail.currentText()))

        # Password
        self.imp_password.setEchoMode(QtWidgets.QLineEdit.Password)

        # Personal certificate
        self.imp_user_cert_butt.clicked.connect(lambda:self.get_file(self.imp_user_cert_butt, self.imp_user_cert_path, "Pkcs12 files (*.p12);;All files (*.*)"))
        self.imp_ca_butt.clicked.connect(lambda:self.get_file_write_line(self.imp_ca_path, "Pem files (*.pem);;All files (*.*)"))
        self.imp_folder_butt.clicked.connect(lambda:self.get_folder(self.imp_folder_path))

        self.imp_OK = self.window.findChild(QtWidgets.QPushButton, 'imp_OK')
        self.imp_OK.clicked.connect(lambda:self.preprocess_imp())

    def preprocess_imp(self):
        '''
        Run method to import certificates to mail client
        '''
        cemaim = CeMaIm(str(self.imp_ca_path.text()), str(self.imp_folder_path.text()), str(self.imp_user_cert_path[0]), self.config_map['imp_mail'], self.imp_password.text())
        status_code, message = cemaim.run()
        if status_code != 0:
                self.message = message
                self.errorMessage(message)
                return
        self.message = ""
        self.status_code = 0

    def __p12_form__(self):
        '''
        Init method for create pkcs12 certificate
        Initialize buttons and LineEdits
        '''
        self.p12_user_cert = self.window.findChild(QtWidgets.QPushButton, 'p12_user_cert')
        self.p12_user_key = self.window.findChild(QtWidgets.QPushButton, 'p12_user_key')
        self.p12_key_password = self.window.findChild(QtWidgets.QLineEdit, 'p12_key_password')
        self.p12_p12_password = self.window.findChild(QtWidgets.QLineEdit, 'p12_p12_password')
        self.p12_p12_password_confirm = self.window.findChild(QtWidgets.QLineEdit, 'p12_p12_password_confirm')

        self.p12_key_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.p12_p12_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.p12_p12_password_confirm.setEchoMode(QtWidgets.QLineEdit.Password)

        self.p12_user_cert.clicked.connect(lambda:self.get_file(self.p12_user_cert, self.p12_user_cert_path, "Pem files (*.pem);;All files (*.*)"))
        self.p12_user_key.clicked.connect(lambda:self.get_file(self.p12_user_key, self.p12_user_key_path, "Pem files (*.pem);;All files (*.*)"))

        self.p12_OK = self.window.findChild(QtWidgets.QPushButton, 'p12_OK')
        self.p12_OK.clicked.connect(lambda:self.preprocess_create_p12())

    def preprocess_create_p12(self):
        '''
        Run method to create pkcs12 certificate
        '''
        if if_file_exists(self.p12_user_cert_path[0]) == False:
            self.errorMessage(f'Personal certificate does not exist. There is nothing on this place:\n{self.p12_user_cert_path[0]}\n')
            return
        if if_file_exists(self.p12_user_key_path[0]) == False:
            self.errorMessage(f'Private key certificate does not exist. There is nothing on this place:\n{self.p12_user_key_path[0]}\n')
            return
        if if_file_is_cert(self.p12_user_cert_path[0]) == False:
            self.errorMessage(f'Personal certificate is not certificate. Choose another file')
            return
        if check_password_match_to_key(self.p12_user_key_path[0], self.p12_key_password.text()) == False:
            self.errorMessage("Password is incorrect for this private key certificate. Try another password or maybe you choosed bad private key certificate. Choosed file do not have to be private key.")
            return
        if check_cert_match_key(self.p12_user_cert_path[0], self.p12_user_key_path[0], self.p12_key_password.text()) == False:
            self.errorMessage("Personal certificate and private key certificate does not match. Choose different files.")
            return
        if self.p12_p12_password.text() != self.p12_p12_password_confirm.text():
            self.errorMessage("Password and confirm password do not match.")
            return
        if self.p12_p12_password.text() == "" :
            self.errorMessage("Password is empty. Type some password.")
            return

        output_folder = Path(self.p12_user_cert_path[0]).parent
#        print(self.p12_user_cert_path[0], self.p12_user_key_path[0], output_folder, self.p12_key_password.text(), self.p12_p12_password.text())
        create_pkcs12(self.p12_user_cert_path[0], self.p12_user_key_path[0], output_folder, self.p12_key_password.text(), self.p12_p12_password.text())

        self.message = ""
        self.status_code = 0

    @QtCore.pyqtSlot(str)
    def mail_changed(self, client_name):
        '''
        Change mail shortcut when mail client is changed
        '''
        self.config_map['imp_mail'] = get_mail_client_shortcut(client_name)

    def run(self):
        '''
        Run method for create and exit Gui
        '''
        self.window.show()
        return self.app.exec()

def run_gui():
    gui = Gui()
    gui.run()
