# Django shortcuts

**You spend too much time typing `python3 manage.py`**

[![badge](https://badge.fury.io/py/django-shts3.svg)](https://pypi.python.org/pypi/django-shts3)

The tool is used by [Uptrader](https://uptrader.io/) team for more then two years

It's a fork of [django-shortcuts](https://github.com/jgorset/django-shortcuts) by [Johannes Gorset](https://github.com/jgorset)

### Features

- shorter aliases for built-in commands
- config files for user-defined shortcuts
- works from any project subdirectory

```bash
$ python3 manage.py shell
$ cd any/project/subdirectory
$ d s  # the same
```

## Installation

```bash
$ pip3 install django-shts3
```

## Usage

PyPi package installs `django` and `d` binaries.
Arguments with `-` at the begining before command are eaten by the Python interpretator.

```bash
$ django <command or shortcut>

$ d <command or shortcut>
```

## Default shortcuts

Alias   | Command
--------|---------------
c       | collectstatic
r       | runserver
s / sh  | shell
t       | test
m       | migrate
mkm     | makemigrations
csu     | createsuperuser
cpw     | changepassword
sa      | startapp

## Customization

The program loads extra aliases from `.django_shts3` file in project directory and in home directory.

Example:

```
alias @@@ command
m @@@ migrate
```

### Example:

I have a docker container with Django and I should bind to 0.0.0.0:8000 on runserver command, so I have:

```
$ cat .django_shts3
r @@@ runserver 0.0.0.0:8000
```

That allows me to start Django server like:

```
$ d r
```

## Contributing

Pull requests are welcome!

Please report all problems to [GitLab issues](https://gitlab.com/qwolphin/django-shts3/issues)
