# ProvBuild

## Dependencies
use python `pip` to install the following packages: `flask`, `sqlalchemy`, `pyposast`, `future`, `apted`

## How to run it
1) cd into noworkflow directory:

`cd capture/noworkflow`

2) run: (it will start a webpage and you can upload your script)

`python app.py`

## How to run it manually - 1
1) cd into noworkflow directory:

`cd capture/noworkflow`

2) run the script _<script_name>.py_ once, we assume the trial id for this run is 1:

`python __init__.py run <script_name>.py`

3) **Function Modify Mode** if you want to modify `<function_name>` in test.py, you need provide trial id 1 (`-t 1`) and function name func_1 (`-fn <function_name>`):

`python __init__.py update -t 1 -fn <function_name>`

4) **Variable Modify Mode** if you want to modify variable `<variable_name>` in test.py, you need provide trial id 1 (`-t 1`) and variable name x (`-vn <variable_name>`):

`python __init__.py update -t 1 -vn <variable_name>`

5) then you can check the ProvScript.py, this script is a cleaner version for your input function (`<function_name>`) or input variable (`<variable_name>`)

6) after you finish modifying ProvScript.py, you can execute this cleaner version (in a similar way as you run the previous script) and check your result:

`python __init__.py runupdate ProvScript.py`

7) if you satisfy with your new result, you can merge ProvScript.py into your previous file (trial id is 1) using:

`python __init__.py merge -t 1`

we name the new script _new-test.py_ and store it in the same directory.


## How to run it manually -2
1) cd into noworkflow directory:

`cd capture/noworkflow`

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
