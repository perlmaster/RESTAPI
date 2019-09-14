#!C:\Perl64\bin\perl.exe -w

######################################################################
#
# File      : restapi-server.cgi
#
# Author    : Barry Kimelman
#
# Created   : August 17, 2019
#
# Purpose   : RESTAPI server CGI script to process requests from command line clients
#
######################################################################

use strict;
use warnings;
use CGI qw(:standard);
use CGI::Carp qw(warningsToBrowser fatalsToBrowser);
use FindBin;
use lib $FindBin::Bin;

require "database.pl";

my $cgi;
my $dbh;
my $username;
my $password;
my $userid;
my %user_info;
my @user_colnames;

my %response = (
	"code" => 0 , 
	"message" => "" ,
	"details" => ""
);

my %response0 = (
	"code" => 0 , 
	"message" => "" ,
	"details" => ""
);
my $response_data = "";

my %functions = (
	"catalog" => \&cmd_catalog ,
	"orders" => \&cmd_get_orders_info ,
	"commands" => \&cmd_commands ,
	"order" => \&cmd_order ,
	"myinfo" => \&cmd_myinfo
);
my $logfile = "c:\\junk\\rest.log";

######################################################################
#
# Function  : print_log
#
# Purpose   : Write a message to the logfile
#
# Inputs    : $_[0] - open mode ( ">" or ">>" )
#             $_[1 .. $#@] - strings comprising message
#
# Output    : (none)
#
# Returns   : nothing
#
# Example   : print_log(">","Process the files : ",join(" ",@xx),"\n");
#
# Notes     : (none)
#
######################################################################

sub print_log
{
	my ( $mode , $message );

	$mode = shift @_;
	$message = join('',@_);
	if ( open(LOG,"${mode}${logfile}") ) {
		print LOG "$message";
		close LOG;
	} # IF

	return;
} # end of print_log

######################################################################
#
# Function  : prepare_execute_sql
#
# Purpose   : Issue the "prepare" and "execute" calls for a SQL statement
#
# Inputs    : $_[0] - SQL statement
#             $_[1] - 1st part of error message when needed
#
# Output    : (none)
#
# Returns   : IF problem THEN undef ELSE statement handle
#
# Example   : $sth = prepare_execute_sql($sql,"Orders command failed");
#
# Notes     : (none)
#
######################################################################

sub prepare_execute_sql
{
	my ( $sql , $error_1 ) = @_;
	my ( $sth );

	$sth = $dbh->prepare($sql);
	unless ( defined $sth ) {
		$response{'code'} = 1;
		$response{'message'} = $error_1 . " : Could not prepare sql : $sql";
		$response{'details'} = $dbh->errstr;
		return undef;
	} # UNLESS
	unless ( $sth->execute() ) {
		$response{'code'} = 1;
		$response{'message'} = $error_1 . " : Could not execute sql : $sql";
		$response{'details'} = $dbh->errstr;
		$sth->finish();
		return undef;
	} # UNLESS

	return $sth;
} # end of prepare_execute_sql

######################################################################
#
# Function  : record_function
#
# Purpose   : Record info for the command requested by the user
#
# Inputs    : $_[0] - command
#
# Output    : (none)
#
# Returns   : IF problems THEN negative ELSE zero
#
# Example   : record_function("catalog");
#
# Notes     : (none)
#
######################################################################

sub record_function
{
	my ( $cmd ) = @_;
	my ( $sql , $num_rows );

	$sql =<<SQL;
INSERT INTO restapi_commands ( cmd_date , userid , cmd)
VALUES ( now() , $userid , "$cmd" )
SQL
	$num_rows = $dbh->do($sql);
	unless ( defined $num_rows ) {
		return -1;
	} # UNLESS

	return 0;
} # end of record_function

######################################################################
#
# Function  : check_username_and_password
#
# Purpose   : Validate the username and password specifiedby the client
#
# Inputs    : (none)
#
# Output    : (none)
#
# Returns   : IF ok THEN zero ELSE non zero
#
# Example   : $status = check_username_and_password();
#
# Notes     : (none)
#
######################################################################

