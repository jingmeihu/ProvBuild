#!/bin/sh
echo "I have several commands: r-run, u-update, d-runupdate, m-merge"
case "$1" in
	r)
		echo "Remove the .noworkflow folder ..."
		rm -r .noworkflow
		echo "The test file name is $2 ..."
		python __init__.py run -v "$2"
		;;
	u)
		echo "The trial id is $2 ..."
		echo "The function name is $3 ..."
		python __init__.py update -t "$2" -fn "$3"
		;;
	d)
		echo "Generate ProvScript.py ..."
		python __init__.py runupdate ProvScript.py
		;;
	m)
		echo "The trial id is $2 ..."
		echo "Generate new file ..."
		python __init__.py merge -t "$2"
		;;
	*) 
		echo "Invalid command"
		;;
esac

