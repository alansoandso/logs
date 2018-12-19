# Ebay prices
Search on [ebay](ebay.co.uk) auctions for sold prices and available auctions for sniping on [gixen](gixen.com)

### Example:

```
$ logs services
...

...
```

## Installing to the pyenv 'tools3'

**Installation**

```
pyenv activate tools3
pip install .
pyenv deactivate
```

**Uninstalling**

```
pyenv activate tools3
pip uninstall logs
pyenv deactivate
```

**Development**

```
pyenv virtualenv 3.6.0 logs
pyenv local logs
pip install -r requirements.txt
```