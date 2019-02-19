# ProvBuild

## Dependencies
use python `pip` to install the following packages: `flask`, `sqlalchemy`, `pyposast`, `future`, `apted`

## How to run ProvBuild interface
1) cd into provbuild directory:

`cd provbuild`

2) run: (it will start a webpage and you can upload your script)

`python app.py`


## How to run ProvBuild manually
1) cd into provbuild directory:

`cd provbuild`

2) run (test file name):

`./make.sh r <script_name>.py`

3) modify function (function name):

`./make.sh uf <function_name>`

4) modify variable (variable name):

`./make.sh uv <variable_name>`

5) run update:

`./make.sh d`

6) merge:

`./make.sh m`
