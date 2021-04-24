# Lab-3-Pygmy-The-book-store
World's smallest book store with a two-tier web design

**Team members**: 
  * Vignesh Radhakrishna (32577580, vradhakrishn@umass.edu)
  * Adarsh Kolya (33018261, akolya@umass.edu)
  * Brinda Murulidhara (32578418, bmurulidhara@umass.edu)

**Milestones**
- Milestone 1 - https://github.com/CS677-Labs/Lab-3-Pygmy-The-book-store/tree/milestone1

## Run 2 catalog servers, 2 order servers and 1 frontend server on localhost
```
cd Lab-3-Pygmy-The-book-store
bash run.sh
```

## Usage
### CLI
Open a new shell
```
cd LAB-3-PYGMY-THE-BOOK-STORE
#For linux based
pip install virtualenv
virtualenv .venv
source .venv/bin/activate

pip install -r src/requirements.txt
source .venv/bin/activate

cd src/cli
```
#### Lookup 
```
python main.py --frontend_server <ip_of_frontend_server> lookup <item number>
```

--frontend_server is optional. If not provided, it takes localhost as default.

Example
```
python main.py --frontend_server ec2-35-175-129-185.compute-1.amazonaws.com lookup 1
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
