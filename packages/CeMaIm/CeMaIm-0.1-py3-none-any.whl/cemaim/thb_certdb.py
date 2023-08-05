import os
import sys
import re
import fnmatch
import subprocess, shlex
from pathlib import Path
from shutil import which
from .utils import debug_message

from OpenSSL import crypto
from OpenSSL.crypto import (load_certificate, dump_privatekey, dump_certificate, X509, X509Name, PKey, load_pkcs12)
from OpenSSL.crypto import (TYPE_DSA, TYPE_RSA, FILETYPE_PEM, FILETYPE_ASN1 )
from Crypto.Util.asn1 import (DerSequence, DerObject)

class MailClient:
    '''
    API for importing to email client
    '''
    mail_client_name = "Test mail client"
    lock = 0
    lock_message = ""
    def __init__(self, debug = False):
        print("Init")

    def import_ca(self, cert_file_path, cert_name):
        print("Import CA")
    def import_personal_cert(self, cert_file_path, password):
        print("Import personal cert")
    def import_pem(self, cert_file_path, cert_name):
        print("Import pem")

class Thunderbird:
    '''
    Class for importing certificates to Thunderbird mail client
    '''
    mail_client_name = "Thunderbird"
    def __init__(self, debug = False):
        self.thunderbird_folder= ""
        self.names_of_imported_certs = []
        self.names_of_personal_imported_certs = []
        self.modulus_of_imported_certs = []
        self.modulus_of_personal_imported_certs = []
        self.debug = debug

        self.lock, self.lock_message = self.__test_system_requirements__()
        if self.lock != 0:
            return
        self.thunderbird_folder = ""
        self.__test_existence_of_thunderbird_folder()

    def __test_system_requirements__(self):
        ## Windows check
        if os.name == "nt":
            return 1, "Program is running under operation system Windows. Import under windows is not compatible"
        ## Installed certutil program
        if which('certutil') == None or which('pk12util') == None:
            return 2, "To import certificates to Thunderbird program needs another programs called 'certutil' and 'pk12util'. They should be at 'libnss3-tools' package."
        # Unlocked
        return 0, ""
    def __test_existence_of_thunderbird_folder(self):
        # Situation if are more than one thunderbird folder
        databases = self.find('cert9.db', str(Path('~/.thunderbird/')))
        if len(databases) == 1:
            self.thunderbird_folder = databases[0].rsplit('/', 1)[0]
        elif len(databases) > 1:
            self.thunderbird_folder = databases[0].rsplit('/', 1)[0]
            debug_message(self.debug, f'There are more than one thunderbird account folders.Import will be done to the folder \'{self.thunderbird_folder}\' which is alphabetically first in the order.')
        else:
            self.lock = 3
            self.lock_message = "There is no Thunderbird folder. Install and sign to thunderbrid email client."

    ## Method finds specified file/folder
    def find(self, pattern, path):
        full_path = os.path.expanduser(path)
        result = []
        for root, dirs, files in os.walk(full_path):
            for name in files:
                if fnmatch.fnmatch(name, pattern):
                    result.append(os.path.join(root, name))
        return result

    ## Parse table from certutil command
    def process_cert_table(self, table):
        line = ''
        for i in table:
            if i == '\n':
                if line != '':
                    line = re.sub(' +', ' ', line)
                    find_flag = False
                    if len(re.findall('u,u,u$', line)) != 0:
                        find_flag = True
                    line = re.sub(' [ pPcCTuW]*,[ pPcCTuW]*,[ pPcCTuW]*$', '', line)
                    self.names_of_imported_certs.append(line)
                    if find_flag == True:
                        self.names_of_personal_imported_certs.append(line)
                line = ''
                continue
            else:
                line += i
        # Remove first and second line - header of table
        self.names_of_imported_certs.pop(0)
        self.names_of_imported_certs.pop(0)

    ## Parse modulus and exponent from certificate
    def process_modulus(self, cert):
        if not re.search('Modulus', cert) or not re.search('Exponent', cert):
            return -1, -1
        modulus = ""
        modulus = re.sub(' +', ' ', cert)
        modulus = re.sub('\n', '', modulus)
        modulus = re.sub('.*Modulus:', '', modulus)
        modulus = re.sub('Exponent:.*', '', modulus)
        modulus = re.sub(' +', '', modulus)
        modulus = re.sub(':', '', modulus)

        exponent = ""
        exponent= re.sub(' +', ' ', cert)
        exponent= re.sub('\n', '', exponent)
        exponent= re.sub('.*Exponent:', '', exponent)
        exponent= re.sub('\(.*', '', exponent)
        exponent= re.sub(' ', '', exponent)

        return modulus, exponent

    ## Source code: http://www.zedwood.com/article/python-openssl-x509-parse-certificate
    def format_split_bytes(self, aa):
        bb = aa[1:] if len(aa)%2==1 else aa #force even num bytes, remove leading 0 if necessary
        return bb

    def format_split_int(self, serial_number):
        aa = "0%x" % serial_number #add leading 0
        return self.format_split_bytes(aa)
