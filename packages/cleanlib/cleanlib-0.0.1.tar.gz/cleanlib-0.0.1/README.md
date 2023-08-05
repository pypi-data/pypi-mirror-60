pip install setuptools wheel twine pipenv-setup
pipenv run python setup.py bdist_wheel --universal
pipenv run python setup.py sdist bdist_wheel

pipenv run python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
