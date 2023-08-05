# -*- coding: utf-8 -*-
"""
 __author__:  @haopeng_dong
 __datetime__:  2020/1/16
"""
import os

from .exceptions import MakeDirException
from .files_content import (
    root_env_s,
    root_env_example_s,
    root_gitignore_s,
    root_init_s,
    root_app_s,
    root_autoapp_s,
    root_compat_s,
    root_database_s,
    root_extensions_s,
    root_gunicorn_s,
    root_readme_s,
    root_settings_s,
    root_supervisord_s,
    applications_test_init_s,
    applications_test_models_s,
    applications_test_urls_s,
    applications_test_views_s,
    applications_user_init_s,
    applications_user_models_s,
    applications_user_readme_s,
    applications_user_views_s,
    exceptions_project_excepions_s,
    flask_ext_logger_s,
    requirements_dev_s,
    requirements_prod_s,
    utils_commands_s
)


def write_file(path, content):
    print("Create file %s" % path)
    with open(path, 'w+') as f:
        f.write(content)
        f.close()


def make_dir(path):
    print("Make directory %s" % path)
    if os.path.exists(path):
        raise MakeDirException('This path is exist.')
    os.mkdir(path)


def make_project_dir(project_path):
    make_dir(project_path)


def init_root_dir(project_path):
    dirs = [
        'applications',
        'enums',
        'exceptions',
        'flask_ext',
        'logs',
        'requirements',
        'scripts',
        'utils'
    ]
    for dir_name in dirs:
        make_dir(os.path.join(project_path, dir_name))


def init_root_files(project_path):
    create_files = [
        {"path": os.path.join(project_path, '.env'), "content": root_env_s()},
        {"path": os.path.join(project_path, '.env_example'), "content": root_env_example_s()},
        {"path": os.path.join(project_path, '.gitignore'), "content": root_gitignore_s()},
        {"path": os.path.join(project_path, '__init__.py'), "content": root_init_s()},
        {"path": os.path.join(project_path, 'app.py'), "content": root_app_s()},
        {"path": os.path.join(project_path, 'autoapp.py'), "content": root_autoapp_s()},
        {"path": os.path.join(project_path, 'compat.py'), "content": root_compat_s()},
        {"path": os.path.join(project_path, 'database.py'), "content": root_database_s()},
        {"path": os.path.join(project_path, 'extensions.py'), "content": root_extensions_s()},
        {"path": os.path.join(project_path, 'gunicorn.conf'), "content": root_gunicorn_s()},
        {"path": os.path.join(project_path, 'gunicorn_example.conf'), "content": root_gunicorn_s()},
        {"path": os.path.join(project_path, 'gunicorn_example.conf'), "content": root_gunicorn_s()},
        {"path": os.path.join(project_path, 'README.rst'), "content": root_readme_s()},
        {"path": os.path.join(project_path, 'settings.py'), "content": root_settings_s()},
        {"path": os.path.join(project_path, 'supervisord.conf'), "content": root_supervisord_s()},
        {"path": os.path.join(project_path, 'supervisord_example.conf'), "content": root_supervisord_s()},
    ]
    for create_file in create_files:
        write_file(create_file['path'], create_file['content'])


def init_applications_dir(project_path):
    dirs = ['test', 'user']
    for dir_name in dirs:
        make_dir(os.path.join(project_path, 'applications', dir_name))

    write_file(os.path.join(project_path, 'applications', '__init__.py'), '')

    test_dir_path = os.path.join(project_path, 'applications', 'test')
    test_dir_files = [
        {"path": os.path.join(test_dir_path, '__init__.py'), "content": applications_test_init_s()},
        {"path": os.path.join(test_dir_path, 'models.py'), "content": applications_test_models_s()},
        {"path": os.path.join(test_dir_path, 'README.rst'), "content": applications_test_models_s()},
        {"path": os.path.join(test_dir_path, 'urls.py'), "content": applications_test_urls_s()},
        {"path": os.path.join(test_dir_path, 'views.py'), "content": applications_test_views_s()},
    ]
    for test_dir_file in test_dir_files:
        write_file(test_dir_file['path'], test_dir_file['content'])

    user_dir_path = os.path.join(project_path, 'applications', 'user')
    user_dir_files = [
        {"path": os.path.join(user_dir_path, '__init__.py'), "content": applications_user_init_s()},
        {"path": os.path.join(user_dir_path, 'models.py'), "content": applications_user_models_s()},
        {"path": os.path.join(user_dir_path, 'README.rst'), "content": applications_user_readme_s()},
        {"path": os.path.join(user_dir_path, 'views.py'), "content": applications_user_views_s()},
    ]
    for user_dir_file in user_dir_files:
        write_file(user_dir_file['path'], user_dir_file['content'])


def init_enums_dir(project_path):
    write_file(os.path.join(project_path, 'enums', '__init__.py'), '')


def init_exceptions_dir(project_path):
    write_file(os.path.join(project_path, 'exceptions', '__init__.py'), '')
    write_file(os.path.join(project_path, 'exceptions', 'project_excepions.py'), exceptions_project_excepions_s())


def init_flask_ext_dir(project_path):
    write_file(os.path.join(project_path, 'flask_ext', '__init__.py'), '')
    write_file(os.path.join(project_path, 'flask_ext', 'logger.py'), flask_ext_logger_s())


def init_requirements_dir(project_path):
    write_file(os.path.join(project_path, 'requirements', 'dev.txt'), requirements_dev_s())
    write_file(os.path.join(project_path, 'requirements', 'prod.txt'), requirements_prod_s())


def init_scripts_dir(project_path):
    write_file(os.path.join(project_path, 'scripts', '__init__.py'), '')


def init_utils_dir(project_path):
    write_file(os.path.join(project_path, 'utils', '__init__.py'), '')
    write_file(os.path.join(project_path, 'utils', 'commands.py'), utils_commands_s())
