######################################################################
#
# File      : create_order_items.sql
#
# Author    : Barry Kimelman
#
# Created   : September 2, 2019
#
# Purpose   : Create order items table
#
# Notes     : (none)
#
######################################################################

create table restapi_order_items (
	item_id					int not null auto_increment,
	sku_number				varchar(32) not null ,
	quantity				int not null ,
	item_price				int not null ,
	order_number			int not null ,
	primary key (item_id) ,
	foreign key (order_number) references restapi_orders(order_number)
);
