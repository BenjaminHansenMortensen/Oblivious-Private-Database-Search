# Oblivious Private Database Search

Welcome to the Oblivious Private Database Search repository which implements an adaptive Oblivious Transfer with access control between
a user and a mock passenger list register ([Kapittel 60. PNR-registeret](https://lovdata.no/dokument/SF/forskrift/2013-09-20-1097/kap60#kap60)). The implementation supports two types of searches on the PNR records
and is meant to demonstrate their practicability. One type of searching is a classical search query which checks 
whether the user's input matches any attribute in the records. The second type is a semantic search which uses Large Language Models 
to embedd the records and the user's input, then calculates their distance. Close vector embeddings imply semantic likeness.

## MP-SPDZ Setup

To get started we need to [download MP-SPDZ](https://github.com/data61/MP-SPDZ/releases). It is recommended to do so on an Ubuntu system, and
I recommend MP-SPDZ version 0.3.8. After having unpacked it we want to set up a few things by executing the following commands
from the top folder.

Fetch the mpc protocols (note that the application uses "semi-party.x" by default so all other files fetched by running this command can be removed if desired):
```
Scripts/tldr.sh
```

Create keys and certificates for communication, this step requires openssl (notes that these keys and certificate expire so this step might need to be redone at a later time):
```
Scripts/setup-ssl.sh
```

Fetch circuits (note that the application only uses the "aes_128.txt" by default):
```
make Programs/Circuits
```

## Oblivious Private Database Search setup

To set up and run the application it requires pip and Python version 3.10 or greater. You can clone the repository to wherever you desired,
but we need to tell it where MP-SPDZ is located. From the top folder in MP-SPDZ run:
```
python -c "import pathlib;print(f'Path(\'{pathlib.Path.cwd()}\')')"
```

This will print out a python Path object which you should copy and set as the value of the variable "mp_spdz_directory" located at the bottom of the /ObliviousPrivateDatabaseSearch/src/application/getters.py
file. An end result example could look something like this "mp_spdz_directory = Path('/home/username/mp-spdz-0.3.8')".

Next, from the top folder /ObliviousPrivateDatabaseSearch/ we install the application by executing:
```
pip install -e .
```

Now that we have installed the application it provides us with three commands that can be ran from anywhere on the system. To create the internal folders of the application, moves over the scripts and circuits to MP_SPDZ and compile the scripts we run:

```
opds_setup
```
Which only has needs to be done once.

To run the application simply run the server and client:
```
opds_client
```
```
opds_server
```
The retrieved PNR records from the server are stored in the /ObliviousPrivateDatabaseSearch/src/application/Client/Retrieved_Records/ folder.

Proper use of the application is to shut down the client by typing "exit" when prompted for a search query. The server will automatically shut down when the client does.

## Cross System Setup

It is also possible to run the server and client on different systems. To do this follow the steps above on the second system but instead of creating 
new keys and certificates you want to copy those from the first system. Making it so that the two systems hold the same set of keys and certificates 
for the parties. They can be located in MP-SPDZ in the "Player-Data" folder, and are named "P0.key", "P0.pem", "P1.key", "P1.pem", "P2.key", "P2.pem", "P3.key" and "P3.pem".

Lastly, in the /ObliviousPrivateDatabaseSearch/src/application/getters.py you want to change the "server_ip" and "client_ip" variables to the IPs (as a string) of the two systems.
The port numbers can be left alone.

Now you can simply run 
```
opds_client
```
on the one system corresponding with the client_ip 
and 
```
opds_server
```
on the one corresponding with the server_ip.
