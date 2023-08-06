#!/bin/bash

# clean up
python setup.py clean --all
rm -r dist

# build package
python setup.py sdist bdist_wheel

# upload package (you will be prompted for user name and password)
python -m twine upload dist/*
