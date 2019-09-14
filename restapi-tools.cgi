#!C:\Perl64\bin\perl.exe -w

######################################################################
#
# File      : restapi-tools.cgi
#
# Author    : Barry Kimelman
#
# Created   : August 27, 2019
#
# Purpose   : Tools for the RESTAPI server and client
#
######################################################################

use strict;
use warnings;
use CGI qw(:standard);
use CGI::Carp qw(warningsToBrowser fatalsToBrowser);
use File::Spec;
use File::Basename;
use DBI;
use Data::Dumper;
use FindBin;
use lib $FindBin::Bin;

require "database.pl";
require "CGI-DUMP-COOKIES.pl";
require "CGI-DUMP-ENV.pl";
require "CGI-DUMP-PARAMETERS.pl";

my $cgi;
my $dbh;
my $script_name = "";
my %parameters = ();
my $top_level_href;
my $title = "RESTAPI Tools";

my $onmouseover =<<MOUSE;
onMouseOver="this.style.background='peru';this.style.color='white';this.style.fontWeight=900;return true;"
onMouseOut="this.style.backgroundColor=''; this.style.color='black';this.style.fontWeight=500;"
MOUSE

my %functions = (
	"meta1" => \&list_metadata ,
	"list_catalog" => \&list_catalog ,
	"list_orders" => \&list_orders ,
	"list_users" => \&list_users ,
	"add_user_1" => \&add_user_1 ,
	"add_user_2" => \&add_user_2 ,
	);

my $input_field_width = 60;

my %screen_fields_add_user = (
"first_name" => { "required" => "yes" , "field_title" => "First Name" , "data_type" => "string" } ,
"last_name" => { "required" => "yes" , "field_title" => "Last Name" , "data_type" => "string" } ,
"email" => { "required" => "yes" , "field_title" => "Email" , "data_type" => "string" } ,
"username" => { "required" => "yes" , "field_title" => "Username" , "data_type" => "string" } ,
"password" => { "required" => "yes" , "field_title" => "Password" , "data_type" => "password" } ,
"addr_line1" => { "required" => "yes" , "field_title" => "Address Line 1" , "data_type" => "string" } ,
"addr_line2" => { "required" => "no" , "field_title" => "Address Line 2" , "data_type" => "string" } ,
"city" => { "required" => "yes" , "field_title" => "City" , "data_type" => "string" } ,
"state" => { "required" => "yes" , "field_title" => "State" , "data_type" => "string" } ,
"zipcode" => { "required" => "yes" , "field_title" => "Zipcode" , "data_type" => "string" } ,
"country" => { "required" => "yes" , "field_title" => "Country" , "data_type" => "string" } ,
"phone" => { "required" => "yes" , "field_title" => "Phone" , "data_type" => "string" } ,
"cell" => { "required" => "yes" , "field_title" => "Cell Phone" , "data_type" => "string" } ,
);
my @fields_order_add_user = (
	"first_name" , "last_name" , "email" , "username" , "password" , "addr_line1" ,
	"addr_line2" , "city" , "state" , "zipcode" , "country" , "phone" , "cell"
);

######################################################################
#
# Function  : display_error
#
# Purpose   : Display an error message.
#
# Inputs    : @_ - array of strings comprising error message
#
# Output    : requested error message
#
# Returns   : (nothing)
#
# Example   : display_error("Hello from here ",$xx);
#
# Notes     : (none)
#
######################################################################

sub display_error
{
	my ( $message );

	$message = join("",@_);
	print "<span class='redtext'>${message}</span>\n";

	return;
} # end of display_error

######################################################################
#
# Function  : list_metadata
#
# Purpose   : Perform metadata tests.
#
# Inputs    : (none)
#
# Output    : appropriate diagnostics
#
# Returns   : (nothing)
#
# Example   : list_metadata();
#
# Notes     : (none)
#
######################################################################

sub list_metadata
{
	mysql_describe_table("restapi_catalog",'qwlc',$dbh);
	mysql_describe_table("restapi_commands",'qwlc',$dbh);
	mysql_describe_table("restapi_orders",'qwlc',$dbh);
	mysql_describe_table("restapi_user",'qwlc',$dbh);

	return;
} # end of list_metadata

