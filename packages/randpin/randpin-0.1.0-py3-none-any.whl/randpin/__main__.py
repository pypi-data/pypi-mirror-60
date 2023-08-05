import os
import pathlib
import random
import subprocess
import sys

import click
import pinboard


def get_config_path():
    HOME = pathlib.Path(os.path.expandvars("$HOME"))
    configdir = os.environ.get('XDG_CONFIG_HOME')
    if not configdir:
        configdir = HOME / '.config'

    configpath = pathlib.Path(configdir) / 'randpin_apikey.txt'

    return configpath


@click.command()
@click.option('--save/--no-save', default=False)
@click.argument('apikey', nargs=-1)
@click.pass_context
def cli(ctx, save, apikey):

    if apikey:
        apikey = apikey[0]
    else:
        apikey = None

    if apikey is None:
        apikey = os.environ.get('RANDPIN_APIKEY')

    if apikey is None:

        configpath = get_config_path()

        if not configpath.exists():
            raise click.ClickException("Couldn't find the API key")

        with configpath.open('r') as f:
            apikey = f.read().strip()

    if save:
        with get_config_path().open('w') as f:
            print(apikey, file=f)

    pb = pinboard.Pinboard(apikey)

    unread = [b for b in pb.posts.all() if b.toread]
    random_unread = random.choice(unread)
    ret = subprocess.run(["xdg-open", random_unread.url],
                         check=False)

    ctx.exit(ret.returncode)


def main():
    cli()


if __name__ == '__main__':
    main()
