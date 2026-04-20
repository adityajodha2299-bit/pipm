# Comparison

This document compares **pipm** with existing tools: `pip`, `pipx`, `uv`, and `cargo`.

No marketing. Just trade-offs.

---

## 🧭 Scope

| Tool  | Primary Purpose                                     |
| ----- | --------------------------------------------------- |
| pip   | Install Python packages                             |
| pipx  | Run Python apps globally in isolated envs           |
| uv    | Fast package manager + environment + resolver       |
| cargo | Rust package manager + build system                 |
| pipm  | Project-bound environment manager (simple workflow) |

---

## ⚖️ Feature Comparison

| Feature                       | pip | pipx          | uv              | cargo        | pipm            |
| ----------------------------- | --- | ------------- | --------------- | ------------ | --------------- |
| Creates virtual environments  | ❌   | ⚠️ (internal) | ✅               | ✅ (implicit) | ✅               |
| Project ↔ env binding         | ❌   | ❌             | ⚠️              | ✅            | ✅               |
| Dependency tracking           | ❌   | ❌             | ✅               | ✅            | ✅ (basic)       |
| Lockfile / reproducibility    | ❌   | ❌             | ✅               | ✅            | ❌               |
| Built-in script runner        | ❌   | ❌             | ✅               | ✅            | ✅               |
| Handles dependency resolution | ❌   | ❌             | ✅ (very strong) | ✅            | ❌               |
| Speed                         | ⚠️  | ⚠️            | 🚀              | 🚀           | ⚠️              |
| Production readiness          | ✅   | ✅             | ✅               | ✅            | ❌ (early stage) |
| Ecosystem maturity            | 🔥  | 🔥            | 🚀 growing      | 🔥           | ❌               |

---

## 🔍 Tool-by-Tool Breakdown

### pip

**What it does well**

* Official, stable, everywhere
* Simple: install packages

**Limitations**

* No environment management
* No dependency tracking
* Easy to break global Python

👉 pip is a *building block*, not a workflow tool.

---

### pipx

**What it does well**

* Clean global installs for CLI tools
* Avoids polluting global Python

**Limitations**

* Not for projects
* No dependency tracking
* No workflow support

👉 pipx is for *apps*, not development.

---

### uv

**What it does well**

* Extremely fast (Rust-based)
* Full dependency resolver
* Lockfiles, reproducibility
* Replaces pip + venv + pip-tools

**Limitations**

* More complex mental model
* Still evolving ecosystem

👉 uv is the **most powerful modern Python tool right now**.

---

### cargo

**What it does well**

* Gold standard DX
* One tool: build, run, test, deps
* Deterministic builds

**Limitations**

* Not Python (different ecosystem)
* Tight integration depends on Rust language design

👉 cargo is what Python tools *wish* they were.

---

### pipm

**What it does well**

* Very simple workflow:

  * create → use → add → run
* Clear project ↔ env binding
* Minimal mental overhead
* Tracks installed packages automatically

**Limitations**

* No dependency resolver
* No lockfile (not reproducible)
* Slower (relies on pip)
* Early-stage, not production-ready
* No ecosystem/tooling around it

👉 pipm prioritizes **simplicity over power**.

---

## 🧠 Honest Positioning

pipm is **not competing with uv**.

* If you need:

  * speed
  * reproducibility
  * complex dependency management
    → use **uv**

* If you want:

  * minimal setup
  * clean workflow
  * learning-friendly tooling
    → pipm can make sense

---

## ⚠️ Reality Check

pipm currently:

* wraps pip
* adds metadata tracking
* simplifies UX

It does **not**:

* solve dependency resolution
* guarantee reproducibility
* replace mature tools

---

## 🎯 Conclusion

* `pip` → low-level tool
* `pipx` → global app runner
* `uv` → modern full-featured solution
* `cargo` → ideal design (reference)
* `pipm` → simple, experimental workflow tool

pipm is useful **only if you value simplicity over capability**.

---