sub check_username_and_password
{
	my ( $status , $sql , $sth , $ref );

	%user_info = ();
	@user_colnames = ();
	$sql =<<QUERY;
SELECT * FROM restapi_user WHERE username = "${username}"
QUERY
	$sth = prepare_execute_sql($sql,"User verification failed");
	unless ( defined $sth ) {
		return -1;
	} # UNLESS
	$ref = $sth->{'NAME'};
	@user_colnames = @$ref;
	$ref = $sth->fetchrow_hashref();
	unless ( defined $ref ) {
		$response{'code'} = 1;
		$response{'message'} = "Invalid username";
		$response{'details'} = "?";
		$sth->finish();
		return -1;
	} # UNLESS
	$status = 0;
	if ( $ref->{"password"} eq $password ) {
		print_log(">>","Userid for user = '$username' is '$userid'\n");
		$userid = $ref->{'userid'};
		$response{'code'} = 0;
		$response{'message'} = "valid password for ${username}";
		$response{'details'} = "?";
		%user_info = %$ref;
	} # IF
	else {
		$response{'code'} = 1;
		$response{'message'} = "invalid password for user ${username}";
		$response{'details'} = "?";
		$status = 1;
	} # ELSE
	$sth->finish();

	return $status;
} # end of check_username_and_password

######################################################################
#
# Function  : cmd_catalog
#
# Purpose   : Retrieve catalog information
#
# Inputs    : (none)
#
# Output    : (none)
#
# Returns   : IF ok THEN zero ELSE non zero
#
# Example   : $status = cmd_catalog();
#
# Notes     : (none)
#
######################################################################

sub cmd_catalog
{
	my ( $query , $sql , $ref , $sth );

	$query =<<QUERY;
SELECT * FROM restapi_catalog
QUERY
	$sth = prepare_execute_sql($query,"Catalog command failed");
	unless ( defined $sth ) {
		return -1;
	} # UNLESS

	$response_data = "";
	while ( $ref = $sth->fetchrow_hashref() ) {
		$response_data .= "<ITEM>" . $ref->{'item_name'} . ',' . $ref->{'sku_number'} .
					',' . $ref->{'item_price'} . "</ITEM>\n";
	} # WHILE over catalog entries
	$sth->finish();

	return 0;
} # end of cmd_catalog

######################################################################
#
# Function  : cmd_get_orders_info
#
# Purpose   : Retrieve orders information for a user
#
# Inputs    : (none)
#
# Output    : (none)
#
# Returns   : IF ok THEN zero ELSE non zero
#
# Example   : $status = cmd_get_orders_info();
#
# Notes     : (none)
#
######################################################################

sub cmd_get_orders_info
{
	my ( $status , %fields , $tag1 , $tag2 , $value , $sth , $ref , $query );
	my ( $num_orders , $ref_orders , $ref_item );

	$query =<<QUERY;
SELECT order_number,order_date,num_items,total_price,order_status
FROM restapi_orders
WHERE userid = $userid
ORDER BY order_number
QUERY
	$sth = prepare_execute_sql($query,"Orders command failed");
	unless ( defined $sth ) {
		return -1;
	} # UNLESS
	$ref_orders = $sth->fetchall_hashref('order_number');
	$sth->finish();

	$response_data = "";
	$num_orders = 0;
	foreach my $ord_num ( keys %$ref_orders ) {
		$num_orders += 1;
		$response_data .= "<ORDER>\n";
		$response_data .= "<ORDER_ID>${ord_num}</ORDER_ID>\n";
		$response_data .= "<ORDER_DATE>$ref_orders->{$ord_num}{'order_date'}</ORDER_DATE>\n";
		$response_data .= "<NUM_ITEMS>$ref_orders->{$ord_num}{'num_items'}</NUM_ITEMS>\n";
		$response_data .= "<TOTAL_PRICE>$ref_orders->{$ord_num}{'total_price'}</TOTAL_PRICE>\n";
		$response_data .= "<ORDER_STATUS>$ref_orders->{$ord_num}{'order_status'}</ORDER_STATUS>\n";
		$query =<<QUERY;
SELECT item_id,sku_number,quantity,item_price
FROM restapi_order_items
WHERE order_number = $ord_num
QUERY
		$sth = prepare_execute_sql($query,"Orders command failed");
		unless ( defined $sth ) {
			$response_data .= "</ORDER>\n";
			return -1;
		} # UNLESS
		$ref_item = $sth->fetchrow_hashref();
		while ( defined $ref_item ) {
			$response_data .= "<ITEM>\n";
			$response_data .= "<SKU>$ref_item->{'sku_number'}</SKU>\n";
			$response_data .= "<QUANTITY>$ref_item->{'quantity'}</QUANTITY>\n";
			$response_data .= "<ITEM_PRICE>$ref_item->{'item_price'}</ITEM_PRICE>\n";
			$response_data .= "</ITEM>\n";
			$ref_item = $sth->fetchrow_hashref();
		} # WHILE over items in an order
		$response_data .= "</ORDER>\n";
	} # FOREACH over all orders for the user
	$sth->finish();
	$response_data .= "<NUM_ORDERS>${num_orders}</NUM_ORDERS>\n";

	return $status;
} # end of cmd_get_orders_info

