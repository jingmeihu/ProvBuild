#!/bin/sh
echo "I have several commands: r-run, uf-update function, uv-update variable, d-runupdate, m-merge"
case "$1" in
	r)
		echo "Remove the .noworkflow folder ..."
		rm -r .noworkflow
		echo "The test file name is $2 ..."
		python __init__.py run "$2"
		;;
	uf)
		echo "The trial id is 1 ..."
		echo "The function name is $2 ..."
		python __init__.py update -t 1 -fn "$2" --debug 0
		;;
	uv)
		echo "The trial id is 1 ..."
		echo "The variable name is $2 ..."
		python __init__.py update -t 1 -vn "$2" --debug 0
		;;
	d)
		echo "Compile ProvScript.py ..."
		# python __init__.py runupdate ProvScript.py
		python ProvScript.py
		;;
	m)
		echo "The trial id is 1 ..."
		echo "Generate new file ..."
		python __init__.py merge -t 1
		;;
	*) 
		echo "Invalid command"
		;;
esac

