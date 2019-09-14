######################################################################
#
# File      : create_commands.sql
#
# Author    : Barry Kimelman
#
# Created   : August 21, 2019
#
# Purpose   : Create commands tracking table
#
# Notes     : (none)
#
######################################################################

create table restapi_commands (
	id						int not null auto_increment,
	cmd_date				datetime not null,
	userid					int not null ,
	cmd						varchar(40) not null,
	primary key (id)
);
