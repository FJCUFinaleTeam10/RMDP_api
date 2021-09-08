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
###get designated restaurant menu

    POST /menu/getMenuBaseOnRestaurant/

###Order data
###get all order
    
    GET /order/listAll/

###create an order

    POST /order/createOrder/

###Restaurant data
###get all restaurant data

    POST /restaurant/getallrestaurantlist/

###get restaurant of city or all restaurant

    POST /restaurant/getrestaurantlist/

###get restaurant of city

    POST /restaurant/getrestaurantbaseoncity/

###get restaurant by using restaurant id

    POST /restaurant/getrestaurantbaseonid/