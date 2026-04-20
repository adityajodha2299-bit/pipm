# pipm 

A lightweight Python environment manager inspired by tools like uv, pipx, and poetry.

## Features

* Create isolated virtual environments
* Manage environments centrally (~/.pipm/envs)
* Install packages into environments
* Track installed packages via metadata
* Simple CLI interface

## Installation
> You can visit [Start Guilde](START_GUIDE.md)

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

* `pipm runx` (For fast easy one time use)

---

Built for learning and experimentation.

---

## For Mental Model
> You can visit [MentalModle.md](MENTAL_MODEL.md) for more information.