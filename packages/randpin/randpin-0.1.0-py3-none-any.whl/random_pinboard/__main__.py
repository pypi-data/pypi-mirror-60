import os
import random
import subprocess
import sys

import pinboard


def get_api_key():
    """
    Retrieve the API key from wherever it may be found.

    Ideal search path is:
        1. config file
        2. environment variable
        3. command-line arg

    For now, only command-line arg is supported.
    """
    apikey = sys.argv[1]

    return apikey


def main():
    apikey = get_api_key()
    pb = pinboard.Pinboard(apikey)

    unread = [b for b in pb.posts.all() if b.toread]
    random_unread = random.choice(unread)
    ret = subprocess.run(["xdg-open", random_unread.url],
                         check=False)

    sys.exit(ret.returncode)


if __name__ == '__main__':
    main()
