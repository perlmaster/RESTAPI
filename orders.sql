######################################################################
#
# File      : orders.sql
#
# Author    : Barry Kimelman
#
# Created   : November 30, 2017
#
# Purpose   : joined query for customer orders
#
# Notes     : (none)
#
######################################################################

SELECT o.order_number,o.userid,o.order_date,o.sku_number,o.quantity,o.unit_price,o.total_price,
u.first_name,u.last_name,u.email,u.phone,u.cell
FROM restapi_orders o,restapi_user u
WHERE o.userid = u.userid
;
