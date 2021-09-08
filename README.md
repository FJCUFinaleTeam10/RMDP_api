# RMDP_api
## Install
Open the terminal and move to the directory of this project,

    $ cd [project_path]

    $ cd RMDP_api 

and type

    $ docker-compose up

##API - data
###Driver data 
###get all driver

    POST /driver/getalldriver/ 

###Response

    {
        "id": "6134398187af41afea62f825",
        "Capacity": 0,
        "City": "Agra",
        "Country_Code": 1,
        "Latitude": 27.220141110852705,
        "Longitude": 78.0062402670762,
        "Route": [],
        "Velocity": 0
    },
    {
        "id": "6134398187af41afea62f826",
        "Capacity": 0,
        "City": "Agra",
        "Country_Code": 1,
        "Latitude": 27.215615345970964,
        "Longitude": 78.04961345045498,
        "Route": [],
        "Velocity": 0
    },...

###get city driver

    POST /driver/getdriverbaseoncity/


