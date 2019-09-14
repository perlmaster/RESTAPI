#!C:\Perl64\bin\perl.exe -w

######################################################################
#
# File      : restapi-client.pl
#
# Author    : Barry Kimelman
#
# Created   : August 17, 2019
#
# Purpose   : RESTAPI client written in Perl
#
# Notes     : All responses are in XML format. All responses sent from
#             the server are contained within a <RESPONSE> tag.
#             The LWP::Simple module is used to send requests to the
#             server.
#
######################################################################

use strict;
use warnings;
use Getopt::Std;
use XML::Simple;
use LWP::Simple;
use LWP::UserAgent;
use LWP::Protocol::https;
use Data::Dumper;
use Term::ReadKey;
use FindBin;
use lib $FindBin::Bin;

require "\\bin\\print_lists.pl";
require "\\bin\\display_pod_help.pl";

my %options = ( "d" => 0 , "h" => 0 );
my $username = "";
my $password = "";
my $prompt = "";
my $exit_flag = 1;

my $help_quit =<<HELP_QUIT;
This command terminates the session with the RESTAPI client.
HELP_QUIT

my $help_catalog =<<HELP_CATALOG;
This command retrieves all the data from the ordering catalog.
HELP_CATALOG

my $help_order =<<HELP_ORDER;
This command places a purchase order. First all the catalog data is
retrieved and displayed then the ordering process begins.
HELP_ORDER

my $help_myorders =<<HELP_MYORDERS;
This command retrieves all the purchase orders for a customer.
HELP_MYORDERS

my $help_myinfo =<<HELP_MYINFO;
This command displays all the personal data for a user.
HELP_MYINFO

my $help_help =<<HELP_HELP;
This command displays help for the specified command.
HELP_HELP

my $help_commands =<<HELP_COMMANDS;
This command shows all the commands issued by the user.
HELP_COMMANDS

my %functions = (
	"catalog" => [ \&cmd_get_catalog_data , \$help_catalog ],
	"order" => [ \&cmd_order , \$help_order ],
	"commands" => [ \&cmd_commands , \$help_commands ],
	"myorders" => [ \&cmd_get_orders_data , \$help_myorders ],
	"myinfo" => [ \&cmd_get_myinfo , \$help_myinfo ],
	"help" => [ \&cmd_help , \$help_help ],
	"quit" => [ \&cmd_end_session , \$help_quit ]
);
my @functions = keys %functions;
my $server_response_data;
my $server_response_xml;
my %catalog = ();
my $catalog_flag = 0;

my @catalog_columns = (
	"item_name" , "sku_number" , "item_price"
);
my @orders_columns = (
	"order_number" , "order_date" , "sku_number" , "quantity"
);

######################################################################
#
# Function  : debug_print
#
# Purpose   : Optionally print a debugging message.
#
# Inputs    : @_ - array of strings comprising message
#
# Output    : (none)
#
# Returns   : nothing
#
# Example   : debug_print("Process the files : ",join(" ",@xx),"\n");
#
# Notes     : (none)
#
######################################################################

sub debug_print
{
	my ( $message );

	if ( $options{"d"} ) {
		$message = join("",@_);
		if ( $message =~ m/^(\n+)/ ) {
			print "$1";
			$message = $';
		} # IF
		print "DEBUG : $message";
	} # IF

	return;
} # end of debug_print

######################################################################
#
# Function  : print_server_error
#
# Purpose   : Display an error message returned by the server
#
# Inputs    :(none)
#
# Output    : error message
#
# Returns   : nothing
#
# Example   : print_server_error();
#
# Notes     : (none)
#
######################################################################

sub print_server_error
{
	print "Error code $server_response_xml->{'code'} returned by server\n";
	print $server_response_xml->{'message'},"\n";
	if ( $server_response_xml->{'details'} =~ m/\S/ && $server_response_xml->{'details'} ne '?' ) {
		print $server_response_xml->{'details'},"\n";
	} # IF
	print "\n";

	return;
} # end of print_server_error

######################################################################
#
# Function  : parse_xml_tags
#
# Purpose   : Parse the XML tags in the server's response
#
# Inputs    : $_[0] - string identifying user request
#
# Output    : appropriare messages
#
# Returns   : IF problem THEN non zero ELSE zero
#
# Example   : $status = parse_xml_tags("login");
#
# Notes     : (none)
#
######################################################################

sub parse_xml_tags
{
	my ( $request_type ) = @_;
	my ( $status );

	$status = 0;
	$server_response_xml = XMLin($server_response_data , , SuppressEmpty => '');

	return 0;
} # end of parse_xml_tags

