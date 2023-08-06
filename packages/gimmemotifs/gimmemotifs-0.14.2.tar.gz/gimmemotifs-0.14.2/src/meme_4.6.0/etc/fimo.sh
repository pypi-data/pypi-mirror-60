#!/bin/csh

# This file is processed by "make" to create file run by
# the fimo web service.

set dir = `pwd`
set jobid  = `basename $dir`

# create link to binary directory
ln -s /home/simon/bin bin

# get log file
set logfile = /home/simon/LOGS/fimo-log

# get the background 
set bkg = /home/simon/etc/bkg.jpg
if -e $bkg cp $bkg .

#
# create an empty index file
#
cat > index.html << HERE
<html>
<head>
<title>fimo Output</title>
</head>
<body background="bkg.jpg">

<hr>
<h2>fimo Job $jobid</h2>
HERE

#
# get the motif file name and DB file name from first two arguments
#
set motifs = $1; shift
set db = $1; shift

#
# set link to database directory unless using uploaded DB
# 
if ($db != "uploaded_db") then
  ln -s /home/simon/db/fasta_databases data
  set db = data/$db
endif

#
# set up the background file and number of sequences in 
# the db file switches if those local files exist
#
set bfile = ''; set nseqs = ''
if (-e $db.bfile) set bfile = "--bgfile $db.bfile"
if (-e $db.nseqs) set nseqs = "-minseqs `cat $db.nseqs`"

# Get start time for log
set t1 = `date -u '+%d/%m/%y %H:%M:%S'`

#
# run fimo 
#
echo "<ul><li>fimo $bfile $* $motifs $db </li></ul><hr>" >> index.html
#
eval "bin/fimo $bfile $* $motifs $db "

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
  if (-s fimo_out/fimo.html) echo "<li><a href='fimo_out/fimo.html'>FIMO output as HTML</a></li>" >> index.html
  if (-s fimo_out/fimo.xml) echo "<li><a href='fimo_out/fimo.xml'>FIMO output as XML</a></li>" >> index.html
  if (-s fimo_out/fimo.gff) echo "<li><a href='fimo_out/fimo.gff'>FIMO output as GFF</a></li>" >> index.html
  if (-s fimo_out/fimo.wig) echo "<li><a href='fimo_out/fimo.wig'>FIMO output as wiggle track</a></li>" >> index.html
  if (-s fimo_out/fimo.txt) echo "<li><a href='fimo_out/fimo.txt'>FIMO output as plain text</a></li>" >> index.html
  if (-s fimo_out/fimo-to-html.xsl) echo "<li><a href='fimo_out/fimo-to-html.xsl'>XSLT Stylesheet for converting FIMO XML to HTML</a></li>" >> index.html
  if (-s fimo_out/cisml.css) echo "<li><a href='fimo_out/cisml.css'>CSS Stylesheet for displaying FIMO HTML</a></li>" >> index.html
  if (-s motifs) echo "<li><a href='motifs'>input motifs</a></li>" >> index.html
  if (-s uploaded_db) echo "<li><a href='uploaded_db'>uploaded database</a></li>" >> index.html
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