#        return aa

    def get_modulus_and_exponent(self, x509):
        if x509.get_pubkey().type()==TYPE_RSA:
            pub_der = DerSequence()
            pub_der.decode(dump_privatekey(FILETYPE_ASN1, x509.get_pubkey()))
#            print(pub_der._seq[1])
#            modulus = "%s:%s" % ( self.format_split_int(pub_der._seq[0]), self.format_split_int(pub_der._seq[1]) )
            modulus = "%s" % ( self.format_split_int(pub_der._seq[1]) )
            exponent = pub_der._seq[2]
            return [ modulus, exponent ]
        return ''

    def get_email_address_from_cert(self, x509name, cert_path):
#        print(x509name.emailAddress)
        if x509name.emailAddress != "":
            return x509name.emailAddress
        elif x509name.CN != "":
            return x509name.CN
        else:
            return cert_path.split('/')[-1]

    ## Return specific format
    def get_org_cn_from_cert(self, x509name):
        return f'{x509name.CN} - {x509name.O}'

    def read_and_extract_cert(self, cert_file_path, ca_flag = False):
        ''' Get specific parts of certificate that are used for compare certificate is in database or not
        '''
        modulus = ""
        exponent = ""
        cert_nickname = ""

        with open(cert_file_path, 'rb+') as f:
            cert_pem = f.read()
            f.close()
            x509 = load_certificate(FILETYPE_PEM, cert_pem)
            keytype = x509.get_pubkey().type()
            keytype_list = {TYPE_RSA:'rsaEncryption', TYPE_DSA:'dsaEncryption', 408:'id-ecPublicKey'}
            key_type_str = keytype_list[keytype] if keytype in keytype_list else 'other'
            if x509.get_pubkey().type()==TYPE_RSA:
                modulus, exponent = self.get_modulus_and_exponent(x509)
#                print(modulus)

            if ca_flag == False:
                cert_nickname = self.get_email_address_from_cert(x509.get_subject(), cert_file_path)
            else:
                cert_nickname = self.get_org_cn_from_cert(x509.get_subject())
        return modulus, exponent, cert_nickname

    def cert_in_database(self, list_of_modules, modulus, exponent):
        '''
        Return if certificate is in database
        '''
        for i in list_of_modules:
            if (i[0] == modulus) and (int(i[1]) == int(exponent)):
                return True
        return False

    def get_list_of_imported_certs(self):
        '''
        Using shell command certutil for get information what certificates are at database
        '''
        if len(self.names_of_imported_certs) == 0:
