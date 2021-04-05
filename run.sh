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


servers=("catalog_server" "order_server" "frontend_server")
ports=("5000" "5001" "5002")
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
    dir[$i]="temp_$i"
    ssh -n ec2-user@"$ip" "rm -rf temp_$i && mkdir temp_$i && cd temp_$i && git clone https://github.com/CS677-Labs/Lab-2-Pygmy-The-book-store 1>/dev/null 2>&1  && cd L* && git checkout feature/multi-servers-2 1>/dev/null 2>&1 || echo \"Repo already present\""
    scp "machines.txt" ec2-user@"$ip":"temp_$i/Lab-2-Pygmy-The-book-store/src/$role/"
    pid=$(ssh -n ec2-user@$ip "sudo pip3 install -r temp_$i/Lab-2-Pygmy-The-book-store/requirements.txt 1>/dev/null 2>&1  && cd temp_$i/Lab-2-Pygmy-The-book-store/src/$role && export FLASK_APP=views.py && (python3 -m flask run --host 0.0.0.0 --port $port 1>/dev/null 2>&1 & echo \$!)")
    echo $pid
    sleep 2
    status=0
    ssh -n ec2-user@"$ip" "ps -ef | grep python | grep $pid | grep -v grep" || status=$?
    pids[i]=$pid
  fi
  if [[ "$status" != 0 ]]
  then
	  echo "Failed to start the server $role in machine with ip $ip. Exiting..." && return 1
  fi
done
echo "Frontend server is running on ${machines[2]}.... Pass this to the CLI to use it with this server."

echo "Press 'q' to exit"
count=0
while : ; do
read k
if [[ "$k" == "q" ]]
then
  echo "Quitting the program"
  exit
fi
done
echo "---------------------------------------------------------------"
