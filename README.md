# Lab-2-Pygmy-The-book-store
World's smallest book store with a two-tier web design

**Team members**: 
  * Vignesh Radhakrishna (32577580, vradhakrishn@umass.edu)
  * Adarsh Kolya (33018261, akolya@umass.edu)
  * Brinda Murulidhara (32578418, bmurulidhara@umass.edu)

**Milestones**
- Milestone 1 - https://github.com/CS677-Labs/Lab-1-The_Bazaar/tree/milestone1


## Run testcases for Single server, single client usecase
```
cd Lab-2-Pygmy-The-book-store
chmod 777 test/SingleServerSingleClient.sh
bash test/SingleServerSingleClient.sh
```

## Run testcases for Multi server, single client usecase
Create a file "machines.txt" with 3 lines. 
First line has the IP of the server where catalog server is to be launched.
Second line has the IP of the server where order server is to be launched.
Third line has the IP of the server where frontend server is to be launched.
```
cd Lab-2-Pygmy-The-book-store
chmod 777 test/MultiServerSingleClient.sh
bash test/MultiServerSingleClient.sh machines.txt
```

## Usage
### Running the servers on localhost
```
pip install virtualenv
virtualenv .venv
```
#### Catalog server
```
#For linux based
source .venv/bin/activate
#For windows based
.venv/scripts/activate.bat

pip install -r src/catalog_server/requirements.txt

export FLASK_APP=src/catalog_server/views.py
python -m flask run --port 5000
```

### Order server
Open a new shell
```
cd LAB-2-PYGMY-THE-BOOK-STORE
#For linux based
source .venv/bin/activate
#For windows based
.venv/scripts/activate.bat

export FLASK_APP=src/order_server/order_server.py
python -m flask run --port 5001
```

### Frontend server
Open a new shell
```
cd LAB-2-PYGMY-THE-BOOK-STORE
#For linux based
source .venv/bin/activate
#For windows based
.venv/scripts/activate.bat

export FLASK_APP=src/frontend_server/frontend.py
python -m flask run --port 5002
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
python main.py lookup <item number>
```

Example
```
python main.py lookup 1
```

#### Search
```
python main.py search --topic "<topic>"
```

Example
```
python main.py search --topic "distributed systems"
```

#### Buy
```
python main.py buy <item number>
```

Example
```
python main.py buy 1
```
