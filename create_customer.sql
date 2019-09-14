######################################################################
#
# File      : create_customer.sql
#
# Author    : Barry Kimelman
#
# Created   : November 23, 2017
#
# Purpose   : Create customer table
#
# Notes     : (none)
#
######################################################################

create table restapi_customer (
	id						int not null auto_increment,
	created_date			datetime not null,
	modified_date			datetime not null,
	first_name				varchar(80) not null,
	last_name				varchar(80) not null,
	email					varchar(80) not null,
	addr_line1				varchar(80) not null,
	addr_line2				varchar(80) not null,
	city					varchar(80) not null,
	state					varchar(80) not null,
	zipcode					varchar(80) not null,
	country					varchar(80) not null,
	phone					varchar(40) not null,
	cell					varchar(40) not null,
	primary key (id)
);
