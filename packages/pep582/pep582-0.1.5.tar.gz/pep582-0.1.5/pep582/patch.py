import site, os, sys, argparse

CODE = """try:
    from pep582.site import load_pypackages
    load_pypackages()
except ImportError:
    pass # uninstalled maybe
"""

BASH_BIN = '''
export PATH="./__pypackages__/bin/:$PATH"
'''


def update_bash_rc(install=True, bin=False):
    if not install:
        bin = False
    for path in filter(os.path.exists, map(os.path.expanduser, ['~/.zshrc', '~/.bashrc', '~/.profile', '~/.bash_profile'])):
        with open(path) as f:
            content = f.read()
        if bin:
            if BASH_BIN in content:
                continue
            else:
                with open(path+'_', 'w') as f:
                    f.write(content+BASH_BIN)
        else:
            if BASH_BIN not in content:
                continue
            else:
                with open(path+'_', 'w') as f:
                    f.write(content.replace(BASH_BIN.strip(), ''))


def update_site_py(install=True, bin=False):
    try:
        if install:
            if not hasattr(site, 'pep582'):
                with open(site.__file__, 'a') as f:
                    f.write(CODE)
                print('{} succesfully patched'.format(site.__file__))
                print('pip install would install into __pypackages__ by default')
                print('good luck!')
            else:
                print('{} already patched'.format(site.__file__))
        else:
            if hasattr(site, 'pep582'):
                with open(site.__file__, 'r') as f:
                    site_content = f.read()
                with open(site.__file__+'_', 'w') as f:
                    f.write(site_content.replace(CODE, ''))
                os.rename(site.__file__+'_', site.__file__)
                print('{} succesfully patched'.format(site.__file__))
                print('pep582 removed')
            else:
                print('pep582 not found in {} '.format(site.__file__))

    except PermissionError:
        os.execvp(sys.executable, ['sudo'] + sys.argv)


