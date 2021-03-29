# Setting up
pip install virtualenv 2>/dev/null >/dev/null
virtualenv .venv 2>/dev/null >/dev/null
pip install -r src/catalog_server/requirements.txt 2>/dev/null >/dev/null
export FLASK_APP=src/catalog_server/views.py
python3 -m flask run --port 5000 2>/dev/null >/dev/null &
pidForCatalog=$!
export FLASK_APP=src/order_server/order_server.py
python3 -m flask run --port 5001 2>/dev/null >/dev/null &
pidForOrder=$!
export FLASK_APP=src/frontend_server/frontend.py 
python3 -m flask run --port 5002 2>/dev/null >/dev/null &
pidForFrontend=$!

sleep 10

echo "Catalog, order and frontend servers are up and running"
testcaseFailed=0

# Run test cases
echo "Doing a lookup for id 1. Expected result - Success"

tmpoutput=$(python3 src/cli/main.py lookup 1)
if [[ $tmpoutput == *"Failed"* ]] ; then
    echo "      Failed to lookup for book with id 1"
    testcaseFailed=1
else
    echo "      Success"
fi
echo
echo
echo "Doing a lookup for id 5. Expected result - Failure"
tmpoutput=$(python3 src/cli/main.py lookup 5)
if [[ $tmpoutput == *"Failed"* ]] ; then
    echo "      Failed to lookup for book with id 5"
else
    echo "      Success"
    testcaseFailed=1
fi
echo
echo
echo "Searching for topic 'distributed systems'. Expected result - Success"
tmpoutput=$(python3 src/cli/main.py search --topic "distributed systems")
if [[ $tmpoutput == *"title"* ]] ; then
    echo "      Success"
else
    echo "      Failed to find a book for topic 'distributed systems'"
    testcaseFailed=1
fi
echo
echo
echo "Searching for topic 'machine learning'. Expected result - Failure"
tmpoutput=$(python3 src/cli/main.py search --topic "machine learning")
if [[ $tmpoutput == *"title"* ]] ; then
    echo "      Success"
    testcaseFailed=1
else
    echo "      Failed to find a book for topic 'machine learning'"
fi
echo
echo
echo "Looking up book with ID 2"
tmpoutput=$(python3 src/cli/main.py lookup 2)
if [[ $tmpoutput == *"Failed"* ]] ; then
    echo "      Failed to lookup for book with id 2"
    testcaseFailed=1
else
    echo "      Success"
fi
countBefore=$(echo $tmpoutput | sed -n 's/^.*count.:.//p' | awk -F[,] '{print $1}')
echo "Current count - $countBefore"
echo "Attempting to buy this book"
tmpoutput=$(python3 src/cli/main.py buy 2)
if [[ $tmpoutput == *"Hooray"* ]] ; then
    echo "      Success"
else
    echo "      Failed to buy"
    testcaseFailed=1
fi
echo "Looking up book with ID 2"
tmpoutput=$(python3 src/cli/main.py lookup 2)
if [[ $tmpoutput == *"Failed"* ]] ; then
    echo "      Failed to lookup for book with id 2"
    testcaseFailed=1
else
    echo "      Success"
fi
countAfter=$(echo $tmpoutput | sed -n 's/^.*count.:.//p' | awk -F[,] '{print $1}')
echo "Count after buy - $countAfter"

diff=$(($countBefore - $countAfter))
if [[ $diff == 1 ]] ; then
    echo "Count has been updated as expected"
else
    echo "Count not updated as expected"
    testcaseFailed=1
fi
echo
echo
if [[ $testcaseFailed == 1 ]] ; then
    echo "Atleast one test case failed"
else
    echo "All test cases succeeded"
fi

kill $pidForCatalog $pidForFrontend $pidForOrder
