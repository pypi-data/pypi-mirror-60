import argparse

def get_arg_parser():
    parser = argparse.ArgumentParser(prog='macgen', description='MAC Address Generation Utility')

    parser.add_argument('-u', '--unicast',              dest='is_multicast', action='store_false', default=False, help='produce a unicast address (default)')
    parser.add_argument('-m', '--multicast',            dest='is_multicast', action='store_true',                 help='produce a multicast address')

    parser.add_argument('-g', '--global',               dest='is_local',     action='store_false',                help='produce a globally unique address / OUI enforced')
    parser.add_argument('-l', '--local',                dest='is_local',     action='store_true',  default=True,  help='produce a locally administered address (default)')

    parser.add_argument('-s', '--separator', type=str,  dest='separator',    action='store',       default=':',   help='use the given octet separator (default: ":")')
    parser.add_argument('-S', '--no-separator',         dest='no_separator', action='store_true',                 help='do not use a separator')

    return parser

def get_args():
    parser = get_arg_parser()
    return parser.parse_args()
