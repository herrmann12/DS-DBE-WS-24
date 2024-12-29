# DS-DBE-WS-24

## Overview
This is the code for the Distributed Systemes Project WS2024 from Group 08. Herby, a distributed system has been created, that allows users to vote in an election while securing that there is always a server running as the leader. The leader is responsible for handling the voting process and taking the registration for election, the vote and to close the voting.

## Getting started
Download all files from vote_system. You can run all the files in the Terminal / Command Center or conda or anything else you might prefer. Watch out, that when using Terminal / Command Center you have to install psutil manually upfront. For conda this installation is not necessary due to the environment.

## Starting the server
To start the server it is neccesary to give the port number that has to be used. This argument is necessary for the server running. If the port is already used, the server cannot start. The IP of your Laptop will be identified and used automatically. 

If your laptop is the first one to start the server in your network, you will be the leader. After this server is stopped, one of the other servers will take over. Therefore the LCR Algorithm will be used and the server with the highest id will be the new leader. Usually, this should be the newest server.

## Registering the election
In order to vote, the election has to be registered first of all. For this, it is necessary to give an election id (id), the candidates (candidates) and autorized users (authorized_users) as arguments to the execution of the file. If the election id has already been used, an error saying that the id already exists will occur.

The registration is only allowed to the admin and therefore the leader, as otherwise anyone could enter candidates to vote on or make themselves an authorized user.

## Voting
For voting, you need the unique id (id), which was the value of the argument (authorized_users) in the register.py file. For canidate (candidate) provide a Name that has been provided in the registration of the election and for the election id (election_id) proivde the corresponding election id (id) from the registration. All arguments will be checked and if not valid, the vote will not be counted.

## Closing Election
Once everyone has voted or the time therefore passed up, the voting will come to an end. As an argument, the id of the election has to be provided. Once again, this can only be done by the admin and therefore the leader. With the end of an election, the winner will be shown to the leader.
