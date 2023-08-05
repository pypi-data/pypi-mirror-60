import click
from random import choice


def validate_argument(ctx, param, value):
    try:
        if len(value) < 2:
            raise ValueError

        return value
    except ValueError:
        raise click.BadParameter(
            'Not enough args to pick from', param_hint='args')
    except Exception as e:
        raise click.ClickException(e)


@click.command(options_metavar='[options]')
@click.argument('args', nargs=-1, callback=validate_argument, metavar='args')
def cli(args):
    """randomly pick out one choice from argument lists.\n
    argument  -\n 
    \t* series of space seperated integers."""

    # randomly pick one from args list
    click.echo(choice(args))
