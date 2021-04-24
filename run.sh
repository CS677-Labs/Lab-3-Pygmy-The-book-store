#/bin/bash
set -e

servers=("catalog_server" "order_server" "frontend_server")

function finish {
  echo "Cleanup"
  for i in "${local_container_names[@]}"
  do
   docker stop $i && docker rm $i || echo "Failed to kill container $i. It is probably already killed or something went wrong."
  done

# For remote cleanup
  for i in ${!servers[@]}; do	  
    ips=(${machines[i]//,/ })
    for j in ${!ips[@]}; do
      ip=${ips[j]}  
      if [[ "$ip" != *"host.docker.internal"* ]] && [[ "$ip" != *"localhost"* ]]
      then
        echo "Attempting to cleanup remote server $ip"
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
local_container_names=()
container_names=()
 if [[ "$1" == "" ]]
 then
  if [[ "$OSTYPE" == *"linux"* ]]
  then
    configFile="machines.txt.local.linux"
  else
    configFile="machines.txt.local"
  fi
  echo "No file passed as parameter. Using the default localhost file $configFile."
 else
  configFile=$1
 fi
frontend_port=""
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
    ip=${ips[j]}
    container_name=${role}_$j
    if [[ "$ip" == *"host.docker.internal"* ]] || [[ "$ip" == *"localhost"* ]]
    then
      echo "Running $role on Localhost...."
      docker load < docker/${role}.tar.gz
      
      if [[ "$role" == "frontend_server" ]]
      then
        frontend_port=$port
        if [[ "$OSTYPE" == "msys" ]]
        then
          docker run -v $(pwd -W)/$configFile:/app/config -d -p $port:$port --name $container_name $role --host=0.0.0.0 --port $port
        else
          docker run -v $(pwd)/$configFile:/app/config -d -p $port:$port --name $container_name --net=host $role --host=0.0.0.0 --port $port
        fi

      else
        if [[ "$OSTYPE" == "msys" ]]
        then
          docker run -v $(pwd -W)/$configFile:/app/config -d -p $port:$port --name $container_name $role $j
        else
          docker run -v $(pwd)/$configFile:/app/config -d -p $port:$port --name $container_name --net=host $role $j
        fi
      fi
      sleep 3
      status=0
      docker ps | grep "$container_name" | grep -v grep >/dev/null 2>&1 || status=$?
      local_container_names+=($container_name)
    else
      echo "Running role $role on remote machine $ip."
      dir[$i]="temp_$i"
      ssh -n ec2-user@"$ip" "rm -rf temp_$i && mkdir temp_$i && cd temp_$i && git clone https://github.com/CS677-Labs/Lab-3-Pygmy-The-book-store 1>/dev/null 2>&1  || echo \"Repo already present\""
      scp $configFile  ec2-user@"$ip":"temp_$i/Lab-3-Pygmy-The-book-store/src/$role/config" >/dev/null 2>&1
      if [[ "$role" == "frontend_server" ]]
      then
          ssh -n ec2-user@$ip "cd temp_$i/Lab-3-Pygmy-The-book-store && docker load docker/${role}.tar.gz && docker cp -f $configFile ${role}:/config && (docker run -v $(pwd)/$configFile:/app/config -d -p $port:$port --name $container_name $role --host=0.0.0.0 --port $port"
      else
          ssh -n ec2-user@$ip "cd temp_$i/Lab-3-Pygmy-The-book-store && docker load docker/${role}.tar.gz && docker cp -f $configFile ${role}:/config && (docker run -v $(pwd)/$configFile:/app/config -d -p $port:$port --name $container_name $role $j"
      fi
      sleep 3
      status=0
      ssh -n ec2-user@"$ip" "docker ps | grep $container_name | grep -v grep >/dev/null 2>&1" || status=$?
      container_names[i]=$container_name
    fi
    if [[ "$status" != 0 ]]
    then
      echo "Failed to start the server $role in machine with ip $ip. Exiting..." && exit 1
    fi
  done
done

if [[ "$ip" == *"host.docker.internal"* ]] || [[ "$ip" == *"localhost"* ]]
then
  echo "Frontend server is running on localhost .... Pass this to the CLI to use it with this server."
else
  echo "Frontend server is running on ${machines[2]}.... Pass this to the CLI to use it with this server."
fi

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