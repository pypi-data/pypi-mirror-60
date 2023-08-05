import os, sys


PEP582 = True

def load_pypackages():

    if os.path.exists('__pypackages__'):
        lib = '__pypackages__/{}.{}/lib'.format(sys.version_info.major, sys.version_info.minor)
        if not os.path.exists(lib):
            os.makedirs(lib)
        sys.path.insert(0, lib)
        if 'pip' in sys.argv or sys.argv[0].endswith('pip'):
            if 'install' in sys.argv and ('-t' not in sys.argv and '--target' not in sys.argv):
                sys.argv.extend(['-t', lib])

