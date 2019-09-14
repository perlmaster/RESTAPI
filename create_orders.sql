######################################################################
#
# File      : create_orders.sql
#
# Author    : Barry Kimelman
#
# Created   : August 20, 2019
#
# Purpose   : Create orders table
#
# Notes     : (none)
#
######################################################################

create table restapi_orders (
	order_number			int not null auto_increment,
	userid					int,  # id of user who placed order
	order_date				datetime not null,
	num_items				int not null,
	total_price				int ,  # total price in pennies
	order_status			enum( 'submitted' , 'shipped' , 'canceled' ) not null,
	primary key (order_number)
);