######################################################################
#
# Function  : list_table_contents
#
# Purpose   : List the contents of the named table
#
# Inputs    : $_[0] - table name
#
# Output    : table records
#
# Returns   : IF problem THEN negative ELSE zero
#
# Example   : $status = list_table_contents($table);
#
# Notes     : (none)
#
######################################################################

sub list_table_contents
{
	my ( $table ) = @_;
	my ( $sql , $sth , $buffer , $ref , @colnames , $index , @cols );
	my ( $count , @parts , $sep , $dollars );

	$sql =<<QUERY;
SELECT * FROM ${table}
QUERY
	$sth = $dbh->prepare($sql);
	unless ( defined $sth ) {
		display_error("prepare failed for the SQL statement<BR>${sql}<BR>$DBI::errstr<BR>\n");
		return -1;
	} # UNLESS
	unless ( $sth->execute() ) {
		display_error("execute failed for the SQL statement<BR>${sql}<BR>$DBI::errstr<BR>\n");
		$sth->finish();
		return -1;
	} # UNLESS

	$ref = $sth->{'NAME'};
	@colnames = @$ref;
	$buffer = join("" , map { "<TH>$_</TH>" } @colnames);
	print qq~
<TABLE border="1" cellspacing="0" cellpadding="3">
<THEAD>
<TR class="th2">${buffer}</TR>
</THEAD>
<TBODY>
~;
$count = 0;
	$ref = $sth->fetchrow_arrayref();
	while ( defined $ref ) {
		$count += 1;
		@cols = @$ref;
		for ( $index = 0 ; $index <= $#colnames ; ++$index ) {
			unless ( defined $cols[$index] ) {
				$cols[$index] = "";
			} # UNLESS
			if ( $colnames[$index] =~ m/price/i ) {
				$cols[$index] = '$' . sprintf "%.2f",$cols[$index]/100.0;
			} # IF
			$buffer = "";
			$sep = "";
			if ( $colnames[$index] =~ m/items_info/i ) {
				foreach my $item ( split(/,/,$cols[$index]) ) {
					@parts = split(/\//,$item);
					$dollars = '$' . sprintf "%.2f",$parts[2]/100.0;
					$buffer .= $sep . "SKU = $parts[0] , count = $parts[1] , unit_price = $dollars";
					$sep = "<BR>";
				} # FOREACH
				$cols[$index] = $buffer;
			} # IF
		} # FOR
		$buffer = join("" , map { "<TD>$_</TD>" } @cols);
		print qq~
<TR ${onmouseover}>${buffer}</TR>
~;
		$ref = $sth->fetchrow_arrayref();
	} # WHILE
	$sth->finish();
	print "</TBODY>\n</TABLE>\n<BR>\n";
	print "<BR>${count} records retrieved from table '$table'<BR>\n";

	return 0;
} # end of list_table_contents

######################################################################
#
# Function  : list_catalog
#
# Purpose   : List records in catalog table
#
# Inputs    : (none)
#
# Output    : records from catalog table
#
# Returns   : (nothing)
#
# Example   : list_catalog();
#
# Notes     : (none)
#
######################################################################

sub list_catalog
{
	my ( $status );

	$status = list_table_contents("restapi_catalog");

	return;
} # end of list_catalog

######################################################################
#
# Function  : list_orders
#
# Purpose   : List records in orders table
#
# Inputs    : (none)
#
# Output    : records from orders table
#
# Returns   : (nothing)
#
# Example   : list_orders();
#
# Notes     : (none)
#
######################################################################

sub list_orders
{
	my ( $status , $sql , $sth , $ref , @colnames );

	$sql =<<QUERY;
SELECT sku_number,item_name FROM restapi_catalog
QUERY
	$sth = $dbh->prepare($sql);
	unless ( defined $sth ) {
		display_error("prepare failed for the SQL statement<BR>${sql}<BR>$DBI::errstr<BR>\n");
		return -1;
	} # UNLESS
	unless ( $sth->execute() ) {
		display_error("execute failed for the SQL statement<BR>${sql}<BR>$DBI::errstr<BR>\n");
		$sth->finish();
		return -1;
	} # UNLESS

	$ref = $sth->{'NAME'};
	@colnames = @$ref;
	print qq~
<TABLE border="1" cellspacing="0" cellpadding="3">
<THEAD>
<TR class="th2"><TH>SKU</TH><TH>Item Name</TH></TR>
</THEAD>
~;
	$ref = $sth->fetchrow_hashref();
	while ( defined $ref ) {
		print qq~
<TR><TD>$ref->{'sku_number'}</TD><TD>$ref->{'item_name'}</TD></TR>
~;
		$ref = $sth->fetchrow_hashref();
	} # WHILE
	$sth->finish();
	print "</TBODY></TABLE><BR>\n";

	$status = list_table_contents("restapi_orders");

	return;
} # end of list_orders

######################################################################
#
# Function  : list_users
#
# Purpose   : List records in users table
#
# Inputs    : (none)
#
# Output    : records from users table
#
# Returns   : (nothing)
#
# Example   : list_users();
#
# Notes     : (none)
#
######################################################################

sub list_users
{
	my ( $status );

	$status = list_table_contents("restapi_user");

	return;
} # end of list_users

######################################################################
#
# Function  : generate_add_new_entry_screen
#
# Purpose   : Generate the add new entry screen.
#
# Inputs    : $_[0] - ref to hash of screen field definitions
#             $_[1] - ref to array of field names defining order
#             $_[2] - value for function code hidden field
#             $_[3] - value for legend title
#
# Output    : HTML code for the add new entry screen.
#
# Returns   : nothing
#
# Example   : generate_add_new_entry_screen(\%screen_fields,\@fields_order,'nextfunc','New User Entry');
#
# Notes     : (none)
#
######################################################################

sub generate_add_new_entry_screen
{
	my ( $ref_screen_fields , $ref_fields_order , $function , $legend_title ) = @_;
	my ( $num_fields , $ref_field , $count , $errmsg , @dropdown );
	my ( $field , $title , $required , $value , %screen_fields );
	my ( $clock , $sec , $min , $hour , $mday , $mon , $year , $wday , $yday , $isdst );
	my ( @fields_order , $date_field , @required , $buffer );

	%screen_fields = %$ref_screen_fields;
	@fields_order = @$ref_fields_order;
	$clock = time;
	( $sec , $min , $hour , $mday , $mon , $year , $wday , $yday , $isdst ) =
				localtime($clock);
	$num_fields = scalar keys %screen_fields;
	$required = "<span class='redtext'>*</span>";

	print qq~
<div id='main_screen' class='pad_left'>
<H3>Required fields are marked with ${required}</H3>
<H3>The format of the date field is YYYY/MM/DD  or  YYYY-MM-DD</H3>
~;

	print qq~
<FORM name="data_entry_form" id="data_entry_form" method="POST" action="${script_name}">
<input type="hidden" name="function" value="$function">
<TABLE border="0" cellspacing="0" cellpadding="4" action="${script_name}">
<CAPTION class='bluetext2'>${legend_title}</CAPTION>
<TBODY style="background: wheat;">
~;

	@required = ();
	foreach my $fieldname ( @fields_order ) {
		$ref_field = $screen_fields{$fieldname};
		if ( $ref_field->{'required'} eq "yes" ) {
			$title = $required . $ref_field->{field_title};
			push @required,$fieldname;
		} # IF
		else {
			$title = $ref_field->{field_title};
		} # ELSE
		print "<TR><TD class='right1'>$title</TD>",
					"<TD width='40px'>\&nbsp;</TD><TD>";
		$value = "";
		if ( $ref_field->{'data_type'} eq "password" ) {
			$field = "<input class='input_fieldset1' type='password' id='${fieldname}' name='${fieldname}' value='${value}' title='$ref_field->{field_title}' size='$input_field_width'>";
		} # IF
		else {
			$field = "<input class='input_fieldset1' type='text' id='${fieldname}' name='${fieldname}' value='${value}' title='$ref_field->{field_title}' size='$input_field_width'>";
		} # ELSE
		print "${field}</TD><TD width='10px'></TD></TR>\n";
	} # FOREACH
	$buffer = join(" , ",map { '"' . $_ . '"' } @required);
	print qq~
</TBODY>
</TABLE>
</fieldset>
<BR>
<input type="submit" class="darktext2" value="Process New Data" name="submit1"
onclick="return check_required_fields(data_entry_form);"
/>

&nbsp;&nbsp;
<input type="reset" name="reset" class="darktext2" value="Reset Form Fields"
/>
</FORM>
</div>
<BR><BR>
~;
	print qq~
<script type="text/javascript">
var required_fields = [ $buffer ];
var num_required = required_fields.length;
</script>
~;

	return;
} # end of generate_add_new_entry_screen

######################################################################
#
# Function  : add_user_1
#
# Purpose   : Generate the add new user entry screen
#
# Inputs    : (none)
#
# Output    : data entry screen for adding a new user
#
# Returns   : (nothing)
#
# Example   : add_user_1();
#
# Notes     : (none)
#
######################################################################

sub add_user_1
{
	my ( $message );

	generate_add_new_entry_screen(\%screen_fields_add_user,\@fields_order_add_user,'add_user_2','New User Data Entry');

	return;
} # end of add_user_1

######################################################################
#
# Function  : add_user_2
#
# Purpose   : Process request to add a new user
#
# Inputs    : (none)
#
# Output    : appropriate messages
#
# Returns   : (nothing)
#
# Example   : add_user_2();
#
# Notes     : (none)
#
######################################################################

sub add_user_2
{
	my ( $value , $ref , $sql , $num_rows , $sep , $errors , $values );

	$sql = "INSERT INTO restapi_user (";
	$sep = "";
	$errors = 0;
	$values = "VALUES ( ";
	foreach my $fieldname ( keys %screen_fields_add_user ) {
		$value = $cgi->param($fieldname);
		if ( $screen_fields_add_user{'required'} eq "yes" ) {
			if ( defined $value && $value =~ m/\S/ ) {
				$values .= $sep . '"$value"';
				$sql .= $sep . $fieldname;
				$sep = " , ";
			} # IF
			else {
				$errors += 1;
				display_error("No value specified for the required field '$fieldname'<BR>\n");
			} # ELSE
		} # IF
		else {
			if ( defined $value && $value =~ m/\S/ ) {
				$values .= $sep . '"' . $value. '"';
				$sql .= $sep . $fieldname;
				$sep = " , ";
			} # IF
		} # ELSE
	} # FOREACH
	if ( $errors == 0 ) {
		$sql .= " , created_date , modified_date";
		$values .= " , now() , now()";
		$sql .= " ) " . $values . " ) ";
		print "<H3>Use the sql : $sql</H3>\n";
		$num_rows = $dbh->do($sql);
		unless ( defined $num_rows ) {
			display_error("error executing : ${sql}<BR>",$DBI::errstr,"<BR>");
			return 1;
		} # UNLESS
		else {
			print "<H3>Successfully added the user record</H3>\n";
		} # ELSE
	} # IF

	return 0;
} # end of add_user_2

######################################################################
#
# Function  : generate_menu_entry
#
# Purpose   : Generate an entry for the main commands menu
#
# Inputs    : $_[0] - menu title
#             $_[1] - command function word
#             $_[2] - help text for mouse hover
#
# Output    : main menu entry
#
# Returns   : 0 --> success , non-zero --> failure
#
# Example   : generate_menu_entry("Add New Entry","addsub1","Add info for a new day");
#
# Notes     : (none)
#
######################################################################

sub generate_menu_entry
{
	my ( $menu_title , $function_word , $helptext ) = @_;
	my ( $form_name );

	$form_name = "form_${function_word}";
	print qq~
	<TR><TD>
<FORM method="POST" action="$script_name">
<input type="hidden" id="function" name="function" value="$function_word">
<input class="darktext2c" type="submit" value="$menu_title"
onmouseover="this.style.color='peru'; this.style.fontFamily='Arial Black';show_help_text('$helptext');"
onmouseout="this.style.color='black'; this.style.background='gainsboro'; this.style.fontFamily='Arial';hide_help_text();"
>
</FORM>
</TD></TR>
~;

	return;
} # end of generate_menu_entry

######################################################################
#
# Function  : generate_main_screen
#
# Purpose   : Generate the main screen
#
# Inputs    : (none)
#
# Output    : HTML
#
# Returns   : 0 --> success , non-zero --> failure
#
# Example   : generate_main_screen();
#
# Notes     : (none)
#
######################################################################

sub generate_main_screen
{

	print qq~
<script type="text/javascript">

function hide_help_text()
{
	document.getElementById('functext').innerHTML = "&nbsp;";
	// document.getElementById('functext').style.background = "white";
}

function show_help_text(help_text)
{
	// hide_all_help_text();
	// document.getElementById('functext').style.background = "wheat";
	document.getElementById('functext').innerHTML = help_text;
}

</script>

<div class="pad_left">

<TABLE border="0" cellspacing="0" cellpadding="6">
<TBODY>
<TR><TD id="functext" name="functext"
style="width: 325px; font-weight: bold; color: peru;">&nbsp;</TD></TR>
~;
	generate_menu_entry("List metadata","meta1","List the metadata for the database table");
	generate_menu_entry("List Catalog","list_catalog","List records from the catalog table");
	generate_menu_entry("List Orders","list_orders","List records from the orders table");
	generate_menu_entry("List Users","list_users","List records from the users table");
	generate_menu_entry("Add User","add_user_1","Generate the add new user entry screen");

	print "</TBODY></TABLE></div>\n";

	return;
} # end of generate_main_screen

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

my ( $function , $status , $errmsg , $func );

$cgi = new CGI;
%parameters = map { $_ , $cgi->param($_) } $cgi->param();

print $cgi->header;

print $cgi->start_html(
			-title => "$title" ,
			-style=>[
				{-src=>'/tooltip.css'},
				{-src=>'/styles.css'},
				{-src=>'/fieldset.css'},
				{-src=>'/print.css'}
			],
			-script=>[
				{-type=>'javascript', -src=>'/check_all_fields.js'},
				{-type=>'javascript', -src=>'/check_for_missing_fields.js'},
				{-type=>'javascript', -src=>'/clearForm.js'},
				{-type=>'javascript', -src=>'/check_required_fields.js'} ,
				{-type=>'javascript', -src=>'/hide_show_divider.js'}
			]
		);

print $cgi->h1("$title");

$script_name = basename($0);
$top_level_href = "<A class='boldlink2' HREF='${script_name}'>Return to Main Screen</A>";

print qq~
<script type="text/javascript">
function general_submission(form_name)
{
	document.getElementById('notes').value = "just a general submission";
	document.getElementById('job_description').value = "just a general submission";
}
</script>
~;

#---------------------#
# Connect to database #
#---------------------#
$dbh = mysql_connect_to_db("qwlc","127.0.0.1","root","archer-nx01",undef,\$errmsg);
unless ( defined $dbh ) {
	display_error($errmsg);
	print $cgi->end_html;
	exit 0;
} # UNLESS

##  cgi_dump_script_parameters($cgi,"CGI script parameters");

#----------------------------#
# Execute requested function #
#----------------------------#
$function = $cgi->param("function");
if ( defined $function && 0 < length $function ) {
	$func = $functions{$function};
	if ( defined $func ) {
		$func->();
		print "<BR><BR>${top_level_href}<BR><BR>\&nbsp;\n";
	} # IF
	else {
		display_error("<BR>Unsupported function code '$function'<BR>\n");
		generate_main_screen();
	} # ELSE
} # IF
else {
	generate_main_screen();
} # ELSE

if ( defined $dbh ) {
	$dbh->disconnect();
} # IF

print $cgi->end_html;

exit 0;
