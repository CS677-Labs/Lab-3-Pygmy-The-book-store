#/bin/bash
set -e
mkdir -p classfiles
function finish {
  echo "Cleanup"
  for i in "${local_pids[@]}"
  do
   kill $i || echo "Failed to kill process $i. It is probably already killed."
   # or do whatever with individual element of the array
  done

#  # For remote cleanup
  while IFS= read -r line
  do
    newline=(${line//=/ })
    id=${newline[0]}
    network=(${newline[1]//,/ })
    url=(${network[0]//:/ })
    ip="${url[0]}:${url[1]}"
    fullurl=$ip
    ip=$(echo "$fullurl" |sed 's/https\?:\/\///')
    ssh -n ec2-user@"$ip" "kill ${pids[id]}" || echo "Failed to kill process $i."
  done < "network-config.properties"
  rm -rf build/* >/dev/null 2>&1
}
trap finish EXIT
trap finish RETURN


servers=("catalog_server", "order_server", "frontend_server")
ports=("5000", "5001", "5002")
machines=()
local_pids=()
pids=()
#
 # Read N - Number of servers. Keep assigning nodes to them - Catalog, Order, and Frontend and run the app accordingly. 
 # Print the url of frontend server. 
 # Run the client and test cases.
echo "Setting up the servers on machines..."
while IFS= read -r line
do
  machines+=($line)
done < machines.txt

for i in ${!servers[@]}; do
  role=${servers[$i]}
  ip=${machines[$i]}
  port=${ports[$i]}
  if [[ "$ip" == *"http://localhost" ]] || [[ "$ip" == *"http://127.0.0.1" ]]
  then
    echo "Running $role on Localhost...."
    export FLASK_APP=src/$role/views.py
    python3 -m flask run --port $port 2>/dev/null &
    pid=$!
    sleep 3
    if ! (ps -ef | grep "python" | grep "$pid_order" | grep -v grep >/dev/null 2>&1)
    then
	    echo "Failed to start $role" && return 1
    fi
    pid=$!
    sleep 3
    ps | grep "python" | grep "$pid" | grep -v grep >/dev/null 2>&1
    status=$?
    local_pids+=($pid)
  else
    echo "Running role $role on remote machine $ip."
    dir[id]="temp_$id"
    ssh -n ec2-user@"$ip" "rm -rf temp_$id && mkdir temp_$id && cd temp_id && git clone https://github.com/CS677-Labs/Lab-2-Pygmy-The-book-store.git || echo \"Repo already present\""
    scp "machines.txt" ec2-user@"$ip":"temp_$id"
    pid=$(ssh -n ec2-user@$ip "cd temp_$id/Lab-2-Pygmy-The-book-store/src/$role && export FLASK_APP=views.py && (python3 -m flask run --port $port 2>/dev/null & echo \$!)")
    sleep 2
    status=0
    ssh -n ec2-user@"$ip" "ps -ef | grep java | grep $pid | grep -v grep" || status=$?
    pids[id]=$pid
  fi
  if [[ "$status" != 0 ]]
  then
	  echo "Failed to start the server $role in machine with ip $ip. Exiting..." && return 1
  fi
done
  
echo "All set for testing...."
echo "---------------------------------------------------------------"
sleep 1
frontend_server="${machines[2]}:${ports[2]}"
testcaseFailed=0

# Run test cases
echo "Test Case 1."
echo "Doing a lookup for id 1. Expecting it to Succeed."

tmpoutput=$(python3 src/cli/main.py $frontend_server lookup 1)
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
tmpoutput=$(python3 src/cli/main.py $frontend_server lookup 5)
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
tmpoutput=$(python3 src/cli/main.py $frontend_server search --topic "distributed systems")
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
tmpoutput=$(python3 src/cli/main.py $frontend_server search --topic "machine learning")
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
tmpoutput=$(python3 src/cli/main.py $frontend_server lookup 2)
if [[ $tmpoutput == *"Failed"* ]] ; then
    echo "Result: Failed to lookup for book with id 2"
    testcaseFailed=1
else
    echo "Result: Success"
fi
echo "---------------------------------------------------------------"
echo "---------------------------------------------------------------"
echo "Test Case 6."
countBefore=$(echo $tmpoutput | sed -n 's/^.*count.:.//p' | awk -F[,] '{print $1}')
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
tmpoutput=$(python3 src/cli/main.py $frontend_server lookup 2)
if [[ $tmpoutput == *"Failed"* ]] ; then
    echo "Result: Failed to lookup for book with id 2"
    testcaseFailed=1
else
    echo "Result: Success"
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
echo "---------------------------------------------------------------"
echo "---------------------------------------------------------------"
if [[ $testcaseFailed == 1 ]] ; then
    echo "Atleast one test case failed"
else
    echo "All test cases succeeded"
fi