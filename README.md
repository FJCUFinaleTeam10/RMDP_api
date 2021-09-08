# RMDP_api
## Install
Open the terminal and move to the directory of this project,

    $ cd [project_path]

    $ cd RMDP_api 

and type

    $ docker-compose up

##API - get data
###Driver data 
###get all driver

    POST /driver/getalldriver/ 


###get city driver

    POST /driver/getdriverbaseoncity/


###Geolaction data
###get cities of desginated country
    
    POST /geolocation/getcity/

###get all countries

    GET /geolocation/getallcountrycode/

###get all cities

    GET /geolocation/getallcities/

###Menu data
###get all menu

    POST /menu/getMenu/ 