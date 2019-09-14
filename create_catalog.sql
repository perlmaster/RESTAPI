######################################################################
#
# File      : create_catalog.sql
#
# Author    : Barry Kimelman
#
# Created   : November 23, 2017
#
# Purpose   : Create catalog table
#
# Notes     : (none)
#
######################################################################

create table restapi_catalog (
	id						int not null auto_increment,
	created_date			datetime not null,
	modified_date			datetime not null,
	item_name				varchar(124) not null,
	sku_number				varchar(80) not null,
	item_price				int not null , # item price in pennies
	primary key (id)
);
