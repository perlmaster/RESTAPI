######################################################################
#
# File      : create_user.sql
#
# Author    : Barry Kimelman
#
# Created   : November 23, 2017
#
# Purpose   : Create user table
#
# Notes     : (none)
#
######################################################################

create table restapi_user (
	userid						int not null auto_increment,
	created_date			datetime not null,
	modified_date			datetime not null,
	first_name				varchar(80) not null,
	last_name				varchar(80) not null,
	email					varchar(80) not null,
	username				varchar(80) not null,
	password				varchar(80) not null,
	addr_line1				varchar(80) not null,
	addr_line2				varchar(80),
	city					varchar(80) not null,
	state					varchar(80) not null,
	zipcode					varchar(80) not null,
	country					varchar(80) not null,
	phone					varchar(40) not null,
	cell					varchar(40) not null,
	primary key (userid)
);
