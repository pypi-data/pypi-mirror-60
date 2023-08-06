#!/bin/csh

# This file is processed by "make" to create the file
# executed by the GLAM2 web service.

set dir = `pwd`
set jobid  = `basename $dir`

# create link to binary directory
ln -s /root/bin bin

# get log file
set logfile = /root/LOGS/glam2-log

# get the background
set bkg = /root/etc/bkg.jpg
if -e $bkg cp $bkg .

# Get the auxiliary files containing address and description
# for glam2html and put their contents on the glam2 command line
set embed = ""
set address = ""
set description = ""
set dtext = ""
if (-e embed_seqs) then
  set embed = "-M"
endif
if (-e address) then
  set address = "`cat address`"
endif
if (-e description && ! -z description) then
  set description = "`cat description`"
endif
if ("$description" != "") then
  set dtext = "<li><B>Description:</B> $description </li>"
endif

#
# Create an empty index file
#
cat > index.html << HERE
<html>
<head>
<title>GLAM2 Output</title>
</head>
<body background="bkg.jpg">

<hr>
<h2>GLAM2 Job $jobid</h2>
<ul>
<li>glam2 -Q -O . $embed -A '$address' -X '$description' $*</li>
$dtext
</ul>
<hr>
HERE

# Get start time for log
set t1 = `date -u '+%d/%m/%y %H:%M:%S'`
 
# Run GLAM2
bin/glam2 -Q -O . $embed -A "'$address'" -X "'$description'" $*

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
if (-s glam2.xml || -s glam2.html || -s glam2.txt) then
  echo "<h2>Results</h2><blockquote><ul>" >> index.html
  if (-s glam2.xml) echo "<li> <a href='glam2.xml'>GLAM2 output as XML</a> </li>" >> index.html
  if (-s glam2.html) echo "<li> <a href='glam2.html'>GLAM2 output as HTML</a> </li>" >> index.html
  if (-s glam2.txt) echo "<li> <a href='glam2.txt'>GLAM2 output as plain text</a> </li>" >> index.html
  if (-s glam2.meme) echo "<li> <a href='glam2.meme'>GLAM2 output as MEME text format</a> </li>" >> index.html
  if (-s sequences) echo "<li> <a href='sequences'>input sequences</a> </li>" >> index.html
  if (-s uploaded_bfile) echo "<li> <a href='uploaded_bfile'>background Markov model</a> </li>" >> index.html
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
