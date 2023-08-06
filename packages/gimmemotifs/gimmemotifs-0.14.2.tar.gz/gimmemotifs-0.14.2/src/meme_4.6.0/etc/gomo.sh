#!/bin/csh

# This file is processed by "make" to create the file
# executed by the GOMO web service.

set dir = `pwd`
set jobid  = `basename $dir`

# create link to binary directory
ln -s /root/bin bin

# get log file
set logfile = /root/LOGS/gomo-log

# get the background
set bkg = /root/etc/bkg.jpg
if -e $bkg cp $bkg .

# get the path to databases
ln -s /root/db/gomo_databases gomo_dbs
set db_path = gomo_dbs

#
# Create an empty index file
#
cat > index.html << HERE
<html>
<head>
<title>GOMO Output</title>
<style type="text/css">
p {margin-left:50px}
ul {margin-left:50px; padding-left:1em;}
</style>
<script type="text/javascript">
  function show_details() {
    document.getElementById('show').style.display = 'none';
    document.getElementById('details').style.display = 'block';
  }
</script>
</head>
<body background="bkg.jpg">

<hr>
<h2>GOMO Job $jobid</h2>
<div id="show" style="display:block;">
  <p><a href="javascript:show_details()">Show Details</a></p>
</div>
<div id="details" style="display:none;">
HERE

# get input arguments
set options = ()
set motifs = $1; shift
set dbs = ()
while ("$1" != "END_OF_DBS")
  set dbs = ($dbs $1)
  shift
end
# get rid of "END_OF_DBS" marker
shift	

# set main db
set main_db = $dbs[1]

echo "<h2>Input</h2><ul>" >> index.html
echo "<li> <a href='motifs'>Motifs</a> (input file)</li>" >> index.html
#foreach db ($dbs)
#  echo "<li> database : $db </li>" >> index.html
#end
echo "</ul><hr>" >> index.html

echo "<h2>Command</h2>" >> index.html


# set up go term to sequence mapping
set gomap = $main_db.csv

# Get start time for log
set t1 = `date -u '+%d/%m/%y %H:%M:%S'`

# Run AMA
set start_time = `/root/etc/timer.sh`
echo "<p>Scoring database sequences with given motifs using AMA</p>" >> index.html
echo "<ul>" >> index.html
set i = 1
set ama_files = ()
foreach db ($dbs)
  # set up the background file 
  set bfile = $db.bfile
  #set ama_file = ama_$i.cisml; @ i++
  set ama_file = $db.cisml
  set ama_files = ($ama_files $ama_file)
  echo "<li>ama --pvalues --verbosity 1 $motifs $db $bfile > $ama_file</li>" >> index.html
  bin/ama --pvalues --verbosity 1 $motifs $db_path/$db $db_path/$bfile > $ama_file
  set exe_status = $status
  if ($exe_status != 0) then
    rm -f $ama_file
    goto finish_ama
  endif
end
finish_ama:
echo "</ul>" >> index.html
echo "<p>(done in " >> index.html
set time_msg = `/root/etc/timer.sh $start_time`
echo $time_msg >> index.html
echo ")</p><br>" >> index.html
if ($exe_status != 0) goto cleanup

# Run meme2images on motifs to create logos
set start_time = `/root/etc/timer.sh`
echo "<p>Creating motif logos using meme2images </p>" >> index.html
echo "<ul><li>meme2images $motifs logos</li></ul>" >> index.html
bin/meme2images $motifs logos
set exe_status = $status
echo "<p>(done in " >> index.html
set time_msg = `/root/etc/timer.sh $start_time`
echo $time_msg >> index.html
echo ")</p><br>" >> index.html
if ($exe_status != 0) goto cleanup

# Run GOMO on output of AMA and the go terms for the corresponding organism
set start_time = `/root/etc/timer.sh`
echo "<p>Associating GO-terms using GOMO <br>" >> index.html
echo "<ul><li>gomo $* --nostatus --verbosity 1 --oc . --dag go.dag $gomap $ama_files</li></ul>" >> index.html
bin/gomo $* --nostatus --verbosity 1 --oc . --dag $db_path/go.dag --images logos $db_path/$gomap $ama_files
set exe_status = $status
echo "<p>(done in " >> index.html
set time_msg = `/root/etc/timer.sh $start_time`
echo $time_msg >> index.html
echo ")</p><hr>" >> index.html
if ($exe_status != 0) goto cleanup

#
# come here on failure
#
cleanup:

# get rid of the surplus logos
rm -rf logos

# unlink the db path
rm $db_path

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
echo "</div>" >> index.html
# Results section
if (-s gomo.xml || -s gomo.html || -s ama_1.cisml) then
  echo "<h2>Results</h2><ul>" >> index.html
  if (-s gomo.html) echo "<li> <a href='gomo.html'>GOMO output as HTML</a> </li>" >> index.html
  if (-s gomo.xml) echo "<li> <a href='gomo.xml'>GOMO output as XML</a> </li>" >> index.html
  set i = 1
  foreach ama_file ($ama_files)
    set db = $dbs[$i]; @ i++
    if (-s $ama_file) then
      gzip $ama_file
      echo "<li> <a href='$ama_file.gz'>AMA output for $db as XML (gzip compressed)</a> </li>" >> index.html
    endif
  end
  echo "</ul><hr>" >> index.html
endif 

# Messages section
if (-s stdout.txt || -s stderr.txt) then
  echo "<h2>Messages</h2><ul>" >> index.html
  if (-s stdout.txt) echo "<li><a href='stdout.txt'>Processing Messages</a></li>" >> index.html
  if (-s stderr.txt) echo "<li><a href='stderr.txt'>Error Messages</a></li>" >> index.html
  echo "</ul><hr>" >> index.html
endif

# End section
echo "</body></html>" >> index.html
