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
  for i in ${!servers[@]}; do	    
    ip=${machines[$i]}
    if [[ "$ip" != *"localhost" ]]
    then
    	echo "Attempting to cleanup ${servers[$i]} with PID ${pids[$i]} on $ip"
    	ssh -n ec2-user@"$ip" "kill -9 ${pids[$i]}" || echo "Failed to kill process $i."
    fi
  done
  return
}
trap finish EXIT
trap finish INT

servers=("catalog_server" "order_server" "frontend_server")
ports=("5000" "5001" "5002")
machines=()
local_pids=()
pids=()
configFile=$1
echo $configFile
 # Read N - Number of servers. Keep assigning nodes to them - Catalog, Order, and Frontend and run the app accordingly. 
 # Print the url of frontend server. 
 # Run the client and test cases.
echo "Setting up the servers on machines..."
while IFS= read -r line
do
  machines+=($line)
done < $configFile

for i in ${!servers[@]}; do
  role=${servers[i]}
  ips=(${machines[i]//,/ })
  port_offset=${ports[$i]}
  for j in ${!ips[@]}; do
    port=$((port_offset+j%3))
    ip=${ips[j]}
    if [[ "$ip" == *"localhost" ]] || [[ "$ip" == *"127.0.0.1" ]]
    then
      echo "Running $role on Localhost...."
      docker load < images/${role}.tar.gz
      docker cp -f $configFile ${role}:/config
      docker run -p $port:$port $role --host=0.0.0.0 --port $port >/dev/null 2>&1 &
      pid=$!
      sleep 3
      if ! (ps -ef | grep "python" | grep "$pid" | grep -v grep >/dev/null 2>&1)
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
        ssh -n ec2-user@"$ip" "rm -rf temp_$i && mkdir temp_$i && cd temp_$i && git clone https://github.com/CS677-Labs/Lab-3-Pygmy-The-book-store 1>/dev/null 2>&1  || echo \"Repo already present\""
        scp $configFile  ec2-user@"$ip":"temp_$i/Lab-3-Pygmy-The-book-store/src/$role/config" >/dev/null 2>&1
        pid=$(ssh -n ec2-user@$ip "cd temp_$i/Lab-3-Pygmy-The-book-store && docker load images/${role}.tar.gz && docker cp -f $configFile ${role}:/config && (docker run -p $port:$port $role --host=0.0.0.0 --port $port >/dev/null 2>&1 & echo \$!)")
        echo $pid
        sleep 2
        status=0
        ssh -n ec2-user@"$ip" "docker ps | grep $role | grep -v grep >/dev/null 2>&1" || status=$?
        pids[i]=$pid
      fi
      if [[ "$status" != 0 ]]
      then
        echo "Failed to start the server $role in machine with ip $ip. Exiting..." && return 1
      fi
  done
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
