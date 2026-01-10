# Installation

## Requirements

- Python 3.10 or higher
- pip

## Install from PyPI

```bash
pip install api-governor
```

## Install from Source

```bash
git clone https://github.com/akz4ol/api-governance-skill.git
cd api-governance-skill
pip install -e .
```

## Install with Development Dependencies

```bash
pip install -e ".[dev]"
```

## Verify Installation

```bash
api-governor --version
```

## Docker

```bash
docker pull ghcr.io/akz4ol/api-governor:latest
docker run --rm -v $(pwd):/specs api-governor /specs/openapi.yaml
```
