# -*- coding: utf-8 -*-
"""
 __author__:  @haopeng_dong
 __datetime__:  2020/1/23
"""
import os
from datetime import datetime

import click

from . import __version__
from .files_content import root_setup_s
from .rflask import (
    make_project_dir,
    write_file,
    init_root_dir,
    init_applications_dir,
    init_enums_dir,
    init_exceptions_dir,
    init_flask_ext_dir,
    init_scripts_dir,
    init_tests_dir,
    init_requirements_dir,
    init_utils_dir,
    init_root_files
)


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(__version__)
    ctx.exit()


@click.group()
@click.option('--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True)
def rflask():
    """A general utility script to init flask restful project.

    Example:

    $ rflask init
    """
    pass


@rflask.command('init')
def init():
    """Init restful project."""
    project_name = click.prompt('\033[0;32m * project_name: \033[0',
                                type=str,
                                default='flask-restful-api-{}'.format(datetime.now().strftime('%Y%m%d-%H%M%S')))
    author = click.prompt('\033[0;32m * author: \033[0', default='Deacon')
    author_email = click.prompt('\033[0;32m * author_email: \033[0', default='deacon@example.com')
    description = click.prompt('\033[0;32m * description: \033[0', default='Flask restful api project.')
    project_path = os.path.join(os.getcwd(), project_name)
    make_project_dir(project_path)
    # init setup.py file.
    write_file(os.path.join(project_path, 'setup.py'), root_setup_s(project_name, author, author_email, description))
    init_root_dir(project_path)
    init_applications_dir(project_path)
    init_enums_dir(project_path)
    init_exceptions_dir(project_path)
    init_flask_ext_dir(project_path)
    init_requirements_dir(project_path)
    init_scripts_dir(project_path)
    init_tests_dir(project_path)
    init_utils_dir(project_path)
    init_root_files(project_path)
    print('')
    print('\033[0;32mDone.\033[0')
