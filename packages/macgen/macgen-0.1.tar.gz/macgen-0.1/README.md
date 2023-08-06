# `magcen` - MAC Address Generation Utility and Library

`macgen` is a simple python library to facilitate the generation of MAC addresses.

## Install

```bash
pip install macgen
```

## Usage

```bash
# generate a MAC with default options (locally administered, unicast)
macgen

# generate a MAC with a dash as the separator
macgen -s -

# generate a MAC with no separator
macgen -S

# generate a local / multicast MAC
macgen -m

# generate a random global (supposedly OUI enforced) / unicast MAC
macgen -g

# generate a global / multicast MAC
macgen -mg
```

## Planned Features

- Generate a repeatable MAC from a seed string
- Supply an OUI prefix

## Development Setup

```bash
virtualenv -p python3 venv
. venv/bin/activate
pip install -r requirements.txt
```
