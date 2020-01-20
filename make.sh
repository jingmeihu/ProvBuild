#!/bin/sh
# echo "I have several commands: r-run, uf-update function, uv-update variable, d-runupdate, m-merge"
case "$1" in
	r) # initial and run the given test python script
		rm -rf .noworkflow
		rm -f ProvScript.py
		echo "The test file name is $2 ..."
		python __init__.py run "$2"
		;;
	uf) # get ProvScript with the given function $2
		echo "The function name is $2 ..."
		python __init__.py update -t 1 -fn "$2" --debug 0
		;;
	ufm) # get ProvScript with the given function $2 and $3
		echo "The function name is $2 ..."
		echo "Also add $3 ..."
		python __init__.py update -t 1 -fn "$2" --morefunc "$3" --debug 0
		;;
	uv) # get ProvScript with the given variable $2
		echo "The variable name is $2 ..."
		python __init__.py update -t 1 -vn "$2" --debug 0
		;;
	uvm) # get ProvScript with the given variable $2 and function $3
		echo "The variable name is $2 ..."
		echo "Also add $3 ..."
		python __init__.py update -t 1 -vn "$2" --morefunc "$3" --debug 0
		;;
	d) # run ProvScript
		echo "Compile ProvScript.py ..."
		python ProvScript.py
		;;
	m) # merge ProvScript into the original test script
		echo "Generate new file ..."
		python __init__.py merge -t 1
		;;
	g) # Regenerate ProvScript
		echo "Regenerate ProvScript.py ..."
		python __init__.py regen -t 1 -f "$2"
		;;
	*) 
		echo "Invalid command"
		;;
esac

