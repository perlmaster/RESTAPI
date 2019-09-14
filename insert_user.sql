######################################################################
#
# File      : insert_user.sql
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

insert into restapi_user (
created_date , modified_date , first_name , last_name , email , username , password ,
addr_line1 , city , state , zipcode , country , phone , cell
)
values (
now() , now() , "fred" , "smith" , "fred@oz.com" , "freddy" , "foobar" ,
"123 main street" , "memphis" , "tn" , "12345" , "usa" , "9017777777" , "9018888888"
);

insert into restapi_user (
created_date , modified_date , first_name , last_name , email , username , password ,
addr_line1 , city , state , zipcode , country , phone , cell
)
values (
now() , now() , "john" , "doe" , "jdoe@oz.com" , "jdoe" , "snafu" ,
"456 somewhere lane" , "atlanta" , "ga" , "12345" , "usa" , "7387777777" , "7388888888"
);
