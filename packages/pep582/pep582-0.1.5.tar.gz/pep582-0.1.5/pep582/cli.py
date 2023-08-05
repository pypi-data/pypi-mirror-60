import click
import sys
from pep582 import patch


@click.group()
def main():
    pass


@click.command()
@click.option('--bin', default=False, help='create __pypackages__/bin and add to PATH')
def install(bin):
    patch.update_site_py(True, bin)
    patch.update_bash_rc(True, bin)


@click.command()
@click.option('--bin', default=False, help='create __pypackages__/bin and add to PATH')
def uninstall(bin):
    patch.update_site_py(False, bin)
    patch.update_bash_rc(False, bin)


@click.command()
def freeze():
    import pip, os, itertools
    from pip.__main__ import _main
    from pep582.site import pypackages_path
    sys.path = [pypackages_path, os.path.dirname(pip.__file__)] + [p for p in sys.path if '-packages' not in p]
    print(sys.path)
    _main()

main.add_command(install)
main.add_command(uninstall)
main.add_command(freeze)

if __name__ == '__main__':
    main()