######################################################################
#
# Function  : cmd_commands
#
# Purpose   : Retrieve commands information
#
# Inputs    : (none)
#
# Output    : (none)
#
# Returns   : IF ok THEN zero ELSE non zero
#
# Example   : $status = cmd_commands();
#
# Notes     : (none)
#
######################################################################

sub cmd_commands
{
	my ( $status , %fields , $sth , $ref , $sql );
	my ( $num_cmds );

	$sql =<<QUERY;
SELECT cmd_date,cmd
FROM restapi_commands
WHERE userid = $userid;
QUERY
	$sth = prepare_execute_sql($sql,"Commands command failed");
	unless ( defined $sth ) {
		return -1;
	} # UNLESS

	$response_data = "";
	$num_cmds = 0;
	while ( $ref = $sth->fetchrow_hashref() ) {
		$num_cmds += 1;
		$response_data .= "<COMMAND>" . $ref->{'cmd_date'} . '::' .
					$ref->{'cmd'} .  "</COMMAND>\n";
	} # WHILE over orders entries
	$sth->finish();
	$response_data .= "<NUM_CMDS>${num_cmds}</NUM_CMDS>\n";

	return $status;
} # end of cmd_commands

######################################################################
#
# Function  : cmd_order
#
# Purpose   : Process an order from the client
#
# Inputs    : (none)
#
# Output    : (none)
#
# Returns   : IF ok THEN zero ELSE non zero
#
# Example   : $status = cmd_order();
#
# Notes     : (none)
#
######################################################################

sub cmd_order
{
	my ( $query , $sth , $ref , @sku , @parms , @items_sku );
	my ( $sku_count , @list , $ref_cat , $item_cost , $total_cost , $summary );
	my ( $dollars , $item_info , $all_info , $sep , $sql , $num_rows , $status );
	my ( @list_order_items , $num_items , $new_row_id , $quoted );

	print_log(">>","Process ORDER cmd : user = '$username' , userid = '$userid'\n");
	$query =<<QUERY;
SELECT * FROM restapi_catalog
QUERY
	$sth = prepare_execute_sql($query,"Order [catalog] command failed");
	unless ( defined $sth ) {
		return -1;
	} # UNLESS

	$ref_cat = $sth->fetchall_hashref('sku_number');
	@sku = keys %$ref;
	@parms = $cgi->param();
	@items_sku = grep /sku_count_\d+/,@parms;
	if ( 0 == scalar @items_sku ) {
		$response{'code'} = 1;
		$response{'message'} = "Order command failed : No SKU/Count parameters";
		$response{'details'} = $dbh->errstr;
		$sth->finish();
		return -1;
	} # IF

	$total_cost = 0;
	$summary = "<SUMMARY>";
	$all_info = "";
	$sep = "";
	@list_order_items = ();
	$num_items = scalar @items_sku;
	foreach my $sku ( @items_sku ) {
		$sku_count = $cgi->param($sku);
		@list = split(/,/,$sku_count);  # [0] is sku , [1] is quantity
		$ref = $ref_cat->{$list[0]};
		unless ( defined $ref ) {
			$response{'code'} = 1;
			$response{'message'} = "Order command failed : Invalid SKU '$list[0]'";
			$response{'details'} = $dbh->errstr;
			$sth->finish();
			return -1;
		} # UNLESS
		if ( $list[1] =~ m/\D/ ) {
			$response{'code'} = 1;
			$response{'message'} = "Order command failed : Non numeric character in count for SKU '$list[0]' : '$list[1]'";
			$response{'details'} = $dbh->errstr;
			$sth->finish();
			return -1;
		} # IF
		push @list_order_items,{ "sku_number" => $list[0] , "quantity" => $list[1] , "item_price" => $ref->{'item_price'} };
		$item_info = "${list[0]}/${list[1]}/" . $ref->{'item_price'};
		$all_info .= $sep . $item_info;
		$sep = ",";
		$item_cost = $ref->{'item_price'} * $list[1];
		$dollars = '$' . sprintf "%.2f",$item_cost/100.0;
		$total_cost += $item_cost;
		$summary .=<<ITEM;
SKU $list[0] '$ref->{"item_name"}' , count = $list[1] , cost = $dollars
ITEM
	} # FOREACH
	$dollars = '$' . sprintf "%.2f",$total_cost/100.0;
	$summary .= "\nTotal Cost = $dollars\n</SUMMARY>";
	$response{'code'} = 0;
	$response{'message'} = "Order details are ok";
	$response{'details'} = "";
	$sth->finish();
	$response_data = $summary;

	$sql =<<SQL;
INSERT INTO restapi_orders ( userid , order_date , total_price , order_status , num_items )
VALUES ( $userid , now() , $total_cost , "submitted" , $num_items )
SQL
	$num_rows = $dbh->do($sql);
	unless ( defined $num_rows ) {
		$response{'code'} = 1;
		$response{'message'} = "Order command failed : could not save details";
		$response{'details'} = $dbh->errstr . "\nSQL used was\n${sql}\n";
		$sth->finish();
		return -1;
	} # UNLESS
	$new_row_id = $dbh->last_insert_id(undef, "qwlc", "restapi_orders", "order_number");
	unless ( defined $new_row_id ) {
		$new_row_id = 999666;
	} # UNLESS
	$sth->finish();

##  push @list_order_items,{ "sku_number" => $list[0] , "quantity" => $list[1] , "item_price" => $ref->{'item_price'} };
	foreach my $ref_item_info ( @list_order_items ) {
		$quoted = '"' . $ref_item_info->{"sku_number"} . '"';
		$sql =<<SQL;
INSERT INTO restapi_order_items ( sku_number , quantity , item_price , order_number )
VALUES ( $quoted , $ref_item_info->{"quantity"} , $ref_item_info->{"item_price"} , $new_row_id )
SQL
		$num_rows = $dbh->do($sql);
		unless ( defined $num_rows ) {
			$response{'code'} = 1;
			$response{'message'} = "Order command failed : could not save details";
			$response{'details'} = $dbh->errstr . "\nSQL used was\n${sql}\n";
			$sth->finish();
			return -1;
		} # UNLESS
	} # FOREACH

	return 0;
} # end of cmd_order

