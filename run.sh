#/bin/bash
set -e

servers=("catalog_server" "order_server" "frontend_server")

function finish {
  echo "Cleanup"
  for i in "${local_container_ids[@]}"
  do
   docker stop $i && docker rm $i || echo "Failed to kill container $i. It is probably already killed or something went wrong."
  done

# For remote cleanup
  for i in ${!servers[@]}; do	  
    ips=(${machines[i]//,/ })
    for j in ${!ips[@]}; do
      ip=${ips[j]}  
      if [[ "$ip" != *"host.docker.internal" ]]
      then
        echo "Attempting to cleanup ${servers[$i]} with container id ${container_ids[$i]} on $ip"
        ssh -n ec2-user@"$ip" "docker stop $(docker ps -aq) && docker rm $(docker ps -aq)" || echo "Failed to stop the server $i. It might have already been cleaned before or something went wrong."
      fi
    done
  done
  return
}

trap finish EXIT
trap finish INT

ports=("5000" "5001" "5002")
machines=()
local_container_ids=()
container_ids=()
configFile=$1
 # Read N - Number of servers. Keep assigning nodes to them - Catalog, Order, and Frontend and run the app accordingly. 
 # Print the url of frontend server. 
 # Run the client and test cases.
echo "Setting up the servers on machines..."
while IFS= read -r line || [ -n "$line" ];
do
  machines+=($line)
done < $configFile
for i in ${!servers[@]}; do
  role=${servers[i]}
  ips=(${machines[i]//,/ })
  port_offset=${ports[$i]}
  for j in ${!ips[@]}; do
    port=$((port_offset+j*3))
    echo $port
    ip=${ips[j]}
    if [[ "$ip" == *"host.docker.internal" ]] || [[ "$ip" == *"127.0.0.1" ]]
    then
      echo "Running $role on Localhost...."
      docker load < docker/${role}.tar.gz
      if [[ "$role" == "frontend_server" ]]
      then
        container_id=$(docker run -v $(pwd)/$configFile:/app/config -d -p $port:$port $role --host=0.0.0.0 --port $port)
      else
        container_id=$(docker run -v $(pwd)/$configFile:/app/config -d -p $port:$port $role $j)
      fi
      sleep 3
      status=0
      docker ps | grep $role | grep "${container_id:0:10}" | grep -v grep >/dev/null 2>&1 || status=$?
      local_container_ids+=($container_id)
      else
        echo "Running role $role on remote machine $ip."
        dir[$i]="temp_$i"
        ssh -n ec2-user@"$ip" "rm -rf temp_$i && mkdir temp_$i && cd temp_$i && git clone https://github.com/CS677-Labs/Lab-3-Pygmy-The-book-store 1>/dev/null 2>&1  || echo \"Repo already present\""
        scp $configFile  ec2-user@"$ip":"temp_$i/Lab-3-Pygmy-The-book-store/src/$role/config" >/dev/null 2>&1
        if [[ "$role" == "frontend_server" ]]
        then
            container_id=$(ssh -n ec2-user@$ip "cd temp_$i/Lab-3-Pygmy-The-book-store && docker load docker/${role}.tar.gz && docker cp -f $configFile ${role}:/config && (docker run -v $(pwd)/$configFile:/app/config -d -p $port:$port $role --host=0.0.0.0 --port $port && echo \$!)")
        else
            container_id=$(ssh -n ec2-user@$ip "cd temp_$i/Lab-3-Pygmy-The-book-store && docker load docker/${role}.tar.gz && docker cp -f $configFile ${role}:/config && (docker run -v $(pwd)/$configFile:/app/config -d -p $port:$port $role $j && echo \$!)")
        fi
        sleep 3
        status=0
        ssh -n ec2-user@"$ip" "docker ps | grep $role | grep -v grep >/dev/null 2>&1" || status=$?
        container_ids[i]=$container_id
      fi
      if [[ "$status" != 0 ]]
      then
        echo "Failed to start the server $role in machine with ip $ip. Exiting..." && exit 1
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