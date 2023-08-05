import click

try:
    from . import externip
except ImportError:
    import externip

@click.group()
def ipfinder():
    pass


ipfinder.add_command(externip.external_IP)
