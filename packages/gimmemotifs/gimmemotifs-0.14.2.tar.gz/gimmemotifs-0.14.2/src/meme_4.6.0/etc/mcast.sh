#!/bin/csh

# This file is processed by "make" to create file run by
# the MCAST web service.

set dir = `pwd`
set jobid  = `basename $dir`

# set path 
set path = ( /home/simon/bin $path )

# get log file
set logfile = /home/simon/LOGS/mcast-log

# get the background 
set bkg = /home/simon/etc/bkg.jpg
if -e $bkg cp $bkg .

#
# create an empty index file
#
cat > index.html << HERE
<html>
<head>
<title>MCAST Output</title>
</head>
<body background="bkg.jpg">

<hr>
<h2>MCAST Job $jobid</h2>
HERE

#
# get the motif file name and DB file name from first two arguments
#
set motifs = $1; shift
set db = $1; shift

# append the local database path unless DB is an uploaded database
#
if ($db != "uploaded_db") set db = /home/simon/db/fasta_databases/$db

#
# set up the background file and number of sequences in 
# the db file switches if those local files exist
#
set bfile = ''; set nseqs = ''
if (-e $db.bfile) set bfile = "--bgfile $db.bfile"

# Get start time for log
set t1 = `date -u '+%d/%m/%y %H:%M:%S'`

#
# run mcast 
#
echo "<ul><li>/home/simon/bin/mcast $bfile $* $motifs $db </li></ul><hr>" >> index.html
#
eval "/home/simon/bin/mcast $bfile $* $motifs $db >mcast.html"

# Get finish time for log
set t2 = `date -u '+%d/%m/%y %H:%M:%S'`

# Log the job
touch $logfile
set host = `hostname`
set submit = `cat submit_time_file`
set email = `cat address_file`
echo "$host $jobid submit: $submit start: $t1 end: $t2 $* $email" >> $logfile

#
# finish the index file
#
# Results section
echo "<h2>Results</h2><blockquote><ul>" >> index.html
  if (-s mcast_out/mcast.html) echo "<li><a href='mcast_out/mcast.html'>MCAST output as HTML</a></li>" >> index.html
  if (-s motifs) echo "<li><a href='motifs'>input motifs</a></li>" >> index.html
  if (-s uploaded_db) echo "<li><a href='uploaded_db'>uploaded database</a></li>" >> index.html
  echo "</ul></blockquote><hr>" >> index.html
endif

# Messages section
if (-s stdout.txt || -s stderr.txt) then
  echo "<h2>Messages</h2><blockquote><ul>" >> index.html
  if (-s stderr.txt) echo "<li><a href='stderr.txt'>Processing Messages</a></li>" >> index.html
  echo "</ul></blockquote><hr>" >> index.html
endif

# End section
echo "</body></html>" >> index.html
