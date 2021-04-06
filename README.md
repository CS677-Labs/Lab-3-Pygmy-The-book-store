# Lab-2-Pygmy-The-book-store
World's smallest book store with a two-tier web design

**Team members**: 
  * Vignesh Radhakrishna (32577580, vradhakrishn@umass.edu)
  * Adarsh Kolya (33018261, akolya@umass.edu)
  * Brinda Murulidhara (32578418, bmurulidhara@umass.edu)

**Milestones**
- Milestone 1 - https://github.com/CS677-Labs/Lab-1-The_Bazaar/tree/milestone1
- Milestone 2 - https://github.com/CS677-Labs/Lab-1-The_Bazaar/tree/milestone2


## Run testcases for Single server, single client usecase
```
cd Lab-2-Pygmy-The-book-store
chmod 777 test/SingleServerSingleClient.sh
bash test/SingleServerSingleClient.sh
```

## Run testcases for Single server, multi client usecase
```
cd Lab-2-Pygmy-The-book-store
chmod 777 test/SingleServerMultiClients.sh
bash test/SingleServerMultiClients.sh
```

## Run testcases for Multi server, multi client usecase
Create a file "machines.txt" with 3 lines. 
First line has the IP of the server where catalog server is to be launched.
Second line has the IP of the server where order server is to be launched.
Third line has the IP of the server where frontend server is to be launched.
```
cd Lab-2-Pygmy-The-book-store
chmod 777 test/MultiServerMultiClients.sh
bash test/MultiServerMultiClients.sh machines.txt
```

## Usage
### Running the servers
```
pip install virtualenv
virtualenv .venv

#For linux based
source .venv/bin/activate
#For windows based
.venv/scripts/activate.bat

pip install -r src/requirements.txt
```
### Setup the servers on either localhost or multiple machines
#### Create a txt file with any name and store three lines for the machine addresses for catalog, order and frontend servers respectively. For running the entire system on your localhost, use machines.txt.local.
```
bash run.sh machines.txt.local
```

### CLI
Open a new shell
```
cd LAB-2-PYGMY-THE-BOOK-STORE
#For linux based
source .venv/bin/activate
#For windows based
.venv/scripts/activate.bat

cd src/cli
```
#### Lookup 
```
python main.py --frontend_server <ip_of_frontend_server> lookup <item number>
```

--frontend_server is optional. If not provided, it takes localhost as default.

Example
```
python main.py --frontend_server --frontend_server ec2-35-175-129-185.compute-1.amazonaws.com lookup 1
```

#### Search
```
python main.py --frontend_server <ip_of_frontend_server> search --topic "<topic>"
```

Example
```
python main.py search --topic "distributed systems"
```

#### Buy
```
python main.py --frontend_server <ip_of_frontend_server> buy <item number>
```

Example
```
python main.py buy 1
```
