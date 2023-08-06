# setup_scmversion

* Master

    - [![Pipeline status](https://gitlab.com/jfaleiro/setup_scmversion/badges/master/pipeline.svg)](https://gitlab.com/jfaleiro/setup_scmversion)
    - [![Coverage status](https://gitlab.com/jfaleiro/setup_scmversion/badges/master/coverage.svg?job=coverage)](https://gitlab.com/jfaleiro/setup_scmversion)

* 0.0.1

    - [![Pipeline status](https://gitlab.com/jfaleiro/setup_scmversion/badges/release/0.0.1/pipeline.svg)](https://gitlab.com/jfaleiro/setup_scmversion/tree/release/0.0.1)
    - [![Coverage status](https://gitlab.com/jfaleiro/setup_scmversion/badges/release/0.0.1/coverage.svg?job=coverage)](https://gitlab.com/jfaleiro/setup_scmversion/tree/release/0.0.1)



Builds a pythonic version number based on information available on your scm (tag, branch, and number of commits).

See [LICENSE](LICENSE) for important licensing information.

## Instalation

Your `setup.py` will need `jfaleiro.setup_scmversion` to start - so you either make sure you have it pre-installed using pip:

```bash
pip install jfaleiro.setup_scmversion
```

or add this on the very top of your `setup.py` and forget about it moving forward.

```python
try:
    import setup_scmversion
except ModuleNotFoundError as e:
    from pip._internal import main
    assert main('install jfaleiro.setup_scmversion'.split()) == 0
    
from setup_scmversion import version
```

You should add it to your `setup_requires` parameter in `setup.py` as well:

```python
setup(
	...
    setup_requires=['jfaleiro.setup_scmversion'],
	...
)
```

## Using

A pythonic version number is created from standard data available in your *scm*, i.e. tag, branch name, and number of differences from master:

```python
setup(
	...
    version=version(),
	...
)
```

For example, release tags `release/<version>` with `nnn` differences from master will produce version `<version>.dev<nnn>` and a tagged version `<tag>` on master will produce the version `<tag>`. Everything else will produce `master.dev<nnn>` for master or `no-version.dev<nnn>` for any other branch. 

You can also use a command line based shortcut to peek at the current version:

```bash
jfaleiro@itacoatiara:~/gitrepos/setup_scmversion (release/0.0.1 *+)$ scmversion 
0.0.1.dev1
```


Enjoy.