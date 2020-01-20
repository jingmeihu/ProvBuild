# ProvBuild

This repository provides the ProvBuild tool for the paper "Improving Data Scientist Efficiency with Provenance".

## Tool
ProvBuild is built on top of noWorkflow. Check out [noWorkflow's Github](https://github.com/gems-uff/noworkflow) for more information details.

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
