#!/bin/sh
# echo "I have several commands: r-run, uf-update function, uv-update variable, d-runupdate, m-merge"
case "$1" in
	r)
		# echo "Remove the .noworkflow folder ..."
		rm -r .noworkflow
		rm -f ProvScript.py
		echo "The test file name is $2 ..."
		python __init__.py run "$2"
		;;
	uf)
		# echo "The trial id is 1 ..."
		echo "The function name is $2 ..."
		python __init__.py update -t 1 -fn "$2" --debug 1
		;;
	ufm)
		# echo "The trial id is 1 ..."
		echo "The function name is $2 ..."
		echo "Also add $3 ..."
		python __init__.py update -t 1 -fn "$2" --morefunc "$3" --debug 0
		;;
	uv)
		# echo "The trial id is 1 ..."
		echo "The variable name is $2 ..."
		python __init__.py update -t 1 -vn "$2" --debug 1
		;;
	uvm)
		# echo "The trial id is 1 ..."
		echo "The variable name is $2 ..."
		echo "Also add $3 ..."
		python __init__.py update -t 1 -vn "$2" --morefunc "$3" --debug 0
		;;
	d)
		echo "Compile ProvScript.py ..."
		# python __init__.py runupdate ProvScript.py
		python ProvScript.py
		;;
	m)
		# echo "The trial id is 1 ..."
		echo "Generate new file ..."
		python __init__.py merge -t 1
		;;
	g)
		echo "Regenerate ProvScript.py ..."
		python __init__.py regen -t 1 -f "$2"
		;;
	*) 
		echo "Invalid command"
		;;
esac

