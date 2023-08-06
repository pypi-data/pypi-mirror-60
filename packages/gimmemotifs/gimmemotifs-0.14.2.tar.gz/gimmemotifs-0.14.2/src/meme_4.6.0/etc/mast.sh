#!/bin/csh

# This file is processed by "make" to create file run by
# the MAST web service.

set dir = `pwd`
set jobid  = `basename $dir`

# create link to binary directory
ln -s /root/bin bin

# get log file
set logfile = /root/LOGS/mast-log

# get the background 
set bkg = /root/etc/bkg.jpg
if -e $bkg cp $bkg .

#
# create an empty index file
#
cat > index.html << HERE
<html>
<head>
<title>MAST Output</title>
</head>
<body background="bkg.jpg">

<hr>
<h2>MAST Job $jobid</h2>
HERE

# Get start time for log
set t1 = `date -u '+%d/%m/%y %H:%M:%S'`

#
# get the motif file name and DB file name from first two arguments
#
set motifs = $1; shift
set db = $1; shift

#
# set link to database directory unless using uploaded DB
# 
if ($db != "uploaded_db") then
  ln -s /root/db/fasta_databases data
  set db = data/$db
endif

#
# set up the background file and number of sequences in 
# the db file switches if those local files exist
#
set bfile = ''; set nseqs = ''
echo "$*" | grep -e '-dna' > /dev/null	# see if -dna given; no bfile if so
if (-e $db.bfile && $status) set bfile = "-bfile $db.bfile"
if (-e $db.nseqs) set nseqs = "-minseqs `cat $db.nseqs`"

#
# run MAST 
#
echo "<ul><li>mast $motifs $db $bfile $* $nseqs -oc . -nostatus</li></ul>" >> index.html
#
set start_time = `/root/etc/timer.sh`
eval "bin/mast $motifs $db $bfile $* $nseqs -oc . -nostatus"
echo "<p>(done in " >> index.html
set time_msg = `/root/etc/timer.sh $start_time`
echo $time_msg >> index.html
echo ")</p><br><hr>" >> index.html

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
if (-s mast.html || -s mast.txt) then
  echo "<h2>Results</h2><blockquote><ul>" >> index.html
  if (-s mast.html) echo "<li><a href='mast.html'>MAST output as HTML</a></li>" >> index.html
  if (-s mast.xml) echo "<li><a href='mast.xml'>MAST output as xml</a></li>" >> index.html
  if (-s mast.txt) echo "<li><a href='mast.txt'>MAST output as txt (format being phased out in next release)</a></li>" >> index.html
  if (-s motifs) echo "<li><a href='motifs'>input motifs</a></li>" >> index.html
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
