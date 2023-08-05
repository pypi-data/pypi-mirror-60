#!/usr/bin/env python3

import json
from contextlib import contextmanager
from datetime import datetime
from os import environ

import click

from ..main import run as run_smugapi


@click.group()
def cli():
    pass


@cli.command(help="display version and exit")
def version():
    from .. import version
    print("smugapi {}".format(version))


@cli.command(help="start http server")
@click.option('-b', '--bind', 'addr', envvar='SMUGAPI_BIND',
        default='localhost', help="bind to what addr (localhost)")
@click.option('-p', '--port', 'port', envvar='SMUGAPI_PORT',
        default=8088,
        help="port for service to bind (8088)")
@click.option('-u', '--prefix', 'prefix', envvar='SMUGAPI_PREFIX',
        default='', help="prefix all url routes with ...")
@click.option('-d', '--debug', 'debug', envvar='SMUGAPI_DEBUG',
        is_flag=True, help="enable debug mode")
@click.option('-w', '--weatherbit', 'weatherbit_key',
        envvar='SMUGAPI_WEATHERBIT', default='', help="weatherbit api key")
@click.option('-t', '--worldtradingdata', 'worldtradingdata_key',
        envvar='SMUGAPI_WORLDTRADINGDATA',
        default='', help="worldtradingdata api key")
@click.option('-c', '--chartmoji', 'enable_chartmoji',
        envvar='SMUGAPI_CHARTMOJI', default=False, is_flag=True,
        help="enable chartmoji in outputs")
def run(**ka):
    print("running smugapi on port:{}{}".format(
        ka['port'], " in debug mode" if ka['debug'] else ''
        ) )
    run_smugapi(**ka)

if __name__ == "__main__":
    cli()


