# Littlenv

A simple script for manage .env in django (or flask), is very easy, you just have to import this library in your manage.py (or your app init file)

## Instalation

    pip install littlenv

## How to use
You can import it and load it before start using or importing any app

    from littlenv impot littlenv

    littlenv.load(allow_ovveride=True)

The 'allow_override' argument is used to allow the plugin to override existing os.environ variables. If it is False script will skip existing os.environ variables.