#            certutil -L -d "$thunderbird_dir"
            process = subprocess.run(['certutil', '-d', 'sql:' + self.thunderbird_folder, '-L'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            # TODO process STDERR
            self.process_cert_table(process.stdout)

    def get_modules_of_imported_certs(self):
        '''
        Get modules of imported certificates. Modules and exponent are uniq part of each certificate.
        '''
        if len(self.modulus_of_imported_certs) == 0 or len(self.modulus_of_imported_certs) != len(self.names_of_imported_certs):
           for i in self.names_of_imported_certs:
                process = subprocess.run(['certutil', '-d', 'sql:' + self.thunderbird_folder, '-L', '-n', i], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
#                print(process.stdout)
#                print(process.returncode)
                if process.returncode == 0:
                    modulus, exponent = self.process_modulus(process.stdout)
                    if modulus != -1 and exponent != -1:
                        self.modulus_of_imported_certs.append((modulus, exponent))
                else:
                    continue

    def import_ca(self, cert_file_path, cert_name):
        '''
        Import CA to Thunderbird database.
        '''
        self.get_list_of_imported_certs()
        self.get_modules_of_imported_certs()

        modulus, exponent, cert_nickname = self.read_and_extract_cert(cert_file_path, True)
        if self.cert_in_database(self.modulus_of_imported_certs, modulus, exponent) != True:
            debug_message(self.debug, f"CA '{cert_name}' will be imported")
            #certutil -A -n $people_email -t ',,'  -d $thunderbird_dir -i $cert
            flags= "CT,C,C"
            process = subprocess.run(['certutil', '-d', 'sql:' + self.thunderbird_folder, '-A', '-i', cert_file_path, '-t', flags, '-n', cert_nickname], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        else:
            debug_message(self.debug, f"CA '{cert_name}' is in the database")

    def import_personal_cert(self, cert_file_path, password):
        '''
        Import user's personal certificate to database. File is at pkcs12 format.
        '''
        self.get_list_of_imported_certs()

        if len(self.modulus_of_personal_imported_certs) == 0 or len(self.modulus_of_personal_imported_certs) != len(self.names_of_personal_imported_certs):
            for i in self.names_of_personal_imported_certs:
                process = subprocess.run(['certutil', '-d', 'sql:' + self.thunderbird_folder, '-L', '-n', i], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                if process.returncode == 0:
                    modulus, exponent = self.process_modulus(process.stdout)
                    if modulus != -1 and exponent != -1:
                        self.modulus_of_personal_imported_certs.append((modulus, exponent))
                else:
                    continue

        try:
            p12 = crypto.load_pkcs12(open(cert_file_path, 'rb').read(), password)
        except:
            # Wrong password
            return 1

        p12_cert = p12.get_certificate()
        modulus, exponent = self.get_modulus_and_exponent(p12_cert)

        if self.cert_in_database(self.modulus_of_personal_imported_certs, modulus, exponent) != True:
            #pk12util -i CA/mipytCA/userCerts/test-cert.p12 -W <password>

            debug_message(self.debug, f"'{cert_file_path}' will be imported")
            process = subprocess.run(['pk12util', '-i', cert_file_path, '-W', password,'-d', 'sql:' + self.thunderbird_folder], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        else:
            debug_message(self.debug, f"'{cert_file_path}' is in the database")


    def import_pem(self, cert_file_path, cert_name):
        '''
        Import certificate i to people tab at thunderbid
        '''
        self.get_list_of_imported_certs()
        self.get_modules_of_imported_certs()

        modulus, exponent, cert_nickname = self.read_and_extract_cert(cert_file_path)

        if self.cert_in_database(self.modulus_of_imported_certs, modulus, exponent) != True:
            debug_message(self.debug, f"'{cert_name}' will be imported")
            #certutil -A -n $people_email -t ',,'  -d $thunderbird_dir -i $cert
            flags= ",,"
            process = subprocess.run(['certutil', '-d', 'sql:' + self.thunderbird_folder, '-A', '-i', cert_file_path, '-t', flags, '-n', cert_nickname], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        else:
            debug_message(self.debug, f"'{cert_name}' is in the database")

    def debug_delete_certs_from_path(self, cert_file_path):
        '''
        This is debugging method for easy remove from database
        '''
        cert_nickname = ""
        with open(cert_file_path, 'rb+') as f:
            cert_pem = f.read()
            f.close()
            x509 = load_certificate(FILETYPE_PEM, cert_pem)
            cert_nickname = self.get_email_address_from_cert(x509.get_subject(), cert_file_path)
        process = subprocess.run(['certutil', '-d', 'sql:' + self.thunderbird_folder, '-D', '-n', cert_nickname], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

#
