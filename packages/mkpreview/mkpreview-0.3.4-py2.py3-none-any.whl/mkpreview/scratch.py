#!/opt/local/bin/python3
'''
Test Argparse with ENV variables
'''

import os
import argparse


def getenviron(prefix, **kwargs):
    '''
    Get a list of environment variables and return a list for ARG Parsing overrides



    '''
    return_list = list()
    key=""
    value=""

    # KWARGS is a translation table KEY=Envionment Variable, Value is return key
    # If set scan for this list, if not use a prefix. If prefix is set, variables are limited to the prefix
    for evar in os.environ:
        if prefix or evar in kwargs.keys():
            value = os.environ.get(evar)
            # Something we can work with
            if kwargs and not prefix:
                print('Kargs Only',evar)
                key=kwargs.get(evar,None)
                print(key,value)

            elif evar.startswith(prefix) and not kwargs:
                key="--" + evar.replace(prefix,'').replace('_','-').lower()

            elif evar.startswith(prefix) and kwargs:
                key = kwargs[evar.replace(prefix,'')]

            if key:
                return_list.append(key)
                if value != 'True' and value != 'False' and value != 'None':
                    return_list.append(value)

        else:
            # ENV var we don't need
            pass


    return return_list

def main():

    env_vars = getenviron(None,FOO='--foo')

    parser = argparse.ArgumentParser()
    parser.prog = 'MyName'
    parser.description = "This program will create a video preview file of a given video"
    parser.epilog = """The filename of the output will be the part_id-md5-originalBaseName.png.
    If the part_id and md5 are unset the filename will be the original base name.png
    """

    parser.add_argument(
            '--version',
            action='version',
            version='1.0.1')

    parser.add_argument(
            '-c', '--tile-cols',
            help='Number of columns for a preview',
            action='store',
            type=int,
            required=False,
            dest='tile_cols',
            default='5'
            )

    parser.add_argument(
            '-r', '--tile-rows',
            help='Number of rows for a preview',
            action='store',
            type=int,
            required=False,
            dest='tile_rows',
            default='5'
        )

    parser.add_argument('--foo', action='store_true')

    if len(env_vars)==0: env_vars=None
    print('Env {}'.format(env_vars))
    parse_out = parser.parse_args(env_vars)

    print('Parsed out {}'.format(parse_out))
    return
if __name__ == "__main__":

    main()