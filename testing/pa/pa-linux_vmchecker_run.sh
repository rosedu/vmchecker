#!/bin/sh

# @author claudiugh 
# Script generic de rulare a temelor sub limita de timp 
# depinde de:
# - tracker: trebuie sa fie compilat din Makefile.checker 
# - verify: executabil generic (script sh/bash/python sau executabil) care verifica outputul studentului 
#

#home=$1
#cd $home

INPUT_DIR=input
OUTPUT_DIR=output
REFERENCES_DIR=refs
TRACKER=tracker
VERIFIER=verify

print_fail_reason() 
{
    reason=`head -n 1 $test_name-tracker.err | sed s/make.*\]\ //`
    echo reason: $reason
}

run_test()
{
    # run test 
    if [ -f $TRACKER ]; 
    then 
	./$TRACKER $timeout $INPUT_DIR/$input_file $OUTPUT_DIR/$output_file \
	    > $test_name-tracker.out 2> $test_name-tracker.err; 
	err=$?;
	if [ $err -eq 0 ];
	then
	    if [ -f $VERIFIER ]; 
	    then
		./$VERIFIER $INPUT_DIR/$input_file \
		    $OUTPUT_DIR/$output_file \
		    $REFERENCES_DIR/$output_file \
		    > $test_name-verifier.out
		if [ $? -eq 0 ]; 
		then
		    echo $test_name: passed; 
		    echo `cat $test_name-tracker.out`;
		    return 0; 
		else
		    echo $test_name: failed; 
		    echo reason: `cat $test_name-verifier.out`; 
		    return 1; 
		fi
	    else
		echo "verifier not found";
		exit; 
	    fi
	else
	    echo $test_name: failed;
	    print_fail_reason; 
	    return 1; 
	    echo; 
	fi
    else 
	echo "the tracker is not built"; 
	exit; 
    fi  
}


run_all_tests()
{
    timeout=`head -n 1 $lang.timeout`
    input_files=`ls $INPUT_DIR`
    passed=0
    failed=0
    for input_file in $input_files
    do
	test_name=`echo $input_file | sed s/\.in//`
	output_file=$test_name.out
	run_test
	if [ $? -eq 0 ];
	then
	    passed=`expr $passed + 1` 
	else
	    failed=`expr $failed + 1`
	fi
	echo; 
    done
    echo; echo results: $passed passed, $failed failed; 
}

# returns 1 for c or 2 for java
detect_lang() 
{
    java_files=`ls | grep -c .java$`
    if [ $java_files -gt 0 ]; 
    then 
	echo "language: java"
	lang="java"
    else 
	echo "language: c/c++";
	lang="c"
    fi
}

setup() 
{
    if [ ! -d $OUTPUT_DIR ]; 
    then
	mkdir $OUTPUT_DIR
    fi
}

clean()
{
    rm -f ./*.out ./*.err ./*.log
    rm -rf $OUTPUT_DIR
}

main() 
{
setup
detect_lang
echo; echo; 
run_all_tests
clean 
}

main > run-stdout.vmr 2> run-stderr.vmr

