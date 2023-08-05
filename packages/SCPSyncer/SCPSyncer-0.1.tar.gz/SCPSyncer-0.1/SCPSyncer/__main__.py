#!/usr/bin/env python3
import argparse
import logging
import colorama
from SCPSyncer import SCPSync

colorama.init()

loghandler = logging.StreamHandler()
loghandler.addFilter(lambda record: record.name.startswith('SCPSync'))
logging.basicConfig(format='', level=logging.INFO, handlers=[loghandler])

###
# Parse command line arguments
parser = argparse.ArgumentParser(prog='scp_sync', description='Synchronise project directory over SCP')
parser.add_argument('-m', '--host', help='The target host machine ip/name')
parser.add_argument('--port', help='The target host port', type=int)
parser.add_argument('-u', '--user', help='The user on the target host')
parser.add_argument('-p', '--password', help='The user password on the target host')
parser.add_argument('-c', '--config_name', help='The name of the predefined configuration to use')
parser.add_argument('path', help='Path to the folder to sync', nargs='?', default='./')
args = parser.parse_args()

try:
    syncer = SCPSync(args.path, host=args.host, port=args.port, user=args.user, password=args.password, config_name=args.config_name)
except SCPSync.ConfigError as e:
    if str(e).split(' ')[0] == 'host':
        args.host = input('Enter IP of target machine: ')
    else:
        raise
    syncer = SCPSync(args.path, host=args.host, port=args.port, user=args.user, password=args.password, config_name=args.config_name)

syncer.sync()