######################################################################
#
# Function  : send_request_via_agent_to_server
#
# Purpose   : Sebd a request to the server
#
# Inputs    : $_[0] - string identifying the request
#             $_[1] - request structure
#
# Output    : appropriate messages
#
# Returns   : IF problem THEN negative ELSE zero
#
# Example   : $status = send_request_via_agent_to_server("login",$request);
#
# Notes     : (none)
#
######################################################################

sub send_request_via_agent_to_server
{
	my ( $request_type , $request ) = @_;
	my ( $status , $url , $ua , $response , $decoded , $num_bytes , $ref );

	print "\nSend a '$request_type' request to the server\n";
	debug_print("Request data : ${request}\n");

	$url = "http://localhost:88/cgi-bin/restapi-server.cgi?${request}";
	debug_print("Request url : ${url}\n");

	$ua = LWP::UserAgent->new;
	$ua->timeout(20);
	$ua->env_proxy;
	$response = $ua->get($url);
	unless ( $response->is_success ) {
		die("Could not send request\n$url\n",Dumper($response->status_line));
	} # UNLESS
	$decoded = $response->decoded_content;
	$server_response_data = $decoded;
	$num_bytes = length $decoded;
	debug_print("${num_bytes} bytes retrieved from ${url}\n");
	debug_print("\n$decoded\n");

	$status = parse_xml_tags("$request_type response");
	if ( $status ) {
		print "Error parsing response from server for '$request_type' request\n";
		return -1;
	} # IF
	debug_print("XML parsed from server catalog response :\n",Dumper($server_response_xml));
	if ( $server_response_xml->{'code'} != 0 ) {
		print_server_error();
		return -1;
	} # IF

	return 0;
} # end of send_request_via_agent_to_server

######################################################################
#
# Function  : read_username_and_password
#
# Purpose   : Prompt the user for a username and password
#
# Inputs    : (none)
#
# Output    : appropriate prompts
#
# Returns   : (nothing)
#
# Example   : read_username_and_password();
#
# Notes     : (none)
#
######################################################################

sub read_username_and_password
{
	print "Username : ";
	$username = <STDIN>;
	chomp $username;

	ReadMode( "noecho");
	print "Enter password for ${username} :";
	$password = <>;
	chomp $password;
	ReadMode ("original") ;
	print "\n";

	return;
} # end of read_username_and_password

######################################################################
#
# Function  : fetch_catalog_info
#
# Purpose   : Get catalog data from server
#
# Inputs    : $_[0] - ref to hash to receive catalog info
#
# Output    : (none)
#
# Returns   : IF problem THEN non zero ELSE zero
#
# Example   : $status = fetch_catalog_info(\%catalog);
#
# Notes     : (none)
#
######################################################################

sub fetch_catalog_info
{
	my ( $ref_catalog ) = @_;
	my ( $req , $ref , @items , $sku , $item_name , $item_cost , $dollars );

	%$ref_catalog = ();
	$req = "function=catalog&username=${username}&password=${password}";
	if ( send_request_via_agent_to_server("catalog",$req) < 0 ) {
		return -1;
	} # IF
	$catalog_flag = 1;

	$ref = $server_response_xml->{'ITEM'};
	if ( ref $ref eq "" ) {
		@items = ( $ref );
	} # IF
	else {
		@items = @$ref;
	} # ELSE

	foreach my $item ( @items ) {
		($item_name , $sku , $item_cost) = split(/,/,$item);
		$ref_catalog->{$sku}{'name'} = $item_name;
		$ref_catalog->{$sku}{'pennies'} = $item_cost;
		$dollars = '$' . sprintf "%.2f",$item_cost/100.0;
		$ref_catalog->{$sku}{'dollars'} = $dollars;
	} # FOREACH

	return 0;
} # end of fetch_catalog_info

######################################################################
#
# Function  : cmd_get_catalog_data
#
# Purpose   : Get catalog data from server
#
# Inputs    : (none)
#
# Output    : catalog data
#
# Returns   : IF problem THEN non zero ELSE zero
#
# Example   : $status = cmd_get_catalog_data();
#
# Notes     : (none)
#
######################################################################

