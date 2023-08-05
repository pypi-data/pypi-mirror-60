import configparser
import click
import getpass
from .cemaim import *
from .utils import create_pkcs12
from .cemaim_qt import Gui
from PyQt5 import QtWidgets, uic, QtCore, QtGui

def parse_cert_path(ctx, param, value):
    return value

def parse_auth_cert(ctx, param, value):
    return value

def validate_config(ctx, param, value):
    '''
    Validate if config File exist
    '''
    if value == None: return value
    try:
        config = configparser.ConfigParser()
        with open(value) as f:
            config.read_file(f)
    except Exception:
        raise click.BadParameter('config file can not be readed')
    return value

def parse_config_file(config_file):
    '''
    Read config file and fill variables to map
    '''
    config = configparser.ConfigParser()
    config.optionxform = str
    with open(config_file) as f:
        config.read_file(f)

    config_map = {}

    for i in config.sections():
        section = i[0:3]
        for key in config[i]:
            config_map[f'{section}_{key.lower()}'] = config[i][key]

    return config_map

def force_parameters_over_config_file(config_map, folder, ca, mail, user_cert, password):
    '''
    Overwrite variables from config file with parametrs settings
    '''
    if ca!= None:
        config_map['imp_ca'] = ca

    if folder != None:
        config_map['imp_folder'] = folder

    if ('imp_mail' not in config_map.keys()) and (mail == None):
        config_map['imp_mail'] = "thb"
    if ('imp_mail' not in config_map.keys()) and (mail != None):
        config_map['imp_mail'] = mail
    if ('imp_mail' in config_map.keys()):
        if config_map['imp_mail'] not in mail_clients.keys():
            print(f'There is no mail client called {config_map["imp_mail"]}. Client it set to default client \'thb\'')
            config_map['imp_mail'] = "thb"

    if user_cert != None:
        config_map['imp_user_cert'] = user_cert

    config_map['password'] = password



@click.command('cemaim')
@click.option('-F', '--folder', callback=parse_cert_path,
        help='Path to location where personal certificates are stored.')
@click.option('-C', '--ca', callback=parse_auth_cert,
        help='Specification of certification authority that will be imported to mail client.')
@click.option('-c', '--cli', is_flag=True,
        help='Do not open window and it will be runned from terminal. This option is not config file option.')
@click.option('-d', '--debug', is_flag=True,
        help='Debug mode is compatible only with \'--cli\' option. This option is not config file option.')
@click.option('-f', '--config-file', metavar='FILENAME', type=click.Path(), callback=validate_config,
        help='Read configuration from config file.')
@click.option('-m', '--mail', metavar=cli_mail_client_text()[0],
type=click.Choice(mail_clients.keys()),
        help='Choose mail client where will be certificates imported. By default will be choosed Thunderbird')
@click.option('-p', '--password', is_flag=True,
        help='Write password for user certificate.')
@click.option('-u', '--user-cert', metavar='FILENAME', type=click.Path(),
        help='Specification of user\'s certificate.')
def cli(folder, ca, cli, debug, config_file, mail, password, user_cert):
    """
    Program for import users certificates to mail client

    It also run Gui with parameters from command line
    """

    config_map = {}
    config_map['imp_ca'] = ""
    config_map['imp_folder'] = ""
    config_map['imp_user_cert'] = ""
    password_string=""
    if password == True:
        try:
            password_string = getpass.getpass()
        except Exception as error:
            print('ERROR', error)


    if config_file != None:
        config_map = parse_config_file(config_file)

    force_parameters_over_config_file(config_map, folder, ca, mail, user_cert, password_string)

    if cli == True:
        ## Import certificate from command line
        cemaim = CeMaIm(config_map['imp_ca'], config_map['imp_folder'], config_map['imp_user_cert'], config_map['imp_mail'], password_string, debug)
        status_code, message = cemaim.run()
        if status_code != 0:
           print(message, file=sys.stderr)
           sys.exit(status_code)

    else:
        ## Run Gui
        gui = Gui(config_map)
        gui.run()


def main():
    cli()
