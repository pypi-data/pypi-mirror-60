import os
import click

@click.command()
@click.option('-f', '--file', default=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Makefile'), help='Path to Makefile (defaults to bundled Makefile)')
@click.argument('target', default='help')
@click.argument('args', nargs=-1)
def main(file, target, args):
    """
    Super fancy wrapper for our Terraform Makefile ;)
    """
    if not os.path.isfile(file):
        click.echo(f'Your {file} not found :(')
        os.sys.exit(1)

    _args = list(args)

    if len(_args) > 0:
        os.system(f"make -f {file} {target} {' '.join(_args)}")
    else:
        os.system(f"make -f {file} {target}")
    

if __name__ == '__main__':
    main()