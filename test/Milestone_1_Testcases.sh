#/bin/bash
set -e
function finish {
  echo "Cleanup"
  kill $pid_catalog $pid_order $pid_frontend >/dev/null 2>&1 || echo "Failed killing some or all the servers."
}
trap finish EXIT
trap finish RETURN
echo "---------------------------------------------------------------"
# Setting up
echo "Setting up the test environment..."
pip install virtualenv 2>/dev/null >/dev/null
virtualenv .venv 2>/dev/null >/dev/null

pip install -r src/catalog_server/requirements.txt 2>/dev/null >/dev/null

# Run catalog server and validate if it's running successfully.
echo "  Starting catalog server..."
export FLASK_APP=src/catalog_server/views.py
python3 -m flask run --port 5000 2>/dev/null >/dev/null &
pid_catalog=$!
sleep 3
if ! (ps | grep "python" | grep "$pid_catalog" | grep -v grep >/dev/null 2>&1)
then
	echo "Failed to start the catalog server" && return 1
fi


# Run order server and validate if it's running successfully.
echo "  Starting order server..."
export FLASK_APP=src/order_server/order_server.py
python3 -m flask run --port 5001 2>/dev/null >/dev/null &
pid_order=$!
sleep 3
if ! (ps | grep "python" | grep "$pid_order" | grep -v grep >/dev/null 2>&1)
then
	echo "Failed to start the order server" && return 1
fi


# Run frontend server and validate if it's running successfully.
echo "  Starting frontend server..."
export FLASK_APP=src/frontend_server/frontend.py 
python3 -m flask run --port 5002 2>/dev/null >/dev/null &
pid_frontend=$!
sleep 3
if ! (ps | grep "python" | grep "$pid_frontend" | grep -v grep >/dev/null 2>&1)
then
	echo "Failed to start the frontend server" && return 1
fi

echo "All set for testing...."
echo "---------------------------------------------------------------"
sleep 1

testcaseFailed=0

# Run test cases
echo "Test Case 1."
echo "Doing a lookup for id 1. Expecting it to Succeed."

tmpoutput=$(python3 src/cli/main.py lookup 1)
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
tmpoutput=$(python3 src/cli/main.py lookup 5)
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
tmpoutput=$(python3 src/cli/main.py search --topic "distributed systems")
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
tmpoutput=$(python3 src/cli/main.py search --topic "machine learning")
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
tmpoutput=$(python3 src/cli/main.py lookup 2)
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
tmpoutput=$(python3 src/cli/main.py buy 2)
if [[ $tmpoutput == *"Hooray"* ]] ; then
    echo "Result: Success"
else
    echo "Result: Failed to buy the book."
    testcaseFailed=1
fi
echo "Looking up book with ID 2. Expecting it to succeed.". 
tmpoutput=$(python3 src/cli/main.py lookup 2)
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
