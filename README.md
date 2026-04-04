# pipm 

A lightweight Python environment manager inspired by tools like uv, pipx, and poetry.

## Features

* Create isolated virtual environments
* Manage environments centrally (~/.pipm/envs)
* Install packages into environments
* Track installed packages via metadata
* Simple CLI interface

## Installation

```bash
pip install -e .
```

## Usage

```bash
pipm create myenv
pipm delete myenv
```

## Project Structure

* `pipm/core` → execution layer
* `pipm/env` → environment management
* `pipm/cli` → CLI interface

## Future Plans

* `pipm use` (active environment)
* `pipm run` (run without activation)
* `pipm add` (install packages easily)

---

Built for learning and experimentation.
