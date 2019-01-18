# Tail application logs
Connect to application logs located on a Kubernetes or on a server

### Example:

```
$ logs services
$ logs -i services
$ logs --int partner-accounts
$ logs --client-int partner-accounts
```

## Dependencies
- Python3
- Pyenv
- jq
- kubetail
- bash complete
- ssh keys

## Installing to the pyenv 'tools3'

**Installation**

```
pyenv activate tools3
pip install .
pyenv deactivate

# or use the script:
reinstall
```

**Uninstalling**

```
pyenv activate tools3
pip uninstall logs
pyenv deactivate
```

**Development**

```
pyenv local tools3
pytest
```

**Bash Completion**

See [Evernote - Bash Completion](https://www.evernote.com/shard/s7/nl/829807/2a62d81d-319f-4066-8693-4c5fc7df29b9/)
```
Add script to /usr/local/etc/bash_completion.d
```

