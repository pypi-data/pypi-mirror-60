# Glorified secrets manager
[![pipeline status](https://gitlab.com/tutti-ch/team-data/glosm/badges/master/pipeline.svg)](https://gitlab.com/tutti-ch/team-data/glosm/commits/master)
[![coverage report](https://gitlab.com/tutti-ch/team-data/glosm/badges/master/coverage.svg)](https://gitlab.com/tutti-ch/team-data/glosm/commits/master)

A Python package and command line tool to manage secrets inside `~/.glosm.json`.

## Installing
`pip install glosm`

## Publishing to PyPI
To publish to PyPI, create tag x.y.z first. Then:

```
git checkout x.y.z
python setup.py sdist
twine upload dist/glosm-x.y.z.tar.gz
```
