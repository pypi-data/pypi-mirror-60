#!/bin/csh

# This file is processed by "make" to create the file
# executed by the MEME web service.

set dir = `pwd`
set jobid  = `basename $dir`

# create link to binary directory
ln -s /root/bin bin

# get log file
set logfile = /root/LOGS/meme-log

# get the background
set bkg = /root/etc/bkg.jpg
if -e $bkg cp $bkg .

#
# Create an empty index file
#
cat > index.html << HERE
<html>
<head>
<title>MEME Output</title>
</head>
<body background="bkg.jpg">

<hr>
<h2>MEME Job $jobid</h2>
HERE

# Get start time for log
set t1 = `date -u '+%d/%m/%y %H:%M:%S'`

# Check if we should run the PSP generator
# extract psp options: should all be before the dividing word "meme"
set pspargs = ""
while ("${1}" != "meme")
    set pspargs = "${pspargs} ${1}"
    shift
end
shift

# if there are any PSP arguments, that means we must run the
# PSP generator, otherwise go straight to MEME
if ("${pspargs}" != "") then
    echo "<ul><li>psp-gen " \
	"${pspargs} &gt; priors.psp</li></ul>" >> index.html
    bin/psp-gen ${pspargs} > priors.psp
    set exe_status = $status
else
    set exe_status = 0
endif

# Run MEME
if ($exe_status == 0) then
    echo "<ul><li>meme $* </li></ul><hr>" >> index.html
    bin/meme $* -oc . -nostatus
    set exe_status = $status
endif

# Run MAST on output of MEME and the input sequences
set bfile = ""
if (-s uploaded_bfile) set bfile = " -bfile uploaded_bfile"
if ($exe_status == 0) bin/mast ./meme.html $1 $bfile -oc . -nostatus

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
if (-s negfile || -s meme.xml || -s meme.html || -s meme.txt || -s mast.html) then
  echo "<h2>Results</h2><blockquote><ul>" >> index.html
  if (-s meme.html) echo "<li> <a href='meme.html'>MEME output as HTML</a> </li>" >> index.html
  if (-s meme.txt) echo "<li> <a href='meme.txt'>MEME output as plain text</a> </li>" >> index.html
  if (-s meme.xml) echo "<li> <a href='meme.xml'>MEME output as XML</a> </li>" >> index.html
  if (-s mast.html) echo "<li> <a href='mast.html'>MAST output as HTML</a> </li>" >> index.html
  if (-s mast.xml) echo "<li> <a href='mast.xml'>MAST output as XML</a> </li>" >> index.html
  if (-s mast.txt) echo "<li> <a href='mast.txt'>MAST output as text (format being phased out in next release)</a> </li>" >> index.html
  if (-s sequences) echo "<li> <a href='sequences'>input sequences</a> </li>" >> index.html
  if (-s uploaded_bfile) echo "<li> <a href='uploaded_bfile'>background Markov model</a> </li>" >> index.html
  if (-s negfile) echo "<li> <a href='negfile'>Negative sequences</a> </li>" >> index.html
  if (-s priors.psp) echo "<li> <a href='priors.psp'>Position-specific priors</a> </li>" >> index.html
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
