from OpenSSL import crypto
from OpenSSL.crypto import (load_privatekey, load_certificate, dump_privatekey, dump_certificate, dump_certificate_request, X509, X509Name, PKey, load_pkcs12)
from OpenSSL.crypto import (TYPE_DSA, TYPE_RSA, FILETYPE_PEM, FILETYPE_ASN1 )
from Crypto.Util import asn1

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives import serialization

from pathlib import Path
import re
import hashlib

def debug_message(debug, message):
    '''
    Print debug message
    '''
    if debug == True:
        print(message)

def encrypt_string(hash_string):
    sha_signature = hashlib.sha256(hash_string.encode()).hexdigest()
    return sha_signature

def check_password_match_to_key(key_file, key_password):
    '''
    Check if password math to key and if key_file is a private key certificate
    '''
    try:
        with open(key_file, "r") as my_key_file:
            my_key_text = my_key_file.read()
            key = load_privatekey(FILETYPE_PEM, my_key_text, key_password.encode())
    except:
        return False
    return True

# source code: https://www.v13.gr/blog/?p=325
def check_cert_match_key(cert_file, key_file, key_password):
    with open(cert_file, "r") as my_cert_file:
        my_cert_text = my_cert_file.read()
        cert = load_certificate(FILETYPE_PEM, my_cert_text)
    # Read private key
    with open(key_file, "r") as my_key_file:
        my_key_text = my_key_file.read()
        priv = load_privatekey(FILETYPE_PEM, my_key_text, key_password.encode())

    pub=cert.get_pubkey()

    # Only works for RSA (I think)
    if pub.type()!=TYPE_RSA or priv.type()!=TYPE_RSA:
        raise Exception('Can only handle RSA keys')

    # This seems to work with public as well
    pub_asn1=dump_privatekey(FILETYPE_ASN1, pub)
    priv_asn1=dump_privatekey(FILETYPE_ASN1, priv)

    # Decode DER
    pub_der=asn1.DerSequence()
    pub_der.decode(pub_asn1)
    priv_der=asn1.DerSequence()
    priv_der.decode(priv_asn1)

    # Get the modulus
    pub_modulus=pub_der[1]
    priv_modulus=priv_der[1]

    if pub_modulus==priv_modulus:
        return True
    else:
        return False

def if_file_exists(file_path):
    '''
    Check if file exist
    '''
    if Path(file_path).is_file():
        return True
    else:
        return False

def if_file_is_cert(file_path):
    '''
    Check if file is pem file (certificate)
    '''
    try:
        with open(file_path, "r") as my_cert_file:
            my_cert_text = my_cert_file.read()
            cert = load_certificate(FILETYPE_PEM, my_cert_text)
    except:
        return False
    return True

def create_key_and_request(name, surname, password, cert_subject, store_location):
    '''
    Method that will create users key and request for certificate.

    It excpect that all input is valit and as input expect:
        - name (string)
        - surname (string)
        - password (string)
        - created subject for certificate (map)
        - path to location where key and certificate will be created (string)
    '''

    # Create private key
    private_key = crypto.PKey()
    private_key.generate_key( TYPE_RSA, 4096)

    # Load private key to cryptography library
    key = load_pem_private_key(crypto.dump_privatekey(crypto.FILETYPE_PEM, private_key),
                                password=None, backend=default_backend())
    # Create key with password
    password_protected_key = key.private_bytes(encoding=serialization.Encoding.PEM,
                                        format=serialization.PrivateFormat.TraditionalOpenSSL,
                                        encryption_algorithm=serialization.BestAvailableEncryption(password.encode()))

    ## Create reuest and set subject items by cert_subject map
    csrrequest = crypto.X509Req()
    csrrequest.get_subject().CN = f'{name} {surname}'
    for (key, value) in cert_subject.items():
        setattr(csrrequest.get_subject(), key, value)
    csrrequest.set_pubkey(private_key)
    csrrequest.sign(private_key, "sha256")

    # Prepare name and path for output files
    store_location = Path(store_location)
    file_name = f'{name[0:1].lower()}{surname.split(" ")[-1].lower()}'
    key_path = store_location / f'{file_name}-key.pem'
    req_path = store_location / f'{file_name}-req.pem'
    ## Export generated key
    open(key_path, 'wb').write(password_protected_key)
    ## Export certificate request
    open(req_path, 'wb').write(crypto.dump_certificate_request(crypto.FILETYPE_PEM, csrrequest))

def create_pkcs12_cert_name(cert_file):
    file_path = Path(cert_file)
#    file_name = re.sub(file_path.suffix, '.p12', file_path.name)
    return f'{file_path.stem}.p12'

def create_pkcs12(cert_file, key_file, output_folder, key_password, p12_password):
    '''
    Method that will create users p12 certificate from user's key and certificate.

    It excpect that all input is valit and as input expect in following order:
        - path to certificate public key (string)
        - path to certificate private key(string)
        - path where p12 certificated will be created (string)
        - password for certificate private key (string)
        - password for p12 certificate (string)
    '''

    # Read certificate
    with open(cert_file, "r") as my_cert_file:
        my_cert_text = my_cert_file.read()
        cert = load_certificate(FILETYPE_PEM, my_cert_text)
    # Read private key
    with open(key_file, "r") as my_key_file:
        my_key_text = my_key_file.read()
        key = load_privatekey(FILETYPE_PEM, my_key_text, key_password.encode())

    p12 = crypto.PKCS12()
    p12.set_privatekey( key )
    p12.set_certificate( cert )

    output_file = Path(output_folder) / f'{Path(cert_file).stem}.p12'
    open(output_file, 'wb' ).write( p12.export(p12_password.encode()) )

