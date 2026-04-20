# Getting Started with pipm


## Installation
   - ### GitHub
     - #### clone
        ```BASH
        git clone https://github.com/adityajodha2299-bit/pipm.git
        ```
     - #### install
        ```BASH
        cd pipm
        pip install -e .
        ```
    
      #### All In One
        ```BASH
        git clone https://github.com/adityajodha2299-bit/pipm.git
        cd pipm
        pip install -e .
        ```

## Quick Start
   1. Create a new environment (named after the current folder by default).
        ```bash
        pipm create
        ```
        <!-- ![gif](assets/good_attempt.gif) -->

   1. Bind the environment to your project.
        ```bash
        pipm use
        ```
        This creates a .pipm file in your project root.

   1. Install packages
        ```SHELL
        pipm add "foo"
        pipm add "foo>=0.19"
        ```
    
   1. Run your script
        ```bash
        pipm run my_script.py
        ```
        Or, if you have a `main_script` set in `.pipm`, just:

        ```bash
        pipm run
        ```
    
   1. Delete an environment
        ```bash
        pipm delete myenv
        ```