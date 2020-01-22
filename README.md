# ProvBuild

This repository provides the ProvBuild tool for the paper "Improving Data Scientist Efficiency with Provenance".

## Tool
ProvBuild is built on top of noWorkflow (Version 1.11.2). Check out [noWorkflow's Github](https://github.com/gems-uff/noworkflow) for more information details.

### Prerequisites
This version of ProvBuild only support **Python 2.7**.

To install ProvBuild, you should follow these basic instructions:

If you have python `pip`, install the following packages:

	$ pip install flask
	$ pip install sqlalchemy
	$ pip install pyposast
	$ pip install future
	$ pip install apted

### Clone the Repository

	$ git clone https://github.com/CrystalMei/ProvBuild.git
	$ cd ProvBuild

### Run ProvBuild Interface

- Step 1: Run `python app.py` and it will start a webpage as shown below:
![StartPage](img/1.png)

- Step 2: Upload the test script `./example/Test.py`, then the webpage shows:
![](img/2.png)

- Step 3: Interact with ProvBuild, e.g., exploring variable `e` in the test script.
![](img/3.png)

### Run ProvBuild Manually
* Initial and run the given test Python script: `./make.sh r <script_name>.py`

* If you want to modify a function, get the ProvScript with the given function: `./make.sh uf <function_name>`

* If you want to modify a variable, get the ProvScript with the given variable: `./make.sh uv <variable_name>`

* Execute the ProvScript and update the result: `./make.sh d`

* Merge the ProvScript into the original test script: `./make.sh m`


## Acknowledgements
This work was supported by NSF award #1450277, the U.S. Air Force and DARPA under contract FA8750-16-C-0045.

## License Terms
The MIT License (MIT)

Copyright (c) 2013 Universidade Federal Fluminense (UFF), Polytechnic Institute of New York University.
Copyright (c) 2018, 2019, 2020 President and Fellows of Harvard College.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
