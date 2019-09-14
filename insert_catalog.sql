######################################################################
#
# File      : insert_catalog.sql
#
# Author    : Barry Kimelman
#
# Created   : November 23, 2017
#
# Purpose   : Load records into user table
#
# Notes     : (none)
#
######################################################################

insert into restapi_catalog (
created_date , modified_date , item_name , sku_number , item_price
)
values (
now() , now() , "soap" , "S001" , 300
);

insert into restapi_catalog (
created_date , modified_date , item_name , sku_number , item_price
)
values (
now() , now() , "toothpaste" , "T001" , 250
);

insert into restapi_catalog (
created_date , modified_date , item_name , sku_number , item_price
)
values (
now() , now() , "bread" , "B001" , 175
);
