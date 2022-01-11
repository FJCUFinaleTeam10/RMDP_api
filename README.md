Requirement
- OS: ubuntu latest version
- docker: 20.10.7
  1) install docker
     $ sudo apt install docker.io
  2) clone the repository
     -$ git clone git@github.com:FJCUFinaleTeam10/RMDP_api.git
  3) run the below command as root users
  Warning : this is demo component of RMDP_api project , please delete all previous image before installation
    $ docker rm -vf $(docker ps -aq)
    $ docker rmi -f $(docker images -aq)
  
    $ cd RMDP_api
    $ pip install virtualenv
    $ virtualenv venv
    $ source venv/bin/activate
    $ docker-compose up -d



