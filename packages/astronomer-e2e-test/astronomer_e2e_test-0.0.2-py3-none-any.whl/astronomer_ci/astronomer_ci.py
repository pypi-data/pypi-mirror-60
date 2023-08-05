import os
import sys
import logging

import click
from astronomer_ci.dockerhub import get_next_tag


def _configure_logging():
    if os.environ.get("DEBUG"):
        level = logging.DEBUG
    else:
        level = logging.INFO
    logging.basicConfig(stream=sys.stderr, level=level)


@click.command()
@click.option('--branch',
              required=True,
              help='The name of the release branch (e.g. "release-0.1")')
@click.option('--repository',
              required=True,
              help='The name of the DockerHub repository (e.g. "astronomerinc"'
              )
@click.option(
    '--image',
    required=True,
    help='The image to find the next version for (e.g. "ap-houston-api")')
def get_next_version(branch, repository, image):
    _configure_logging()
    print(get_next_tag(branch, repository, image))


def main():
    get_next_version()


if __name__ == "__main__":
    main()