sub cmd_get_catalog_data
{
	my ( $req , %tags , $status );
	my ( $ref , @items , @item_name , @sku , @price );
 
	read_username_and_password();
	unless ( $catalog_flag ) {
		if ( fetch_catalog_info(\%catalog) ) {
			return -1;
		} # IF
	} # UNLESS

	@item_name = ();
	@sku = ();
	@price = ();
	foreach my $sku ( keys %catalog ) {
		push @item_name,$catalog{$sku}{'name'};
		push @sku,$sku;
		push @price,$catalog{$sku}{'dollars'};
	} # FOREACH

	print "\n";
	print_lists([ \@item_name , \@sku , \@price ] , [ "Item Name" , "SKU" , "Price" ] , "=",\*STDOUT);

	return 0;
} # end of cmd_get_catalog_data

######################################################################
#
# Function  : cmd_order
#
# Purpose   : Make a purchase (process an order command)
#
# Inputs    : (none)
#
# Output    : appropriate messages
#
# Returns   : IF problem THEN non zero ELSE zero
#
# Example   : $status = cmd_order();
#
# Notes     : (none)
#
######################################################################

sub cmd_order
{
	my ( $req , %tags , $status , $sku );
	my ( %hash , $index , $data , @arrays , @headers , $catalog_size );
	my ( $num_order_items , $count , $buffer );
	my ( $error , $item_number , $item_count , $item_cost , $order_cost );
	my ( @order , $prompt , $summary , $sku_tag , $sku_value );
	my ( $ref , @items , @fields , @item_name , @sku , @price );
 
	read_username_and_password();

	# First we need to send a catalog request so that the user can see the
	# list of items that are available for purchase
	unless ( $catalog_flag ) {
		if ( fetch_catalog_info(\%catalog) ) {
			return -1;
		} # IF
	} # UNLESS

	@item_name = ();
	@sku = ();
	@price = ();
	foreach my $sku ( keys %catalog ) {
		push @item_name,$catalog{$sku}{'name'};
		push @sku,$sku;
		push @price,$catalog{$sku}{'pennies'};
	} # FOREACH over catalog entries

	$catalog_size = scalar @item_name;

	@arrays = ( \@item_name , \@price , \@sku );
	@headers = ( "Item Name" , "Item Price" , "SKU Number" );
	print "\n";
	print_lists( \@arrays , \@headers , "=");

	$req = "function=order&username=${username}&password=${password}";

	print "\nEnter a blank line to finish items entering process\n";
	$prompt = "Enter sku and item count : ";
	print "\n${prompt}";
	$num_order_items = 0;
	$buffer = <STDIN>;
	chomp $buffer;
	$error = 0;
	$order_cost = 0;
	@order = ();
	while ( $buffer =~ m/\S/ ) {
		unless ( $buffer =~ m/(\S+)\s+(\d+)/ ) {
			print "Invalid input line\n";
			print "\n${prompt}";
			$buffer = <STDIN>;
			chomp $buffer;
			next;
		} # UNLESS
		$sku = uc $1;
		$item_count = $2;
		unless ( exists $catalog{$sku} ) {
			$error = 1;
			print "\nInvalid characters in input data\n";
			last;
		} # IF
		$num_order_items += 1;
		$sku_tag = "sku_count_$num_order_items";
		$sku_value = "${sku},${item_count}";
		$req .= "&${sku_tag}=${sku_value}";
		$item_cost = $item_count * $catalog{$sku}{'pennies'};
		$order_cost += $item_cost;
		print "\n${prompt}";
		$buffer = <STDIN>;
		chomp $buffer;
	} # WHILE processing order items
	print "\nThere are ${num_order_items} items in your order\n";
	if ( $num_order_items > 0 ) {
		print join("\n",@order),"\n\norder cost = $order_cost\n";
		print "data for order is :\n${req}\n";
		if ( send_request_via_agent_to_server("order",$req) < 0 ) {
			return -1;
		} # IF
		else {
			$summary = $server_response_xml->{"SUMMARY"};
			if ( defined $summary ) {
				print "\nOrder Summary :\n$summary\n";
			} # IF
			else {
				print "No summary was returned\n";
			} # ELSE
		} # ELSE
	} # IF

	print "\n";

	return 0;
} # end of cmd_order

######################################################################
#
# Function  : cmd_get_orders_data
#
# Purpose   : Get orders data from server
#
# Inputs    : (none)
#
# Output    : user's orders data
#
# Returns   : IF problem THEN non zero ELSE zero
#
# Example   : $status = cmd_get_orders_data();
#
# Notes     : (none)
#
######################################################################

