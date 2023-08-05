import site, os, sys

if not hasattr(site, 'pep582'):
    try:
        with open(site.__file__, 'a') as f:
            f.write("from pep582 import site")
        print('{} succesfully patched'.format(site.__file__))
        print('try creating __pypackages__ in some directory')
        print('pip install inside that directory would install into __pypackages__ by default')
        print('good luck!')
    except PermissionError:
        os.execvp(sys.executable, ['sudo']+sys.argv)
else:
    print('{} already patched'.format(site.__file__))

