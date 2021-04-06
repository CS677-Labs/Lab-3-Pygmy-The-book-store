#/bin/bash
set -e
function finish {
  echo "Cleanup"
  echo "q" > /tmp/run_inp
  rm /tmp/run_inp
  sleep 3
}
trap finish EXIT
trap finish RETURN
echo "---------------------------------------------------------------"
echo "Setting up the test environment... Will take 20 seconds"
# Setting up
rm /tmp/run_inp 2>/dev/null 1>&2 || echo "Failed to remove fifo file. Soft error."
mkfifo /tmp/run_inp
tail -f /tmp/run_inp | bash run.sh "machines.txt.local" 1>/dev/null 2>&1 &
sleep 15
if ! (ps -ef | grep "run.sh" | grep -v grep >/dev/null 2>&1)
    then
	    echo "Failed to setup the servers...." && return 1
fi
echo "All set for testing...."
echo "---------------------------------------------------------------"
sleep 1

testcaseFailed=0

# Run test cases
echo "Test Case 1."
echo "Doing a lookup for id 1. Expecting it to Succeed."

tmpoutput=$(python3 src/cli/main.py localhost lookup 1)
if [[ $tmpoutput == *"Failed"* ]] ; then
    echo "Result: Failed to lookup for book with id 1"
    testcaseFailed=1
else
    echo "Result: Success"
fi
echo "---------------------------------------------------------------"
echo "---------------------------------------------------------------"
echo "Test Case 2."
echo "Doing a lookup for id 5. Expecting it to fail."
tmpoutput=$(python3 src/cli/main.py localhost lookup 5)
if [[ $tmpoutput == *"Failed"* ]] ; then
    echo "Result: Failed to lookup for book with id 5, as excepted."
else
    echo "Result: Success"
    testcaseFailed=1
fi
echo "---------------------------------------------------------------"
echo "---------------------------------------------------------------"
echo "Test Case 3."
echo "Searching for topic 'distributed systems'. Expected it to succeed."
tmpoutput=$(python3 src/cli/main.py localhost search --topic "distributed systems")
if [[ $tmpoutput == *"title"* ]] ; then
    echo "Result: Success"
else
    echo "Result: Failed to find a book for topic 'distributed systems'"
    testcaseFailed=1
fi
echo "---------------------------------------------------------------"
echo "---------------------------------------------------------------"
echo "Test Case 4."
echo "Searching for topic 'machine learning'. Expecting it to fail."
tmpoutput=$(python3 src/cli/main.py localhost search --topic "machine learning")
if [[ $tmpoutput == *"title"* ]] ; then
    echo "Result: Success"
    testcaseFailed=1
else
    echo "Result: Failed to find a book for topic 'machine learning', as excepted."
fi
echo "---------------------------------------------------------------"
echo "---------------------------------------------------------------"
echo "Test Case 5."
echo "Looking up book with ID 2. Excepting it to succeed."
tmpoutput=$(python3 src/cli/main.py localhost lookup 2)
if [[ $tmpoutput == *"Failed"* ]] ; then
    echo "Result: Failed to lookup for book with id 2"
    testcaseFailed=1
else
    echo "Result: Success"
fi
echo "---------------------------------------------------------------"
echo "---------------------------------------------------------------"
echo "Test Case 6."
countBefore=$(echo $tmpoutput | sed -n 's/^.*count.:.//p' | awk -F[,}] '{print $1}')
echo "Current count of the - $countBefore"
echo "Attempting to buy this book. Expecting it to succeed."
tmpoutput=$(python3 src/cli/main.py localhost buy 2)
if [[ $tmpoutput == *"Hooray"* ]] ; then
    echo "Result: Success"
else
    echo "Result: Failed to buy the book."
    testcaseFailed=1
fi
echo "Looking up book with ID 2. Expecting it to succeed.". 
tmpoutput=$(python3 src/cli/main.py localhost lookup 2)
if [[ $tmpoutput == *"Failed"* ]] ; then
    echo "Result: Failed to lookup for book with id 2"
    testcaseFailed=1
else
    echo "Result: Success"
fi
countAfter=$(echo $tmpoutput | sed -n 's/^.*count.:.//p' | awk -F[,}] '{print $1}')
echo "Count after buy - $countAfter"

diff=$(($countBefore - $countAfter))
if [[ $diff == 1 ]] ; then
    echo "Count has been updated as expected"
else
    echo "Count not updated as expected"
    testcaseFailed=1
fi
echo "---------------------------------------------------------------"
echo "---------------------------------------------------------------"
if [[ $testcaseFailed == 1 ]] ; then
    echo "Atleast one test case failed"
else
    echo "All test cases succeeded"
fi