sub cmd_get_orders_data
{
	my ( $req , $status , @items , $num_orders , @list , $sku );
	my ( @fields , $ref , $dollars , $total_cost , $item_cost );
	my ( $id , $date , $items_info , $unit_price , $quantity );
	my ( $item_cost_dollars , @item_names , $maxlen_name , $order_status );
	my ( @orders , $ref_items , $ref_orders );
 
	read_username_and_password();

	unless ( $catalog_flag ) {
		if ( fetch_catalog_info(\%catalog) ) {
			return -1;
		} # IF
	} # UNLESS
	@item_names = map { $catalog{$_}->{'name'} } keys %catalog;
	$maxlen_name = (sort { $b <=> $a} map { length $_ } @item_names)[0];

	$req = "function=orders&username=${username}&password=${password}";
	if ( send_request_via_agent_to_server("orders",$req) < 0 ) {
		return -1;
	} # IF

	$num_orders = $server_response_xml->{'NUM_ORDERS'};
	print "\n${num_orders} orders were found for ${username}\n\n";
	if ( $num_orders == 0 ) {
		return 0;
	} # IF

	$ref_orders = $server_response_xml->{'ORDER'};
	$ref = ref $ref_orders;
# Build an array of hash references to orders info
	if ( $ref eq "HASH" ) {
		@orders = ( $ref_orders );
	} # IF
	else {
		@orders = @$ref_orders;
	} # ELSE

	printf "%2s %-20.20s %-${maxlen_name}.${maxlen_name}s %8s %-10.10s %s\n","Id","Date","Item","Quantity","Unit Price" , "Unit Cost";
	printf "%2s %-20.20s %-${maxlen_name}.${maxlen_name}s %-8.8s %-10.10s %s\n","==","====","====","========","==========" , "=========";

	foreach my $ref_order ( @orders ) {
		$id = $ref_order->{"ORDER_ID"};
		$date = $ref_order->{"ORDER_DATE"};
		$order_status = $ref_order->{"ORDER_STATUS"};
		$ref_items = $ref_order->{"ITEM"};
		$ref = ref $ref_items;
		if ( $ref eq "HASH" ) {
			@items = ( $ref_items );
		} # IF
		else {
			@items = @$ref_items;
		} # ELSE
		foreach my $ref_item ( @items ) {
			$sku = $ref_item->{"SKU"};
			$quantity = $ref_item->{"QUANTITY"};
			$unit_price = $ref_item->{"ITEM_PRICE"};
			$item_cost = $quantity * $unit_price;
			$item_cost_dollars = '$' . sprintf "%.2f",$item_cost/100.0;
			$total_cost += $item_cost;
			$dollars = '$' . sprintf "%.2f",$unit_price/100.0;
			printf "%2d %-20.20s %-${maxlen_name}.${maxlen_name}s %-8d %-10s %s\n",$id,$date,
						$catalog{$sku}{'name'},$quantity,$dollars,$item_cost_dollars;
		} # FOREACH over items in an order
		$dollars = '$' . sprintf "%.2f",$total_cost/100.0;
		printf "%2s %-20.20s %-${maxlen_name}.${maxlen_name}s %-8.8s %-10.10s","  ","    ","   ","        ","          ";
		print " $dollars (total cost of order) , status = '$order_status'\n";
		print "\n";
	} # FOREACH over all orders

	print "\n";

	return 0;
} # end of cmd_get_orders_data

######################################################################
#
# Function  : cmd_get_myinfo
#
# Purpose   : Get myinfo data from server
#
# Inputs    : (none)
#
# Output    : user's personal data
#
# Returns   : IF problem THEN non zero ELSE zero
#
# Example   : $status = cmd_get_myinfo();
#
# Notes     : (none)
#
######################################################################

sub cmd_get_myinfo
{
	my ( $req , $status , $ref , @colnames , $colnames , $maxlen );
 
	read_username_and_password();

	$req = "function=myinfo&username=${username}&password=${password}";
	if ( send_request_via_agent_to_server("myinfo",$req) < 0 ) {
		return -1;
	} # IF

	$colnames = $server_response_xml->{'COLNAMES'};
	@colnames = split(/,/,$colnames);
	$maxlen = (sort { $b <=> $a} map { length $_ } @colnames)[0];
	print "\n";
	foreach my $colname ( @colnames ) {
		printf "%-${maxlen}.${maxlen}s : %s\n",$colname,$server_response_xml->{$colname};
	} # FOREACH

	return 0;
} # end of cmd_get_myinfo

######################################################################
#
# Function  : cmd_commands
#
# Purpose   : Show all the commands issued by the user
#
# Inputs    : (none)
#
# Output    : commands issued by the user
#
# Returns   : IF problem THEN non zero ELSE zero
#
# Example   : $status = cmd_commands();
#
# Notes     : (none)
#
######################################################################

