# pypi-downloader

## Description

This project can be used to mirror the pypi index using the new warehouse API.

This project consists of three scripts:

1. the main single threaded script pypi-downloader.py
1. a multithreaded version of the main script, pypi-downloader-mt.py
1. a helper script to get the current list of packages from the pypi index site currently located at: <https://pypi.org/>

## Config file

If a config file is specified as a command line parameter, the config file uses the YAML format.

The config file consists of three sections:

1. logging - Specifies a logging.dictConfig dictionary
1. threads - Number of threads to use
1. packages - List of packages to download, if no packages are specified, all packages are downloaded from the pypi index site
1. blacklist - List of packages to not download

Note: For logging, this module uses the root logger only.
Note: Values specified in the config file can be overridden by values specified on the command line.

## Config file examples

### Default configuration

`
logging:
  version: 1
  formatters:
    simple:
      format: '[%(levelname)s]: %(message)s'
  handlers:
    console1:
      class: logging.StreamHandler
      level: ERROR
      formatter: simple
      stream: ext://sys.stderr
    console2:
      class: logging.StreamHandler
      level: DEBUG
      formatter: simple
      stream: ext://sys.stdout
  root:
    level: INFO
    stream: ext://sys.stdout
    handlers: [console1, console2]
threads: 1
packages:
blacklist:
`

### Default configuration with packages and blacklist specified and non default thread count

`
logging:
  version: 1
  formatters:
    simple:
      format: '[%(levelname)s]: %(message)s'
  handlers:
    console1:
      class: logging.StreamHandler
      level: ERROR
      formatter: simple
      stream: ext://sys.stderr
    console2:
      class: logging.StreamHandler
      level: DEBUG
      formatter: simple
      stream: ext://sys.stdout
  root:
    level: INFO
    stream: ext://sys.stdout
    handlers: [console1, console2]
threads: 5
packages:

- tox
- mypy

blacklist:

- pyyaml

`

Note: In the previous example, the list of packages should not have surrounding blank lines and should be indented 2 spaces under their respective key (packages or blacklist).