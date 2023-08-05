import os
import sys
import re
import requests
import tempfile
from bs4 import BeautifulSoup
from os import listdir
from os.path import isfile, join
from .utils import *

## Import mail client file here
from .thb_certdb import Thunderbird, MailClient

# Place to add another email client communicator
mail_clients = {
    'thb': Thunderbird,
#    'mail': MailClient,
}

def cli_mail_client_text():
    '''
    Get text and list of mail clients
    This option is used by click
    '''

    mail_client_list = []
    output = "["
    for i in mail_clients.items():
        line = f'{i[0]} - ({i[1].mail_client_name})'
        output = output + line + ", "
        mail_client_list.append(line)
    output = re.sub(', $', '', output)
    output = output + "]"
    return output, mail_client_list

def get_mail_client_shortcut(client_name):
    '''
    Get shortcuts of clients names
    '''
    for (key, value) in mail_clients.items():
        if value.mail_client_name == client_name:
           return key

def get_mail_client_names():
    '''
    Return list of client names
    '''
    mail_client_names = []
    for i in mail_clients.items():
        mail_client_names.append(i[1].mail_client_name)
    return mail_client_names

class CeMaIm:
    '''
    Class for importing certificates to mail client.
    '''
    def __init__(self, auth_cert, path, user_cert, mail, password, debug = False, ca_location = False, certs_location = False):
        ca = re.sub('[ ]*$', '', auth_cert)
        ca = re.sub('^[ ]*', '', ca)

        p12 = re.sub('[ ]*$', '', user_cert)
        p12 = re.sub('^[ ]*', '', p12)
        self.auth_cert = ca
        self.path = path
        self.user_cert = p12
        self.mail = mail
        self.password = password
        self.ca_location = ca_location
        self.certs_location = certs_location
        self.debug = debug
        self.communicator = self.__get_communicator__()

    def __get_communicator__(self):
        '''
        Set up what mail client communicator will be used
        '''
        return mail_clients[self.mail](self.debug)

    def recognize_web(self, path):
        '''
        Recognize where the file is located if its on web or at local disk
        '''
        if re.match('^https?://.*', path):
#            print("Web")
            return True
        else:
#            print("Local")
            return False

    def listFD(self, url, ext='pem'):
        '''
            Get list of files at specified http site
        '''
        try:
            page = requests.get(url)
        except:
            return 30, f'Something goes wrong when downloading from "{self.path}".\nTry files download manual and set their path at disk.', []
        if page.status_code < 200 or page.status_code > 300:
            return 30, f'Something goes wrong when downloading from "{self.path}".\nTry files download manual and set their path at disk.', []
#        print(page)
        soup = BeautifulSoup(page.text, 'html.parser')
        return 0, '', [url + node.get('href') for node in soup.find_all('a') if node.get('href').endswith(ext)]


    def get_and_import_CA(self):
        '''
        Download and test file of certificate authority.

        If it goes through test it will be imported by mail client
        '''
        ca_file = ""

        fp = tempfile.NamedTemporaryFile()
#        print(fp.name)
        #Recognize if it is web or local
        if self.recognize_web(self.auth_cert) == True:
            #Download from web
            try:
                myfile = requests.get(self.auth_cert)
            except:
                return 20, f'Something goes wrong when downloading from "{self.auth_cert}".\nTry it again or download it manual and set its path at disk.'
            if myfile.status_code < 200 or myfile.status_code > 300:
                return 20, f'Something goes wrong when downloading from "{self.auth_cert}".\nTry it again or download it manual and set its path at disk.'
            ca_file = myfile.content.decode()
            fp.write(myfile.content)
#            fp.seek(0)
#            print(fp.read())
            ca_file = fp.name
#            print(myfile.content.decode())
        else:
            ca_file = self.auth_cert
#            with open(self.auth_cert) as f:
#                ca_file = f.read()

        # Import CA
#        self.communicator.import_ca("/mnt/Data/School/Master/PYT/certs-mail-import/CA/mipytCA/cacert.pem" , "tester")
        if if_file_exists(ca_file) == False:
            return 21, f'File \'{ca_file}\' you are trying import does not exist. Select another file.'
        if if_file_is_cert(ca_file) == False:
            return 22, f'File \'{ca_file}\' you are trying import is not certicate file at pem format. Select another file.'
        self.communicator.import_ca(ca_file, str(Path(self.auth_cert).name))
