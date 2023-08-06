#!/usr/bin/env python3
import shlex
import os
import sys


ALIASES = {
    # Django
    'c'  : 'collectstatic',
    'r'  : 'runserver',
    'sp' : 'startproject',
    'sa' : 'startapp',
    't'  : 'test',

    # Shell
    's'  : 'shell',
    'sh' : 'shell',

    # Auth
    'csu': 'createsuperuser',
    'cpw': 'changepassword',

    # Migrations
    'm'  : 'migrate',
    'mg' : 'migrate',
    'mkm': 'makemigrations'
}


def load_config(path):
    try:
        with open(path, 'r') as f:
            for line_number, raw_string in enumerate(f, 1):
                string = raw_string.strip('\n')
                try:
                    alias, command = string.split(' @@@ ')
                except ValueError:
                    error = (
                        "django-shts3: can't parse config file {path} (line {line_number})"
                        .format(path=path, line_number=line_number)
                    )
                    sys.exit(error)

                ALIASES[alias] = command
    except (OSError, IOError):
        pass


def expand_command(command):
    try:    
        alias = ALIASES[command]
    except KeyError:
        return [command]

    try:
        return shlex.split(alias)
    except ValueError as e:
        sys.exit(
            "django-shts3: can't parse alias: {alias} ({error})"
            .format(alias=alias, error=str(e))
        )


def main():
    project_dir = os.getcwd()
    while True:
        manage_script = os.path.join(project_dir, 'manage.py')

        if os.path.exists(manage_script):
            break

        parent_dir = os.path.dirname(project_dir)
        if parent_dir == project_dir:  # root dir
            sys.exit(
                "django-shts3: No 'manage.py' script found in this directory or its parents"
            )
        
        project_dir = parent_dir

    home_config = os.path.expanduser('~/.django_shts3')
    load_config(home_config)

    app_config = os.path.join(project_dir, '.django_shts3')
    load_config(app_config)

    args = sys.argv[1:]
    if args:
        args = expand_command(args[0]) + args[1:]

    parameters = [sys.executable, manage_script] + args
    os.execvp(sys.executable, parameters)


if __name__ == '__main__':
    main()
