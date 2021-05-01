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

## To run the system on AWS EC2 instances
Create a config file. This file should have 3 lines.

1st line will contain comma separated list of servers where catalog server replicas should run.
2nd line will contain comma separated list of servers where order server replicas should run.
3rd line will contain DNS name/IP of server where frontend server should run.

Example :
```
cat config
ec2-52-204-17-35.compute-1.amazonaws.com,ec2-54-146-69-77.compute-1.amazonaws.com,ec2-54-152-5-125.compute-1.amazonaws.com
ec2-54-157-158-136.compute-1.amazonaws.com,ec2-52-23-179-14.compute-1.amazonaws.com,ec2-107-23-14-212.compute-1.amazonaws.com
ec2-54-237-55-198.compute-1.amazonaws.com
```
With the above config file 3 replicas of catalog server will run on servers listed on line 1. 3 replicas of order server will run on servers listed on line 2.
And front end server will run on server on line 3.

Please ensure there is no extra space in between.

Login to a server that has passwordless ssh set up to all the above servers. Clone the repo and do the below :
```
cd Lab-3-Pygmy-The-book-store
bash run.sh config
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
