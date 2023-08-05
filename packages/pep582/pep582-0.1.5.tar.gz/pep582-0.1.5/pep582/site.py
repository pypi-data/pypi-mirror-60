import os, sys


pypackages_path = os.path.join(os.path.abspath(getattr(sys.modules['__main__'], '__file__', '.')), '__pypackages__')


def load_pypackagesa():

    if os.path.exists(pypackages_path):
        lib = os.path.join(pypackages_path, '{}.{}/lib'.format(sys.version_info.major, sys.version_info.minor))
        if not os.path.exists(lib):
            os.makedirs(lib)
            os.makedirs('{}/bin'.format(lib))
            bin = os.path.abspath(os.path.join(pypackages_path, 'bin'))
            if os.path.islink(bin):
                os.unlink(os.path.abspath(os.path.join(pypackages_path, 'bin')))
            os.symlink(os.path.abspath(os.path.join(lib, 'bin')), os.path.abspath(os.path.join(pypackages_path, 'bin')))
        sys.path.insert(0, lib)
        if 'pip' in sys.argv or sys.argv[0].endswith('pip'):
            if 'install' in sys.argv and ('-t' not in sys.argv and '--target' not in sys.argv):
                sys.argv.extend(['-t', lib])