#        self.communicator.import_ca(ca_file, str(Path(self.auth_cert).name)self.auth_cert.split('/')[-1])
        fp.close()
        return 0, ''

    def get_and_import_pem(self):
        '''
        Download all from web or read all from specified path and imported by mail client
        Every file is test if exists and if its pem file.
        '''
        users_certs_list = []
        if self.recognize_web(self.path) == True:
            # Get list of users from web
            status_code, message, list_of_files = self.listFD(self.path, 'pem')
            if status_code != 0:
                return status_code, message
            for pem in list_of_files:
                fp = tempfile.NamedTemporaryFile()
                try:
                    myfile = requests.get(pem)
                except:
                    debug_message(self.debug, f'Something goes wrong when downloading from "{self.auth_cert}".\nTry it again or download it manual and set its path at disk.')
                    continue
                if myfile.status_code < 200 or myfile.status_code > 300:
                    debug_message(self.debug, f'Something goes wrong when downloading from "{self.auth_cert}".\nTry it again or download it manual and set its path at disk.')
                    continue

                fp.write(myfile.content)

                if if_file_exists(fp.name) == False:
                    debug_message(self.debug, f'File \'{ca_file}\' you are trying import does not exist. Will not be imported.')
                    fp.close()
                    continue
                if if_file_is_cert(fp.name) == False:
                    debug_message(self.debug, f'File \'{ca_file}\' you are trying import is not certicate file at pem format. Will not be imported.')
                    fp.close()
                    continue

                self.communicator.import_pem(fp.name, pem.split('/')[-1])
                fp.close()
        else:
            if os.path.exists(self.path) == False:
                return 31, f'Path to this folder {self.path} does not exist. Choose another one.'

            users_certs_list = [f for f in listdir(self.path) if f.endswith('.pem')]
            file_path = Path(self.path)
            for pem in users_certs_list:
                file_path_with_cert = file_path / pem
                if if_file_exists(str(file_path_with_cert)) == False:
                    debug_message(self.debug, f'File \'{str(file_path_with_cert)}\' you are trying import does not exist. Will not be imported.')
                    continue
                if if_file_is_cert(str(file_path_with_cert)) == False:
                    debug_message(self.debug, f'File \'{str(file_path_with_cert)}\' you are trying import is not certicate file at pem format. Will not be imported.')
                    continue

                self.communicator.import_pem(str(file_path_with_cert), str(file_path_with_cert.name))
        return 0, ''

    def import_personal_cert(self):
        '''
        Import personal cert at pkcs12 format
        '''
        self.communicator.import_personal_cert(self.user_cert, self.password)

    def check_p12_file(self):
        '''
        Check if pkcs12 file is OK and password match to cert
        '''
        if if_file_exists(self.user_cert) == False:
            return 10, f'Personal certificate does not exist. There is nothing on this place:\n{self.user_cert}\n'
        try:
            p12 = crypto.load_pkcs12(open(self.user_cert, 'rb').read(), self.password)
        except:
            return 11, f'Password is incorrect for this p12 certificate "{Path(self.user_cert).name}". Try another password or maybe you choosed bad private key certificate. Choosed file do not have to be private key.'
        return 0, ''

    def run(self):
        '''
        Main method that run importing of CA, pkcs12 and pems file
        '''
        if self.debug == True:
            print(f'Running with configuration:\n\tCA: {self.auth_cert}\n\tMail client: {self.mail}\n\tUser certificate: {self.user_cert}\n\tPassword: {self.password}\n\tPath: {self.path}\n')
        # Test if mail client is OK
        if self.communicator.lock != 0:
            return self.communicator.lock, self.communicator.lock_message


        ## Get and import CA
        if self.auth_cert != "":
            status_code, message = self.get_and_import_CA()
            if status_code != 0:
                return status_code, f'{message}\n If you want to skip import CA set path to certificate authority empty.'


        if self.user_cert != "" and self.user_cert != ".":
            status_code, message = self.check_p12_file()
            if status_code != 0:
                return status_code, message
            self.import_personal_cert()

        ## Get and import Certs
        if self.path == "":
            return 40, f'There is no path to folder of certificates. Nothing will be imported.'
        status_code, message = self.get_and_import_pem()
        if status_code != 0:
            return status_code, message
        return 0, ''
