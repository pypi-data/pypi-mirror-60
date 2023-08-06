#!/bin/csh

# This file is processed by "make" to create file run by
# the GLAM2SCAN web service.

set dir = `pwd`
set jobid  = `basename $dir`

# create link to binary directory
ln -s /home/simon/bin bin

# get log file
set logfile = /home/simon/LOGS/glam2scan-log

# get the background 
set bkg = /home/simon/etc/bkg.jpg
if -e $bkg cp $bkg .

#
# create an empty index file
#
cat > index.html << HERE
<html>
<head>
<title>GLAM2SCAN Output</title>
</head>
<body background="bkg.jpg">

<hr>
<h2>GLAM2SCAN Job $jobid</h2>
HERE
#
# get the motif file name and DB file name from first two arguments
#
set i = $#argv
set db = $argv[$i]; @ i--
set aln = $argv[$i]; @ i--
set alph = $argv[$i]; @ i--

#
# set link to database directory unless using uploaded DB
# 
if ($db != "uploaded_db") then
  ln -s /home/simon/db/fasta_databases data
  set db = data/$db
endif

# Get start time for log
set t1 = `date -u '+%d/%m/%y %H:%M:%S'`

#
# run GLAM2SCAN
#
echo "<ul><li>glam2scan $argv[-$i] $alph $aln $db > glam2scan.txt</li></ul><hr>" >> index.html
#
bin/glam2scan $argv[-$i] $alph $aln $db > glam2scan.txt
# Create html output
if ($status == 0) bin/glam2scan2html < glam2scan.txt > glam2scan.html

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
if (-s glam2scan.html || -s glam2scan.txt) then
  echo "<h2>Results</h2><blockquote><ul>" >> index.html
  if (-s glam2scan.html) echo "<li><a href='glam2scan.html'>GLAM2SCAN output as HTML</a></li>" >> index.html
  if (-s glam2scan.txt) echo "<li><a href='glam2scan.txt'>GLAM2SCAN output as plain text</a></li>" >> index.html
  if (-s aln) echo "<li><a href='aln'>input alignment</a></li>" >> index.html
  #if (-s uploaded_db) echo "<li><a href='uploaded_db'>uploaded database</a></li>" >> index.html
  echo "</ul></blockquote><hr>" >> index.html
endif

# Messages section
if (-s stdout.txt || -s stderr.txt) then
  echo "<h2>Messages</h2><blockquote><ul>" >> index.html
  if (-s stdout.txt) echo "<li><a href='stdout.txt'>Processing Messages</a></li>" >> index.html
  if (-s stderr.txt) echo "<li><a href='stderr.txt'>Error Messages</a></li>" >> index.html
  echo "</ul></blockquote><hr>" >> index.html
endif

# End section
echo "</body></html>" >> index.html