sub cmd_commands
{
	my ( $req , $cmds , $status , $ref , $count , @cmds , @fields , @list , @dates );
 
	read_username_and_password();

	$req = "function=commands&username=${username}&password=${password}";
	if ( send_request_via_agent_to_server("commands",$req) < 0 ) {
		return -1;
	} # IF

	print "Commands :\n",Dumper($server_response_xml),"\n";
	$cmds = $server_response_xml->{"COMMAND"};
	$ref = ref $cmds;
	if ( $ref eq "" ) {
		@list = ( $cmds );
	} # IF
	else {
		@list = ( @$cmds );
	} # ELSE

	@cmds = ();
	@dates = ();
	foreach my $cmd ( @list ) {
		@fields = split(/::/,$cmd);
		push @dates,$fields[0];
		push @cmds,$fields[1];
	} # FOREACH
	print_lists( [ \@dates , \@cmds ] , [ "Date" , "Command" ] , "=" , \*STDOUT);

	return 0;
} # end of cmd_commands

######################################################################
#
# Function  : cmd_end_session
#
# Purpose   : Process quit command
#
# Inputs    : (none)
#
# Output    : appropriate messages
#
# Returns   : IF problem THEN non zero ELSE zero
#
# Example   : $status = cmd_end_session();
#
# Notes     : (none)
#
######################################################################

sub cmd_end_session
{
	my ( $req , $status );

	$exit_flag = 0;

	return 0;
} # end of cmd_end_session

######################################################################
#
# Function  : cmd_help
#
# Purpose   : display help info for a command
#
# Inputs    : (none)
#
# Output    : appropriate info
#
# Returns   : nothing
#
# Example   : cmd_help();
#
# Notes     : (none)
#
######################################################################

sub cmd_help
{
	my ( $ref , $cmd , $buffer , @list );

	print "\nFor which command ? ";
	$buffer = <STDIN>;
	chomp $buffer;
	$buffer =~ s/^\s+//g;
	$buffer =~ s/\s+$//g;
	$ref = $functions{$buffer};
	unless ( defined $ref ) {
		print "Invalid command\n";
	} # UNLESS
	else {
		@list = @$ref;
		if ( defined $list[1] ) {
			$buffer = $list[1];
			print "$$buffer\n";
		} # IF
		else {
			print "No help exists for that command\n";
		} # ELSE
	} # ELSE

	return;
} # end of cmd_help

######################################################################
#
# Function  : MAIN
#
# Purpose   : TCP client written in Perl
#
# Inputs    : @ARGV - optional arguments
#
# Output    : (none)
#
# Returns   : 0 --> success , non-zero --> failure
#
# Example   : restapi-client.pl -d
#
# Notes     : (none)
#
######################################################################

MAIN:
{
	my ( $status , $buffer , $ref , @list );

	$status = getopts("hd",\%options);
	if ( $options{"h"} ) {
		display_pod_help($0);
		exit 0;
	} # IF

	unless ( $status ) {
		die("Usage : $0 [-dh]\n");
	} # UNLESS

	$prompt = "\nEnter command ( " . join(" , ",keys %functions) . " ) : ";
	print "$prompt";
	while ( $buffer = <STDIN> ) {
		chomp $buffer;
		$ref = $functions{$buffer};
		unless ( defined $ref ) {
			@list = grep /${buffer}/,@functions;
			if ( 0 < scalar @list ) {
				if ( 1 == scalar @list ) {
					print ">>> $list[0]\n";
					$ref = $functions{$list[0]};
				} # IF
				else {
					print "'$buffer' matches more than one command\n";
				} # ELSE
			} # IF
		} # UNLESS

		if ( defined $ref ) {
			@list = @$ref;
			$list[0]->($list[1]);
		} # IF
		else {
			print "Invalid command '$buffer'\n";
		} # ELSE
		print "$prompt";
		if ( $exit_flag == 0 ) {
			last;
		} # IF
	} # WHILE

	exit 0;
} # end of MAIN
__END__
=head1 NAME

restapi-client.pl - TCP client written in Perl

=head1 SYNOPSIS

restapi-client.pl [-dh]

=head1 DESCRIPTION

TCP client written in Perl

=head1 PARAMETERS

  (none)

=head1 OPTIONS

  -h - produce this summary
  -d - activate debugging mode

=head1 EXAMPLES

restapi-client.pl

=head1 EXIT STATUS

 0 - successful completion
 nonzero - an error occurred

=head1 AUTHOR

Barry Kimelman

=cut
