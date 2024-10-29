# ![Open Quantum Design](docs/img/oqd-logo-text.png)

[![black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
![versions](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)
[![CI](https://github.com/OpenQuantumDesign/oqd-compiler-infrastructure/actions/workflows/CI.yml/badge.svg)](https://github.com/OpenQuantumDesign/oqd-compiler-infrastructure/actions/workflows/CI.yml)

<h2 align="center">
    Open Quantum Design: Compiler Infrastructure
</h2>

## What's here:

This repository contains the base classes for various compilation and transpilation tasks with the OQD stack.

## Installation

Install with pip:

```bash
pip install git+https://github.com/OpenQuantumDesign/oqd-compiler-infrastructure.git
```

To install locally for development,

```bash
git clone https://github.com/OpenQuantumDesign/oqd-compiler-infrastructure.git
```

## Documentation

To deploy the documentation locally, implemented with [mkdocs](https://www.mkdocs.org/), run the following commands:

```bash
pip install .[docs]
mkdocs serve
```