######################################################################
#
# Function  : cmd_myinfo
#
# Purpose   : Retrieve info for specified user
#
# Inputs    : (none)
#
# Output    : (none)
#
# Returns   : IF ok THEN zero ELSE non zero
#
# Example   : $status = cmd_myinfo();
#
# Notes     : (none)
#
######################################################################

sub cmd_myinfo
{
	my ( $status );

	$response_data = "<COLNAMES>" . join(",",@user_colnames) . "</COLNAMES>\n";
	foreach my $colname ( @user_colnames ) {
		$response_data .= "<$colname>$user_info{$colname}</$colname>\n";
	} # FOREACH

	return $status;
} # end of cmd_myinfo

######################################################################
#
# Function  : MAIN
#
# Purpose   : Entry point for this program.
#
# Inputs    : @ARGV - array of parameters
#
# Output    : HTML
#
# Returns   : 0 --> success , non-zero --> failure
#
# Example   : (none)
#
# Notes     : (none)
#
######################################################################

my ( $buffer , $status , $function , $func , $errmsg , $errors );

$cgi = new CGI;

print "Content-Type: text/xml\r\n";   # header tells client you send XML
print "\r\n";                         # empty line is required between headers and body

%response = %response0;
$response_data = "";
$username = $cgi->param('username');
$password = $cgi->param('password');

$errors = 0;

#---------------------#
# Connect to database #
#---------------------#
$dbh = mysql_connect_to_db("qwlc","127.0.0.1","root","archer-nx01",undef,\$errmsg);
unless ( defined $dbh ) {
	$response{'code'} = 1;
	$response{'message'} = "Can't connect to database\n${errmsg}\n";
	$response{'details'} = "?";
	$errors += 1;
} # UNLESS

# Validate presence of username and password

unless ( $errors ) {
	unless ( defined $username && $username =~ m/\S/ && defined $password && $password =~ m/\S/ ) {
		$response{'code'} = 1;
		$response{'message'} = "Missing username or password in request";
		$response{'details'} = "?";
		$errors += 1;
	} # UNLESS
} # UNLESS

# Validate username and password
unless ( $errors ) {
	$status = check_username_and_password();
	if ( $status ) {
		$errors += 1;
	} # IF
} # UNLESS

# Process request from client

unless ( $errors ) {
	$function = $cgi->param('function');
	print_log(">","user = '$username' , pass = '$password' , func = '$function'\n");
	unless ( defined $function && $function =~ m/\S/ ) {
		$response{'code'} = 1;
		$response{'message'} = "User request does not contain a function code";
		$response{'details'} = "?";
	} # UNLESS
	else {
		record_function($function);
		$func = $functions{$function};
		if ( defined $func ) {
			$func->();
		} # IF
		else {
			$response{'code'} = 1;
			$response{'message'} = "User request contains invalud function code '$function'";
			$response{'details'} = "?";
		} # ELSE

	} # ELSE
} # UNLESS

# write response
$buffer = join("\n" , map { "<$_>" . $response{$_} . "</$_>" } ( "code" , "message" , "details" )) . "\n";
if ( $response_data =~ m/\S/ ) {
	$buffer .= $response_data;
} # IF
$buffer = "<response>\n${buffer}\n</response>\n";
print "$buffer";

exit 0;
