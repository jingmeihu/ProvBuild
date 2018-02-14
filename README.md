# ProvBuild

## how to run it manually
1) cd into noworkflow directory:

`cd capture/noworkflow`

2) run the script _test.py_ once, we assume the trial id for this run is 1:

`python __init__.py run test.py`

3) **Function Modify Mode** if you want to modify `func_1` in test.py, you need provide trial id 1 (`-t 1`) and function name func_1 (`-fn func_1`):

`python __init__.py update -t 1 -fn func_1`

4) **Variable Modify Mode** if you want to modify variable `x` in test.py, you need provide trial id 1 (`-t 1`) and variable name x (`-vn x`):

`python __init__.py update -t 1 -vn x`

5) then you can check the ProvScript.py, this script is a cleaner version for your input function (`func_1`) or input variable (`x`)

6) after you finish modifying ProvScript.py, you can execute this cleaner version (in a similar way as you run the previous script) and check your result:

`python __init__.py runupdate ProvScript.py`

7) if you satisfy with your new result, you can merge ProvScript.py into your previous file (trial id is 1) using:

`python __init__.py merge -t 1`

we name the new script _new-test.py_ and store it in the same directory.


## how to run it automatically
1) cd into noworkflow directory:

`cd capture/noworkflow`

2) run (test file name):

`./make.sh r test.py`

3) modify function (function name):

`./make.sh uf func_1`

4) modify variable (variable name):

`./make.sh uv var_1`

5) run update:

`./make.sh d`

6) merge:

`./make.sh m`
