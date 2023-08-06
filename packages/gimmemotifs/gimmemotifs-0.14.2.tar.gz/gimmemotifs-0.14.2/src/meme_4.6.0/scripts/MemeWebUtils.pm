# File: MemeWebUtils.pm
# Project: Website CGI
# Description: MemeWebUtils.pm made from MemeWebUtils.pm.in by make. Helper functions for CGI pages.

package MemeWebUtils;

use strict;
use warnings;

require Exporter;
our @ISA = qw(Exporter);
our @EXPORT_OK = qw(getnum is_numeric get_alph valid_address valid_meme_version add_status_msg update_status);

use Fcntl;
use HTTP::Request::Common qw(GET);
use XML::Simple;
use HTML::PullParser;
use HTML::Template;

use lib qw(/home/simon/lib/perl);
use CatList qw(load_categories load_entry);

my $template_dir = '/home/simon/web/cgi-bin';
##############################################################################
#          Functions
##############################################################################

#
# Use POSIX strtod to convert a variable to a number.
#
# Used in
# Utils
#
sub getnum {

  use POSIX qw(strtod);
  my $str = shift;
  $str =~ s/^\s+//;
  $str =~ s/\s+$//;
  $! = 0;
  my($num, $unparsed) = strtod($str);
  if (($str eq '') || ($unparsed != 0) || $!) {
      return undef;
  } else {
      return $num;
  } 

} 

#
# Test whether a variable is a number.
#
# Used in
# Utils
#
sub is_numeric { defined &getnum($_[0]) } 

#
# get the alphabet of a string: DNA or PROTEIN
#
# Used in
# Utils
#
sub get_alph
{
  my ($letters) = @_;                # get arguments 
  my ($old, $new, $x);

  $old = length($letters);

  # check against allowed nucleotide letters
  $x = $letters;
  $x =~ tr/ABCDGHKMNRSTUVWY//cd; # delete all letters that aren't a nucleotide letter
  $new = length($x);
  if ($old == $new) { # if nothing was deleted then it has only dna letters
    return("DNA", "");
  } else {
    # check against allowed protein letters
    $x = $letters;
    $x =~ tr/ABCDEFGHIKLMNPQRSTUVWXYZ//cd; # delete all non-protein letters
    $new = length($x);
    if ($old == $new) { # if nothing was deleted then it has only protein letters
      return("PROTEIN", "");
    } else {
      # get the unknown letters
      $x = $letters;
      $x =~ tr/ABCDEFGHIKLMNPQRSTUVWXYZ//d; # delete all known letters
      return("UNRECOGNIZED", $x);
    }
  }
} # get_alph

#
# valid_address
#
# Checks email address syntax and host validity.
# Returns 0 if the address is invalid, 1 on success.
#
# Merged from Validation.txt
#
# Used in
# Utils
#
sub valid_address {
  my($addr) = @_;
  my($domain, $valid);
  return(0) unless ($addr =~ /^[^@]+@([-\w]+\.)+[A-Za-z]{2,4}$/);
  $domain = (split(/@/, $addr))[1];
  $valid = 0; open(DNS, "nslookup -q=mx $domain |") || return(-1);
  while (<DNS>) {
    #my $line = (/^$domain.*mail exchanger/);
    $valid = 1 if (/^$domain.*\s(mail exchanger|internet address)\s=/);
  }
  return($valid);
}

#
# valid_meme_version
#
# Checks a version string to ensure that it should be parsable.
# Return 0 if the version is unknown or unparsable, 1 on success.
#
sub valid_meme_version {
  my ($ver_str) = @_;
  my @ver_strs = split(/\./, $ver_str);
  #check that there is a version number at all
  return 0 unless scalar(@ver_strs) > 0;
  #check that each part of a version number is actually a number
  my @ver_nums = ();
  foreach my $ver_part (@ver_strs) {
    my $ver_num = getnum($ver_part);
    return 0 unless defined $ver_num;
    push(@ver_nums, $ver_num);
  }
  # check the major version number
  if ($ver_nums[0] < 3) {
    return 0; # prior to version 3 is too old
  }
  # get the current version numbers
  my $cur_str = "4.6.0";
  my @cur_nums = split(/\./, $cur_str);
  # compare the current version to the specified
  while (@ver_nums && @cur_nums) {
    my $ver_num = shift(@ver_nums);
    my $cur_num = shift(@cur_nums);
    if ($ver_num > $cur_num) {
      # it's newer, hence unknown
      return 0;
    } elsif ($ver_num < $cur_num) {
      # older
      last;
    }
  }
  #seems to be valid
  return 1;
}


#
# add_status_msg
#
# Adds a message to the message list
# and returns the list. For use with
# update_status.
#
sub add_status_msg {
  my ($msg, $msg_list) = @_;
  push(@$msg_list, {msg => $msg});
  return $msg_list;
}

#
# update_status
#
# Creates or updates the specified status file to contain the
# file list only showing each of the files if they exist and
# the message list.
#
sub update_status {
  my ($output_file, $program, $refresh, $files_list, $msg_list, $status) = @_;

  my @found_files = ();
  foreach my $entry (@$files_list) {
    my $file = $entry->{'file'};
    push(@found_files, $entry) if (defined($file) && -e $file && -s $file);
  }

  my $fh; # I'm suspicious that the 0777 may be too permissive (but that's what we had before)
  sysopen($fh, $output_file, O_CREAT | O_WRONLY, 0777) or die("Failed to open \"$output_file\".");
  my $template = HTML::Template->new(filename => "$template_dir/job_status.tmpl");
  $template->param(program => $program, refresh => $refresh, files => \@found_files, msgs => $msg_list, status => $status);
  print $fh $template->output;
  close($fh) or die("Failed to close \"$output_file\".");
}

#
# Private Function
#
# Provide basic escaping of xml characters in a string.
# Note that does not detect existing escaped characters
# and so they would be re-escaped.
#
sub _fix_xml {
  my $text = shift;
  $text =~ s/&/&amp;/g;
  $text =~ s/</&lt;/g;
  $text =~ s/>/&gt;/g;
  $text =~ s/"/&quot;/g;
  return $text;
}

##############################################################################
#                      Object Methods
##############################################################################

#
# new
#
# Constructor.
#
# Used in
# meme.pl
# fimo.pl
# glam2.pl
# glam2scan.pl
# gomo.pl
# mast.pl
# mcast.pl
#
sub new {
  my $classname = shift;
  my $self = {};
  bless($self, $classname);
  $self->_init(@_);
  return $self;
}

#
# Private Method
#
# _init
#
# Sets the program to the passed value.
#
sub _init {
  my $self = shift;
  die("Expected Utils object") unless ref($self) eq 'MemeWebUtils';
  my ($program, $bin_dir) = @_;
  $program = "" unless defined $program;
  $self->{PROGRAM} = $program;
  $self->{BIN_DIR} = $bin_dir;
  $self->{NERRORS} = 0;
}

#
# get_program
#
# Gets the program name as passed to the constructor.
#
sub get_program {
  my $self = shift;
  die("Expected Utils object") unless ref($self) eq 'MemeWebUtils';
  return $self->{PROGRAM};
}

#
# has_errors
#
# Returns the number of errors that have been detected.
#
# Used in
# meme.pl
# fimo.pl
# glam2.pl
# glam2scan.pl
# gomo.pl
# mast.pl
# mcast.pl
#
sub has_errors {
  my $self = shift;
  die("Expected Utils object") unless ref($self) eq 'MemeWebUtils';
  return $self->{NERRORS};
}

#
# Check to see whether the email address is valid.
#
# Used in
# meme.pl
# fimo.pl
# glam2.pl
# glam2scan.pl
# gomo.pl
# mast.pl
# mcast.pl
#
sub check_address
{
  my $self = shift;
  die("Expected Utils object") unless ref($self) eq 'MemeWebUtils';
  my ($address, $email_contact) = @_;
  my ($status);

  if (!$address) {
    $self->whine(
      "You must include a return e-mail address to receive your results.<br />",
      "Please go back and include one."
    );
  } else {
    $status = valid_address($address);
    if ($status == 0) {
      $self->whine(
        "There is an error in your return email address:<br />",
        "&nbsp;&nbsp;&nbsp;&nbsp; <tt>$address</tt><br />",
        "It is possible that your email address is correct, in which case",
        "the problem may be that your host is behind a firewall and",
        "is consequently not found by the nslookup routines.  Consult with",
        "your systems people to see if you have an nslookup-visible email",
        "address.  If none is available, please send email to <br />",
        "&nbsp;&nbsp;&nbsp;&nbsp; <tt>$email_contact</tt> <br />",
        "mentioning this problem."
      );
    }
  }
} # check_address

#
# Check to see whether the p-value threshold is valid.
#
# Used in
# fimo.pl
# 
sub check_pvalue
{
  my $self = shift;
  die("Expected Utils object") unless ref($self) eq 'MemeWebUtils';
  my ($pvalue) = @_;

  if (! is_numeric($pvalue) || $pvalue < 0 || $pvalue > 1.0) {
    $self->whine(
      "You must use a number between 0 and 1 in the output threshold p-value field."
    );
  }
} # check_pvalue

#
# Check whether a DNA-only option is valid
#
# Used in
# fimo.pl
#
sub check_dna_only
{
  my $self = shift;
  die("Expected Utils object") unless ref($self) eq 'MemeWebUtils';
  my ($alphabet, $option, $text) = @_;

  if ($alphabet ne "DNA") {
    $self->whine("You may only use the '$option' $text.");
  }
} # check_dna_only

#
# Check to see whether the description is valid.
# 
# Used in
# meme.pl
# fimo.pl
# glam2.pl
# glam2scan.pl
# gomo.pl
# mast.pl
# mcast.pl
#
sub check_description
{
  my $self = shift;
  die("Expected Utils object") unless ref($self) eq 'MemeWebUtils';
  my ($description) = @_;
  $description = "" unless defined $description;
  if ($description =~ /[^\w _\-\(\)]/) {
    $self->whine(
      "You may only use letters, numbers, underlines, dashes, blanks and parentheses",
      "in the description field."
    );
  }
} # check_description


#
# get sequence data
#
# Object method.
#
# Get data from a textbox or uploaded file and convert
# it to FASTA format.
#
# Returns $sequences_given, $fasta_seqs
# Uses object global $self->{PROGRAM}.
#
# Used by
# Utils
# meme.pl
# glam2.pl
#
sub get_sequence_data {
  my $self = shift;
  die("Expected Utils object") unless ref($self) eq 'MemeWebUtils';
  my $PROGRAM = $self->{PROGRAM};
  my $BIN_DIR = $self->{BIN_DIR};
  my (
    $data,            # data from textbox, if defined
    $datafile_name,         # open filehandle from CGI.pm, if defined
    $maxsize,            # maximum total sequence size
    $shuffle,            # shuffle sequences if true
    $purge,            # if nonempty options for purge
    $dust,            # if nonempty options for dust
  ) = @_;
  my (
    $fasta_data,        # sequence data in FASTA format
    $alphabet,            # sequence alphabet DNA/PROTEIN
    $nseqs,            # number of sequences
    $min,             # minimum length
    $max,             # maximum length
    $ave,             # average length
    $total,             # total length
    $raw_seqs,
    $cooked_seqs,
    $status,
    $letters,
    $fasta_seqs,
    $getsize_res,
    $error_msg,
    $sequences_given,
    $purgeout
  );
  #file names (FIXME why aren't we using the perl temp file functions?)
  $fasta_seqs = $PROGRAM . "_fasta.seqs.$$"; # $$ is process id
  $getsize_res = $PROGRAM . "_getsize_res.$$";
  $error_msg = $PROGRAM . "_error.$$";
  $sequences_given = 1;
  #return defaults
  $fasta_data = "";
  $alphabet = "UNRECOGNIZED";
  $nseqs = 0;
  $min = 0;
  $max = 0;
  $ave = 0;
  $total = 0;

  # check that sequence data was provided
  if (!$datafile_name && !$data) {
    $self->whine(
      "You haven't entered any sequence data. <br />",
      "If you still wish to submit a query, please go back and enter the",
      "name of a sequence file or the actual sequences."
    );
    $sequences_given = 0;
  }

  # don't allow both datafile and data
  if ($datafile_name && $data) {
    $self->whine(
      "You may not enter <i>both</i> the name of a sequence file and sequences.<br />",
      "If you still wish to submit a query, please go back and erase either",
      "what you have written in the <i>name of a file</i> field or",
      "in the <i>actual sequences</i> field."
    );
    $sequences_given = 0;
  }

  #
  # create a file containing the raw sequences
  #
  if ($sequences_given) {
    # slurp the uploaded file into a scalar if there was no textbox data
    $data = do {local $/; <$datafile_name>} unless ($data);

    # convert to UNIX EOL
    $data =~ s/\r\n/\n/g;        # Windows -> UNIX eol
    $data =~ s/\r/\n/g;            # MacOS -> UNIX eol

    # print raw sequences to a file
    $raw_seqs = $PROGRAM . "_raw_seqs.$$";
    open(SEQS, ">$raw_seqs") || $self->whine("Can't open file $raw_seqs: $!");
    print SEQS "$data\n";
    close (SEQS);
    chmod 0777, $raw_seqs;

    # check that sequences were given
    if ($datafile_name) {
      $_ = `wc $raw_seqs`;
      my @tmp = split (' ');
      if ($tmp[0] == 0) {
        $self->whine(
          "$PROGRAM could not read your sequence file or it is empty. <br />",
          "Make sure the name is correct and that you have read access",
          "to the file."
        );
        $sequences_given = 0;
      }
    }
  } # create raw sequence file

  #
  # convert raw sequences to FASTA format using READSEQ
  #
  if ($sequences_given) {
    $cooked_seqs = $PROGRAM . "_cooked_seqs.$$";
    $status = system
        ("$BIN_DIR/readseq -a -f=8 $raw_seqs 1>$cooked_seqs 2>$error_msg");
    my $error = `cat $error_msg`; 
    unlink "$error_msg";
    if ($status) {
      $self->whine(
        "An error occurred when the READSEQ program attempted to convert".
        "your dataset to FASTA format.<br />",
        "READSEQ returned: <pre>$error</pre>"
      );
      $sequences_given = 0;
    }
  } # convert to FASTA

  #
  # get information on sequences
  #
  if ($sequences_given) {
    my($getsize1, $getsize2);

    # Run the 'getsize' program to get information on the raw sequence data.
    $getsize_res = $PROGRAM . "_getsize.$$";
    $status = system
        ("$BIN_DIR/getsize $raw_seqs 1>$getsize_res 2>/dev/null");
    chop($getsize1 = `cat $getsize_res`);
    unlink $getsize_res;
    ($nseqs, $min, $max, $ave, $total, $letters) = split (' ', "$getsize1");

    # Run the 'getsize' program to get information on converted data; will
    # be unchanged if it is FASTA
    $status = system
        ("$BIN_DIR/getsize -nd $cooked_seqs 1>$getsize_res 2>$error_msg");
    my $error = `cat $error_msg`;
    unlink $error_msg;
    if ($error || $status) {
      $self->whine(
        "After converting to FASTA format using the READSEQ program,",
        "the following errors in your dataset were detected:<br /><pre>$error</pre>",
        "<br />Make sure all your sequences are in the same format since READSEQ",
        "assumes that all sequences are in the same format as the first sequence.",
      );
      unlink $getsize_res;
      $sequences_given = 0;
    } else {
      # get final information
      chop($getsize2 = `cat $getsize_res`);
      unlink $getsize_res;
      ($nseqs, $min, $max, $ave, $total, $letters) = split (' ', "$getsize2");
      # Use original dataset if it is FASTA
      if ($getsize1 eq $getsize2) {
        #print "<p>Using original dataset<p>";
        my $error = `cp $raw_seqs $cooked_seqs`;
        if ($error ne "") {
          $self->whine(
            "An error occurred while trying to copy your data.<br />",
            "cp returned: <pre>$error</pre>"
          );
          $sequences_given = 0;
        }
      }
    }
  } # get sequence info

  #
  # final checks
  #
  if ($sequences_given) {
    # check for problem reading the dataset
    if ($nseqs <= 0) {
      $self->whine(
        "Your dataset appears to be in a format that $PROGRAM does not recognize.",
        "<br /> Please check to be sure that your data is",
        "<a href=\"../help_format.html\">formatted</a> properly."
      );
      $self->copy_stdout("$raw_seqs");
      $sequences_given = 0;
    }
    # check for bad sequences
    if ($nseqs > 0 && $min == 0) {
      $self->whine(
        "Your dataset appears to contain one or more zero-length sequences.",
        "<br /> Please check to be sure that your data is",
        "<a href=\"../help_format.html\"> formatted</a> properly."
      );
      $sequences_given = 0;
    }
    # Make sure the data was in FASTA format or got converted correctly.
    if ($self->{NERRORS} == 0 && $nseqs == 0 ) {
      $self->whine(
        "$PROGRAM was unable to read your sequence data. <br />",
        "Please check to be sure that your sequence data is",
        "<a href=\"../help_format.html\"> formatted</a> properly.  <br />",
        "If you are still having trouble, you can try to convert",
        "your data to",
        "<a href=\"http://dot.imgen.bcm.tmc.edu:9331/seq-util/Help/example_input.html\">",
        "FASTA format</a> using the",
        "<a href=\"http://dot.imgen.bcm.tmc.edu:9331/seq-util/readseq.html\">",
        "ReadSeq</a> program and then resubmit it."
      );
      $sequences_given = 0;
    }
    # Make sure there isn't too much data.
    if ($total > $maxsize) {
      $self->whine(
        "The data you have entered contains more than $maxsize characters.",
        "$PROGRAM cannot process it at this time. <br />",
        "Please submit a smaller dataset."
      );
    }
  } # final checks

  #
  # prepare sequences and alphabet and do filtering if requested
  #
  if ($sequences_given) {
    # shuffle sequences if requested
    if ($shuffle) {
      # $fasta_data = `$BIN_DIR/fasta-shuffle-letters -tod < $cooked_seqs`;
      $status = system("$BIN_DIR/fasta-shuffle-letters -tod < $cooked_seqs 1>$cooked_seqs.shuffled 2>$error_msg");
      my $error = `cat $error_msg`;
      unlink $error_msg;
      if ($error || $status) {
        $self->whine(
          "After shuffling, the following errors resulted:<br /><pre>$error</pre>",
          "<br />Please check your sequences."
        );
      }
      `mv $cooked_seqs.shuffled $cooked_seqs`;
    }
    $alphabet = get_alph($letters);
    # here alphabet is "DNA" or "PROTEIN" unless error in input
    my $dust_input = $cooked_seqs; # changes if $purge
    if ($purge) {
      my $purge_opts = "";
      my $purgemethod = "b"; # BLAST default for protein
      # purge names output as <infile>.e<N> where <N> is score
      if ($alphabet eq "DNA") {
        $purge_opts = "-n"; # signal DNA to purge
        $purgemethod = "e"; # exahustive search for DNA
      }
      $purgeout = $cooked_seqs.".$purgemethod".$purge;
      $status = system("$BIN_DIR/purge $cooked_seqs $purge $purge_opts 2>$error_msg");
      my $error = `cat $error_msg`; unlink $error_msg;
      if ($error || $status) {
        $self->whine("From purge, the following errors resulted:<br /><pre>$error</pre>");
      }
      $dust_input = $purgeout;
    }
    # now do dust: if $purgeout exists, use it otherwise use $cooked_seqs
    my $dustout = "";
    if ($dust) {
      $self->whine ("dust is only good for DNA") unless ($alphabet eq "DNA");
      $dustout =  $cooked_seqs.".dust";
      $status = system("$BIN_DIR/dust $dust_input $dust 1>$dustout 2>$error_msg");
      my $error = `cat $error_msg`; unlink $error_msg;
      if ($error || $status) {
        $self->whine("From dust, the following errors resulted:<br /><pre>$error</pre>");
      }
    }
    if ($dustout) {
      $fasta_data = `cat $dustout`;
    } elsif (defined $purgeout) {
      $fasta_data = `cat $purgeout`;
    } else {
      $fasta_data = `cat $cooked_seqs`;
    }
    my $bad_symbols;
    ($alphabet, $bad_symbols) = get_alph($letters);
    if ($bad_symbols) {
      my @bad_lines = $self->find_bad_sequence_data($bad_symbols, $fasta_data);
      $self->whine(
        "Your sequences contained the following unrecognized letters: $bad_symbols.<br/>",
        "The unrecognized letters occurred in the following locations:",
        @bad_lines,
        "<br/>",
        "Please convert your sequences to one of the recognized sequence",
        "<a href=\"../help_alphabet.html\">alphabets</a>."
      );
    }
  }# sequences given

  # clean up
  unlink $raw_seqs if $raw_seqs;
  unlink $cooked_seqs if $cooked_seqs;
  unlink $purgeout if $purgeout;

  return($fasta_data, $alphabet, $nseqs, $min, $max, $ave, $total);
} # get_sequence_data

#
# get sequence data
#
# Object method.
#
# Get data from a textbox or uploaded file in FASTA format
#
# Returns $sequences_given, $fasta_seqs
# Uses object global $self->{PROGRAM}.
#
# meme-seq.pl
#

sub get_fasta_data {
  my $self = shift;
  die("Expected Utils object") unless ref($self) eq 'MemeWebUtils';
  my $PROGRAM = $self->{PROGRAM};
  my $BIN_DIR = $self->{BIN_DIR};
  my (
    $data,            # data from textbox, if defined
    $datafile_name,   # open filehandle from CGI.pm, if defined
    $expected_alphabet, # if defined, string of only accepted sequence letters
    $expected_alphabet_name # if defined name of alphabet
  ) = @_;
  my (
    $alphabet,            # sequence alphabet DNA/PROTEIN
    $nseqs,            # number of sequences
    $min,             # minimum length
    $max,             # maximum length
    $ave,             # average length
    $total,             # total length
    $raw_seqs,
    $status,
    $letters,
    $fasta_seqs,
    $getsize_res,
    $error_msg,
    $sequences_given
  );
  #file names (FIXME why aren't we using the perl temp file functions?)
  $fasta_seqs = $PROGRAM . "_fasta.seqs.$$"; # $$ is process id
  $getsize_res = $PROGRAM . "_getsize_res.$$";
  $error_msg = $PROGRAM . "_error.$$";
  $sequences_given = 1;
  #return defaults
  $alphabet = "UNRECOGNIZED";
  $nseqs = 0;
  $min = 0;
  $max = 0;
  $ave = 0;
  $total = 0;

  # check that sequence data was provided
  if (!$datafile_name && !$data) {
    $self->whine(
      "You haven't entered any sequence data. <br />",
      "If you still wish to submit a query, please go back and enter the",
      "name of a sequence file or the actual sequences."
    );
    $sequences_given = 0;
  }

  # don't allow both datafile and data
  if ($datafile_name && $data) {
    $self->whine(
      "You may not enter <i>both</i> the name of a sequence file and sequences.<br />",
      "If you still wish to submit a query, please go back and erase either",
      "what you have written in the <i>name of a file</i> field or",
      "in the <i>actual sequences</i> field."
    );
    $sequences_given = 0;
  }

  #
  # create a file containing the raw sequences
  #
  if ($sequences_given) {
    # slurp the uploaded file into a scalar if there was no textbox data
    $data = do {local $/; <$datafile_name>} unless ($data);

    # convert to UNIX EOL
    $data =~ s/\r\n/\n/g;        # Windows -> UNIX eol
    $data =~ s/\r/\n/g;            # MacOS -> UNIX eol

    # print raw sequences to a file
    $raw_seqs = $PROGRAM . "_raw_seqs.$$";
    open(SEQS, ">$raw_seqs") || $self->whine("Can't open file $raw_seqs: $!");
    print SEQS "$data\n";
    close (SEQS);
    chmod 0777, $raw_seqs;

    # check that sequences were given
    if ($datafile_name) {
      my $filesize = -s "$raw_seqs";
      if (!$filesize) {
        $self->whine(
          "$PROGRAM could not read your sequence file or it is empty. <br />",
          "Make sure the name is correct and that you have read access",
          "to the file."
        );
        $sequences_given = 0;
      }
    }
  } # create raw sequence file


  #
  # get information on sequences
  #
  if ($sequences_given) {
    my($getsize1, $getsize2);

    # Run the 'getsize' program to get information on the raw sequence data.
    $getsize_res = $PROGRAM . "_getsize.$$";
    $status = system
        ("$BIN_DIR/getsize $raw_seqs 1>$getsize_res 2>$error_msg");
    my $error = `cat $error_msg`;
    unlink $error_msg;
    if ($error || $status) {
      $self->whine(
        "Check your FASTA sequences. ",
        "The following errors in your dataset were detected:<br /><pre>$error</pre>",
      );
    }
    chop($getsize1 = `cat $getsize_res`);
    unlink $getsize_res;
    ($nseqs, $min, $max, $ave, $total, $letters) = split (' ', "$getsize1");
    # if we have an expected alphabet, whine if a letter isn't in it
    # in any sequence (case independent)
    $expected_alphabet_name = "expected" unless $expected_alphabet_name;
    $self->whine("Check your FASTA sequences: they contain at least one<br>".
		 "character not in the $expected_alphabet_name alphabet<br>".
		 "(allowed characters: `$expected_alphabet')."
		 )
	if ($expected_alphabet && $letters !~ m/^[$expected_alphabet]+$/i);
  }

  #
  # final checks
  #
  if ($sequences_given) {
    # check for problem reading the dataset
    if ($nseqs <= 0) {
      $self->whine(
        "Your dataset appears to be in a format that $PROGRAM does not recognize.",
	"<br /> Please check to be sure that your data is in ",
        "<a href=\"../help_format.html\">FASTA</a> format; here is your input:"
      );
      $self->copy_stdout("$raw_seqs");
      $sequences_given = 0;
    }
    # check for bad sequences
    if ($nseqs > 0 && $min == 0) {
      $self->whine(
        "Your dataset appears to contain one or more zero-length sequences.",
        "<br /> Please check to be sure that your data is",
        "<a href=\"../help_format.html\"> formatted</a> properly."
      );
      $sequences_given = 0;
    }
    # Make sure the data was in FASTA format or got converted correctly.
    if ($self->{NERRORS} == 0 && $nseqs == 0 ) {
      $self->whine(
        "$PROGRAM was unable to read your sequence data. <br />",
        "Please check to be sure that your sequence data is in correct",
        "<a href=\"../help_format.html\">FASTA</a> format.  <br />",
        "If you are still having trouble, you can try to convert",
        "your data to",
        "<a href=\"http://dot.imgen.bcm.tmc.edu:9331/seq-util/Help/example_input.html\">",
        "FASTA format</a> using the",
        "<a href=\"http://dot.imgen.bcm.tmc.edu:9331/seq-util/readseq.html\">",
        "ReadSeq</a> program and then resubmit it."
      );
      $sequences_given = 0;
    }
  } # final checks

  #
  # prepare sequences and alphabet and do filtering if requested
  #

  return($data, $alphabet, $nseqs, $min, $max, $ave, $total);
} # get_fasta_data


#
# Get actual name of the database to search along with
# other information about it.
#
# Uses global $PROGRAM
#
# Used by
# fimo.pl
# glam2scan.pl
# gomo.pl
# mast.pl
# mcast.pl
#
sub get_db_name {
  my $self = shift;
  die("Expected Utils object") unless ref($self) eq 'MemeWebUtils';
  my $PROGRAM = $self->{PROGRAM};
  my (
    $motif_alphabet,    # motif alphabet
    $upload_db_name,    # name of uploaded db file
    $max_upload_size,   # maximum size of the uploaded file
    $translate_dna,    # scan DNA with protein motifs
    $short_dna_only,    # don't allow DNA search of long sequences
    $database_index,    # index of databases
    $database_id        # id of database
  ) = @_;
  my (
    $db,         # full name of db file
    $uploaded_data,    # contents of uploaded file
    $db_alphabet,    # local/PROTEIN/DNA
    $target_alphabet,    # alphabet of db
    $db_root,         # db file name w/o extension
    $prot_db,         # protein version exists
    $nuc_db,         # DNA version exists
    $short_seqs,    # sequences are all "short"
    $db_menu_name,    # db name for menus
    $db_long_name,    # db name for documentation
    $db_descr,         # text for verification message
    $prom_start,    # start of promoter (gomo)
    $prom_end,        # end of promoter (gomo)
    @extra_dbs        # extra databases (gomo)
  );    # return values

  # get available versions of database
  if ($upload_db_name eq "") { # local database
    $db_alphabet = "local";
    #attempt to load the entry
    eval {
      ($db_root, $prot_db, $nuc_db, $short_seqs, $db_menu_name, $db_long_name, $prom_start, $prom_end, @extra_dbs) =
          load_entry($database_index, $database_id);
    };
    if ($@) {
      #loading most likely failed because they didn't select a database
      $self->whine(
        "You must specify a supported database or a database to upload.<br />",
        "Please go back and specify one."
      );
    }
    $db_descr = "";
  } else { # uploaded database
    $db_root = $upload_db_name;
    # check that name doesn't contain quotes
    if ($db_root =~ /['`"]/) {
      $self->whine("Uploaded database file name may not contain quote characters.");
    }
    my ($nseqs, $min, $max, $ave, $total);
    ($uploaded_data, $db_alphabet, $nseqs, $min, $max, $ave, $total) =
        $self->get_sequence_data("", $upload_db_name, $max_upload_size, 0);
    $prot_db = ($db_alphabet eq "PROTEIN") ? 1 : 0;
    $nuc_db = ($db_alphabet eq "DNA") ? 1 : 0;
    $short_seqs = 1;                # allow search 
    $db_descr = "  <li>Database type: <b>$db_alphabet</b></li>\n".
    "<li>Database sequences: <b>$nseqs</b></li>\n".
    "<li>Database size: <b>$total</b></li>";
    #does this mean there are no extra dbs? because the user uploaded this db? I'm not certain
    @extra_dbs = ();
  }
  my $i;
  my @extra_files = ();
  while (@extra_dbs) {
    push(@extra_files, shift(@extra_dbs) . ".na");
    shift(@extra_dbs); #skip description
  }
  # get desired sequence alphabet
  $target_alphabet = ($motif_alphabet eq "PROTEIN" && !$translate_dna) ? "PROTEIN" : "DNA";

  # set actual name of database to search
  if ($db_alphabet eq "local") {
    $db = $db_root;
    if ($target_alphabet eq "DNA" && $nuc_db) {
      if ($short_dna_only && !($short_seqs)) {
        $self->whine("The DNA sequences in database '$db_menu_name' are too long for searching by $PROGRAM.");
      } else {
        $db .= ".na";
      }
    } elsif ($target_alphabet eq "PROTEIN" && $prot_db) {
      $db .= ".aa";
    } elsif (defined $db_root) {
      $self->whine("There is no $target_alphabet version of database '$db_menu_name'.");
    }
  } else {
    if ($target_alphabet eq $db_alphabet) {
      $db = "uploaded_db";
    } else {
      $self->whine("The uploaded database '$db_root' seems to be $db_alphabet but should be $target_alphabet.");
    }
  }

  return($db, $uploaded_data, $db_alphabet, $target_alphabet, $db_root, $prot_db,
    $nuc_db, $short_seqs, $db_menu_name, $db_long_name, $db_descr, \@extra_files);
} # get_db_name

#
# Upload the file containing motifs and return data in a scalar.
# Converts to UNIX EOL.  Checks that the file is not empty.
# 
# Returns $motif_data.
#
# Used by
# fimo.pl
# glam2scan.pl
# gomo.pl
# mast.pl
# mcast.pl
#
sub upload_motif_file {
  my $self = shift;
  die("Expected Utils object") unless ref($self) eq 'MemeWebUtils';
  my $PROGRAM = $self->{PROGRAM};
  my (
    $motif_file_name,        # (raw) uploaded motif file
    $inline_motifs          # contains inline motifs if defined (input)
  ) = @_;
  my $motif_data = $inline_motifs;

  # check that name doesn't contain quotes
  if ($motif_file_name =~ /['`"]/) {
    $self->whine("Uploaded motif file name may not contain quote characters.");
  }

  # slurp the uploaded file into a scalar if there was no inline data
  $motif_data = do {local $/; <$motif_file_name>} unless ($motif_data);

  # convert to UNIX EOL
  $motif_data =~ s/\r\n/\n/g;        # Windows -> UNIX eol
  $motif_data =~ s/\r/\n/g;        # MacOS -> UNIX eol

  #
  # check that motif file was found and not empty
  #
  unless ($motif_data =~ /\W+/) {
    $self->whine("Your motif/alignment file $motif_file_name was not found or was empty.  Please check its name and retry.");
    $motif_data = "";
  }

  return($motif_data);
} # upload_motif_file

#
# Check the validity of a MEME file.
#
# Returns $motifs_found, $motif_alphabet, $nmatrices and $total_cols
# 
# Used by
# fimo.pl
# gomo.pl
# mast.pl
# mcast.pl
#
sub check_meme_motifs {
  my $self = shift;
  die("Expected Utils object") unless ref($self) eq 'MemeWebUtils';
  my $BIN_DIR = $self->{BIN_DIR};
  my (
    $type,            # "mast" or "meme-io"
    $motif_data          # string containing motifs
  ) = @_;
  my ($motifs_found, $motif_alphabet, $total_cols, $nmatrices, $version);
  my ($alphabet);
  my $version_hdr_re = 'MEME\s+version\s+(\S+)';
  my $alph_hdr_re = 'ALPHABET=\s*(\S+)';
  my $strand_hdr_re = 'strands:';
  my $motif_hdr_re = 'letter-probability matrix:\s+alength=\s+\d+\s+w=\s+(\d+)';

  # process meme-io type file
  if ($type eq "meme-io") {
    # first try parsing as XML
    ($motifs_found, $motif_alphabet, $nmatrices, $total_cols) =
        $self->check_meme_motifs_as_xml($motif_data);

    if (!$motifs_found) {
      # second try parsing as HTML
      ($motifs_found, $motif_alphabet, $nmatrices, $total_cols) =
          $self->check_meme_motifs_as_html($motif_data);
    }

    # otherwise, try parsing as HTML or text
    if (!$motifs_found) {
      my @widths;
      # check that MEME version given
      ($version) = ($motif_data =~ /$version_hdr_re/);
      $self->whine("Can't find MEME version in motif file.<br />") unless ($version);
      # get the alphabet
      ($alphabet) = ($motif_data =~ /$alph_hdr_re/);
      chop($_ = `$BIN_DIR/alphtype $alphabet 2>&1`);
      $motif_alphabet = $_;                     # DNA/PROTEIN
      # check if strands given for DNA
      if ($motif_alphabet eq 'ACGT') { #what is strands actually used for?! AFAIK nothing actually uses it.
        my ($strands) = ($motif_data =~ /$strand_hdr_re/);
        $self->whine("Can't find 'strands:' in motif file.<br />") unless ($strands);
      }
      # get the number of motifs, total columns
      $nmatrices = @widths = ($motif_data =~ /$motif_hdr_re/g);
      $total_cols = eval(join "+", @widths);
      $motifs_found = ($nmatrices > 0);
    }

  } 

  if ($motif_alphabet ne "PROTEIN" and $motif_alphabet ne "DNA") {
    $self->whine("Illegal alphabet: $motif_alphabet");
    $motifs_found = 0;
  }

  return($motifs_found, $motif_alphabet, $nmatrices, $total_cols);

} # check_meme_motifs 

#
# Private Method
#
# Check the validity of a MEME XML file.
#
# Returns $motifs_found, $motif_alphabet, $num_motifs and $total_motif_columns
# 
# Used by
# Utils
#
sub check_meme_motifs_as_xml {
  my $self = shift;
  die("Expected Utils object") unless ref($self) eq 'MemeWebUtils';
  my $BIN_DIR = $self->{BIN_DIR};

  my $motif_data = pop @_;
  my ($motifs_found, $motif_alphabet, $num_motifs, $total_motif_columns);
  my $ref = eval { XMLin($motif_data, KeepRoot => 1) }; # Try parsing as XML

  if ($@) {
    # Parsing as XML failed.
    $motifs_found = 0;
  }
  else {
    # Parsing as XML succeded.
    # Check that this is a MEME XML file.
    my $alphabet = $ref->{'MEME'}->{'training_set'}->{'alphabet'}; 
    if ($alphabet) {
      # Is a MEME XML file
      $motifs_found = 1;
      my $letters = $alphabet->{'letter'};
      my @letters;
      while (my ($key, $letter) = each %$letters) {
        push @letters, "$letter->{'symbol'}";
      }
      @letters = sort @letters;
      my $alphabet_string = join '', @letters;
      chop($motif_alphabet = `$BIN_DIR/alphtype $alphabet_string 2>&1`);
      
      if ($motif_alphabet ne "PROTEIN" and $motif_alphabet ne "DNA") {
        $self->whine("Untranslatable alphabet string in XML: $alphabet_string");
      }

      my $model = $ref->{'MEME'}->{'model'};
      $num_motifs = $model->{'nmotifs'};
      my $motifs = $ref->{'MEME'}->{'motifs'}->{'motif'};
      $total_motif_columns = 0;
      while (my ($key, $motif) = each %$motifs) {
        $total_motif_columns += $motif->{'width'};
      }
    }
    else {
      # Is not a MEME XML file
      $motifs_found = 0;
    }
  }
  return($motifs_found, $motif_alphabet, $num_motifs, $total_motif_columns);
} # check_meme_motifs_as_xml

#
# Private Method
#
# Check the validity of a MEME HTML file.
#
# Returns $motifs_found, $motif_alphabet, $num_motifs and $total_motif_columns
# 
# Used by
# Utils
#
sub check_meme_motifs_as_html {
  my $self = shift;
  die("Expected Utils object") unless ref($self) eq 'MemeWebUtils';
  my $BIN_DIR = $self->{BIN_DIR};
  my $motif_data = pop @_;
  my ($motifs_found, $motif_alphabet, $num_motifs, $total_motif_columns);
  my $motif_hdr_re = 'letter-probability matrix:\s+alength=\s+\d+\s+w=\s+(\d+)';

  my $p = HTML::PullParser->new(doc => \$motif_data, start => 'attr', report_tags => qw(input));
  my $token = $p->get_token;
  while ($token) {
    my $hashref = @$token[0]; 
    my %attrs = %$hashref;
    if (exists($attrs{"type"}) && $attrs{"type"} =~ m/^hidden$/i && exists($attrs{"name"}) && exists($attrs{"value"})) {
      my $name = $attrs{"name"};
      my $value = $attrs{"value"};
      if ($name =~ m/^nmotifs$/i) {
        $num_motifs = int($value);
        if ($num_motifs <= 0) {
          $self->whine("The number of motifs was smaller than expected: $value");
        }
      } elsif ($name =~ m/^alphabet$/i) {
    chop($motif_alphabet = `$BIN_DIR/alphtype $value 2>&1`);
    if ($motif_alphabet ne "PROTEIN" and $motif_alphabet ne "DNA") {
      $self->whine("Untranslatable alphabet string in HTML: $value");
    }
      } elsif ($name =~ m/^pspm\d+$/i) {
        my $width = int($value =~ m/letter-probability matrix:\s+alength=\s+\d+\s+w=\s+(\d+)/i);
        if (defined $total_motif_columns) {
          if ($width != $total_motif_columns) {
            $self->whine("$name has a different width ($width) to the expected ($total_motif_columns)");
          }
        } else {
          $total_motif_columns = $width;
        }
      } 
    }
    $token = $p->get_token;
  }
  if (defined $num_motifs && defined $motif_alphabet && defined $total_motif_columns) {
    $motifs_found = 1;
  } else {
    $motifs_found = 0;
  }

  return($motifs_found, $motif_alphabet, $num_motifs, $total_motif_columns);
} # check_meme_motifs_as_html

#
# Private Method
#
# send a verification message
#
# Uses global $PROGRAM
#
# Used by
# Utils
#
sub send_verification
{
  my $self = shift;
  die("Expected Utils object") unless ref($self) eq 'MemeWebUtils';
  my $PROGRAM = $self->{PROGRAM};
  my (
    $address,            # to
    $from,            # to
    $jobid,            # from opal
    $message             # message
  ) = @_;

  my $sendmail = "/usr/lib/sendmail -t";

  my $content = "To: " . $address . "\n";
  $content .= "From: $from\n";
  $content .= "Reply-to: $from\n";
  $content .= "Subject: $PROGRAM Submission Information (job $jobid)\n";
  $content .= "Content-type: text/html\n\n";
  $content .= "<hr>This is an auto-generated response to your job submission.<br />\n\n";
  $content .= $message;

  open(SENDMAIL, "|$sendmail") or $self->whine("Can't open sendmail.<br />");
  print SENDMAIL $content;
  close SENDMAIL;
} # send_verification

#
# make form header
# 
# Used by
# meme.pl
# fimo.pl
# glam2.pl
# glam2scan.pl
# gomo.pl
# mast.pl
# mcast.pl
#
sub make_form_header {
  my $self = shift;
  die("Expected Utils object") unless ref($self) eq 'MemeWebUtils';
  my $PROGRAM = $self->{PROGRAM};
  my ($program, $form_type, $optional_css, $indent_lvl, $tab) = @_;
  $indent_lvl = 0 unless $indent_lvl;
  $tab = "\t" unless $tab;
  my $indent = $tab x $indent_lvl;

  my $content = 
      $indent."<!DOCTYPE html>\n".
      $indent."<html>\n".
      $indent.$tab."<head>\n".
      $indent.$tab.$tab."<title>$program - $form_type </title>\n".
      $indent.$tab.$tab."<!-- provide relative path to html directory (parent of cgi-bin) -->\n".
      $indent.$tab.$tab."<script language=\"javascript\" type=\"text/javascript\">var html_path = \"../\"</script>\n".
      $indent.$tab.$tab."<script src=\"../check-submission-form.js\" type=\"text/javascript\"></script>\n".
      $indent.$tab.$tab."<script src=\"../tomtom.js\" type=\"text/javascript\"></script>\n".
      $indent.$tab.$tab."<link href=\"../doc/meme-suite.css\" rel=\"stylesheet\" type=\"text/css\" />\n".
      $indent.$tab.$tab."<link rel=\"icon\" type=\"image/png\" href=\"../images/memesuite_icon.png\">" .
      $indent.$tab.$tab."<link rel=\"shortcut icon\" type=\"image/x-icon\" href=\"../images/memesuite_icon.ico\">" .
      $indent.$tab.$tab."<!-- provide function for clearing upload field -->\n".
      $indent.$tab.$tab."<script> function clearFileInputField(tagId) { document.getElementById(tagId).innerHTML = document.getElementById(tagId).innerHTML; } </script>\n";
  if ($optional_css) {
      $content .=
          $indent.$tab.$tab."<style>\n".
          $optional_css.
          $indent.$tab.$tab."</style>\n";
  }
  $content .=
      $indent.$tab."</head>\n";

 return($content);
} # make_form_header

#
# make submission form tailer
#
# Used by
# meme.pl
# fimo.pl
# glam2.pl
# glam2scan.pl
# gomo.pl
# mast.pl
# mcast.pl
#
sub make_submission_form_tailer {
  my $self = shift;
  die("Expected Utils object") unless ref($self) eq 'MemeWebUtils';
  my $PROGRAM = $self->{PROGRAM};
  my ($indent_lvl, $tab) = @_;
  $indent_lvl = 0 unless $indent_lvl;
  $tab = "\t" unless $tab;
  my $indent = $tab x $indent_lvl;
  my $content = 
      $indent.$tab.$tab.$tab.$tab.$tab.$tab."<script src=\"../template-footer.js\" type=\"text/javascript\" ></script>\n".
      $indent.$tab.$tab.$tab.$tab.$tab."</div>\n".
      $indent.$tab.$tab.$tab.$tab."</td>\n".
      $indent.$tab.$tab.$tab."</tr>\n".
      $indent.$tab.$tab."</table>\n".
      $indent.$tab."</body>\n".
      $indent."</html>\n";

  return($content);
} # make_submission_form_tailer

#
# make submissiom form top: program name, logo, description
#
# Used by
# meme.pl
# fimo.pl
# glam2.pl
# glam2scan.pl
# gomo.pl
# mast.pl
# mcast.pl
#
sub make_submission_form_top {
  my $self = shift;
  die("Expected Utils object") unless ref($self) eq 'MemeWebUtils';
  my $PROGRAM = $self->{PROGRAM};
  my ($action, $logo, $alt, $description, $indent_lvl, $tab) = @_;
  my ($content);

  $indent_lvl = 0 unless $indent_lvl;
  $tab = "\t" unless $tab;

  my $indent = $tab x $indent_lvl;

  $content = 
      $indent."<table class=\"maintable\">\n".
      $indent.$tab."<tr>\n".
      $indent.$tab.$tab."<td class=\"menubase\">\n".
      $indent.$tab.$tab.$tab."<div id=\"menu\">\n".
      $indent.$tab.$tab.$tab.$tab."<script src=\"../meme-suite-menu.js\" type=\"text/javascript\"></script>\n".
      $indent.$tab.$tab.$tab."</div>\n".
      $indent.$tab.$tab."</td>\n".
      $indent.$tab.$tab."<td class=\"maintablewidth\">\n".
      $indent.$tab.$tab.$tab."<div id=\"main\">\n".
      $indent.$tab.$tab.$tab.$tab."<noscript>\n".
      $indent.$tab.$tab.$tab.$tab.$tab."<h1>MEME Suite</h1>\n".
      $indent.$tab.$tab.$tab.$tab.$tab."The MEME Suite web application requires the use of JavaScript<br />\n".
      $indent.$tab.$tab.$tab.$tab.$tab."Javascript doesn't seem to be available on your browser.\n".
      $indent.$tab.$tab.$tab.$tab."</noscript>\n".
      $indent.$tab.$tab.$tab.$tab."<form enctype=\"multipart/form-data\" method=\"POST\" action=\"$action\">\n".
      $indent.$tab.$tab.$tab.$tab.$tab."<table>\n".
      $indent.$tab.$tab.$tab.$tab.$tab.$tab."<col width=\"20%\">\n".
      $indent.$tab.$tab.$tab.$tab.$tab.$tab."<tr>\n".
      $indent.$tab.$tab.$tab.$tab.$tab.$tab.$tab."<td width=\"350\" valign=\"top\">\n".
      $indent.$tab.$tab.$tab.$tab.$tab.$tab.$tab.$tab."<img src=\"$logo\" alt=\"$alt\"><br />\n".
      $indent.$tab.$tab.$tab.$tab.$tab.$tab.$tab.$tab."<center>\n".
      $indent.$tab.$tab.$tab.$tab.$tab.$tab.$tab.$tab.$tab."Version 4.6.0\n".
      $indent.$tab.$tab.$tab.$tab.$tab.$tab.$tab.$tab."</center>\n".
      $indent.$tab.$tab.$tab.$tab.$tab.$tab.$tab."</td>\n".
      $indent.$tab.$tab.$tab.$tab.$tab.$tab.$tab."<td align=\"left\" valign=\"bottom\">\n".
      $indent.$tab.$tab.$tab.$tab.$tab.$tab.$tab.$tab."<p align=\"justify\">\n".
      $description.
      $indent.$tab.$tab.$tab.$tab.$tab.$tab.$tab.$tab."</p>\n".
      $indent.$tab.$tab.$tab.$tab.$tab.$tab.$tab."</td>\n".
      $indent.$tab.$tab.$tab.$tab.$tab.$tab."</tr>\n".
      $indent.$tab.$tab.$tab.$tab.$tab."</table>\n";

  return($content);
} # make_submission_form_top

#
# make submission form bottom
#
# Used by
# meme.pl
# fimo.pl
# glam2.pl
# glam2scan.pl
# gomo.pl
# mast.pl
# mcast.pl
#
sub make_submission_form_bottom {
  my $self = shift;
  die("Expected Utils object") unless ref($self) eq 'MemeWebUtils';
  my $PROGRAM = $self->{PROGRAM};
  my ($indent_lvl, $tab) = @_;
  $indent_lvl = 0 unless $indent_lvl;
  $tab = "\t" unless $tab;
  my $indent = $tab x $indent_lvl;
  my $content = $indent."</form>\n";

  return($content);
} # make_submission_form_bottom

# make input table
#
# Used by
# meme.pl
# fimo.pl
# glam2.pl
# glam2scan.pl
# gomo.pl
# mast.pl
# mcast.pl
#

# used to make sure we have a unique label each time we use the showhide feature
my $label_number;

sub make_input_table {
  my $self = shift;
  die("Expected Utils object") unless ref($self) eq 'MemeWebUtils';
  my $PROGRAM = $self->{PROGRAM};
  my ($name, $left, $right, $indent_lvl, $tab, $showhide) = @_;
  $indent_lvl = 0 unless $indent_lvl;
  $tab = "\t" unless $tab;
  my $indent = $tab x $indent_lvl;
  my $content = "";
  # open and close the showhide feature if needed
  my $open = "";
  my $close = "";
  # make sure we have a unique label each time we use the showhide feature
  if ($showhide) {
      # always do showhide if requested even if named undefined
      $name = "" unless defined($name);
      if (! defined($label_number)) {
	  $label_number = 0;
      } else {
	  $label_number++;
      }
      my $label = "option_".$label_number;
      $open = qq{<div id="$label\_ctrl" style="display:block;">\n<h3 class="meme">
                 <a href="javascript:show_hide('$label','$label\_ctrl')"><img src="../images/plus.png" style="border-width:0px;"/> $name</a>
                  </h3>
                </div>
                <div id="$label" style="display:none;">
                  <h3 class="meme">
                  <a href="javascript:show_hide('$label\_ctrl','$label')"><img src="../images/minus.png" style="border-width:0px;"/> $name</a>
                  </h3>};
      $close = "</div>";
  } else {
      $open = qq(<center><label class="mainheadingmedium">$name</label></center>) if $name;
      $close = "";
  }
  $content .= 
      $indent."<!-- $name args -->\n".
      "$open";
      
  $content .=
      $indent."<table>\n".
      $indent.$tab."<tr>\n".
      $indent.$tab.$tab."<td valign=\"top\" align=\"left\">\n".
      $left.
      $indent.$tab.$tab."</td>\n".
      $indent.$tab.$tab."<td valign=\"top\" align=\"right\">\n".
      $indent.$tab.$tab.$tab.
      "<!-- this is probably possible with a div, but in the absence of a css expert I'm using a table... -->\n".
      $indent.$tab.$tab.$tab."<table><tr><td align=\"left\">\n".
      $right.
      $indent.$tab.$tab.$tab."</td></tr></table>\n".
      $indent.$tab.$tab."</td>\n".
      $indent.$tab."</tr>\n".
      $indent."</table>\n";
  $content .=  # if we are using the show_hide feature, close it off
      $close;
} # make_input_table

#
# make a description field
#
# Used by
# meme.pl
# fimo.pl
# glam2.pl
# glam2scan.pl
# gomo.pl
# mast.pl
# mcast.pl
#
sub make_description_field {
  my $self = shift;
  die("Expected Utils object") unless ref($self) eq 'MemeWebUtils';
  my $PROGRAM = $self->{PROGRAM};
  my ($subject, $value, $indent_lvl, $tab) = @_;
  $value = "" unless defined $value;

  $indent_lvl = 0 unless $indent_lvl;
  $tab = "\t" unless $tab;

  my $indent = $tab x $indent_lvl;

  my $content = 
      $indent."<!-- description -->\n".
      $indent."<a href=\"../help_email.html\"><b>Description</b></a> of your $subject:<br />\n".
      $indent."<input class=\"maininput\" type=\"TEXT\" size=\"40\" name=\"description\" value=\"$value\">\n";

  return($content);
} # make_description_field

#
# make address field
#
# Used by
# meme.pl
# fimo.pl
# glam2.pl
# glam2scan.pl
# gomo.pl
# mast.pl
# mcast.pl
#
sub make_address_field {
  my $self = shift;
  die("Expected Utils object") unless ref($self) eq 'MemeWebUtils';
  my $PROGRAM = $self->{PROGRAM};
  my ($address, $address_verify, $indent_lvl, $tab) = @_;
  $address = "" unless defined $address;
  $address_verify = "" unless defined $address_verify;
  $indent_lvl = 0 unless $indent_lvl;
  $tab = "\t" unless $tab;
  my $indent = $tab x $indent_lvl;
  my $content = 
      $indent."<!-- address fields -->\n".
      $indent."Your <a href=\"../help_email.html\"><b>e-mail address:</b></a><br />\n".
      $indent."<input class=\"maininput\" type=\"TEXT\" size=\"30\" name=\"address\" value=\"$address\"><br />\n".
      $indent."Re-enter <b>e-mail address:</b><br />\n".
      $indent."<input class=\"maininput\" type=\"TEXT\" size=\"30\" name=\"address_verify\" value=\"$address_verify\"><br />\n".
      $indent."<br />\n";

  return($content);
} # make_address_field

#
# make a motif file field
# 
# Used by
# fimo.pl
# glam2scan.pl
# gomo.pl
# mast.pl
# mcast.pl
#
sub make_motif_field {
  my $self = shift;
  die("Expected Utils object") unless ref($self) eq 'MemeWebUtils';
  my $PROGRAM = $self->{PROGRAM};
  my ($program, $name, $inline_data, $alphabet, $doc1, $doc2, $doc3, $doc4, $indent_lvl, $tab) = @_;
  $indent_lvl = 0 unless $indent_lvl;
  $tab = "\t" unless $tab;
  my $indent = $tab x $indent_lvl;
  my $content;

  # print the input fields for the motif file unless already input
  if (! $inline_data) {
    $content = 
        $indent . "Your <a href=\"$doc1\"><b>motif</b></a> file:".
                  "<input class=\"maininput\" name=\"$name\" type=\"file\" /><br />\n".
        $indent . "<a href=\"$doc2\"><b>Sample</b></a> $doc4.<br />\n";
  } else {
    my $hidden_value = $doc3;

    #$hidden_value =~ s/\s+/_/g;        # replace white space with underline
    $hidden_value =~ s/\'//g;            # remove single quotes
    $hidden_value =~ s/<tt>//g;            # remove <tt>
    $hidden_value =~ s/<\/tt>//g;

    $content = 
        $indent."<p>\n".
        $indent.$tab."<H3>\n".
        $indent.$tab.$tab."$PROGRAM will search using your previously provided motif(s):\n".
        $indent.$tab.$tab."$doc3\n".
        $indent.$tab."</H3>\n".
        $indent.$tab."<input type=\"hidden\" name=\"alphabet\" value=\"$alphabet\">\n".
        $indent.$tab."<input type=\"hidden\" name=\"inline_name\" value=\"$hidden_value\">\n".
        $indent.$tab."<input type=\"hidden\" name=\"inline_$name\" value=\"$inline_data\">\n";

  } # no inline

  return($content);
} # make_motif_field

#
# make a list of supported databases field
# 
# Used by
# fimo.pl
# glam2scan.pl
# gomo.pl
# mast.pl
# mcast.pl
#
sub make_supported_databases_field {
  my $self = shift;
  die("Expected Utils object") unless ref($self) eq 'MemeWebUtils';
  #get params
  my (
    $name,          # name to give field
    $desc,          # brief db description, eg "Sequence"
    $index,         # path to the index file
    $query,         # url used to query the databases by substituting "~category~" with the category index.
    $docs,          # url for documentation on the database
    $indent_lvl,    # number of tabs to indent, zero if undefined
    $tab            # tab character, "\t" if undefined
  ) = @_;
  # set defaults for the indent
  $indent_lvl = 0 unless $indent_lvl;
  $tab = "\t" unless $tab;
  my $indent = $tab x $indent_lvl;

  # get a list of categories from the index
  my @categories = load_categories($index);

  #
  my $content =  
      $indent."<br />$desc database to search--select <b>one</b> of the following:<br />\n".
      $indent."<br />\n".
      $indent."<!-- supported databases -->\n".
      $indent."A <a href=\"$docs\"><b>supported database</b></a>:<br />\n".
      $indent."<script type=\"text/javascript\" src=\"../selectdb.js\" defer=\"defer\"></script>\n".
      $indent."Category: <br />\n".
      $indent."<select id=\"category\" onchange=\"send_dblist_request('$query', this.value, '$name')\">\n".
      $indent.$tab."<option value=\"\" selected=\"selected\" ></option>\n";
  for (my $i = 0; $i < scalar(@categories); $i++) {
    $content .= $indent.$tab."<option value=\"$i\">" . $categories[$i] . "</option>\n";
  }
  $content .=
      $indent."</select><br />\n".
      $indent."Database:\n<br />".
      $indent."<select style=\"min-width:10em;\" id=\"$name\" name=\"$name\" disabled=\"disabled\">\n".
      $indent.$tab."<option value=\"\" selected=\"selected\"></option>\n".
      $indent."</select><br />\n".      
      $indent."<!-- attempt to fix partially cached pages causing the select boxes to be unusable -->\n".
      $indent."<script type=\"text/javascript\">\n".
      $indent.$tab."var last_db_index = 0;\n".
      $indent.$tab."function fixPage(e) {\n".
      $indent.$tab.$tab."send_dblist_request('$query', document.getElementById('category').value, '$name', last_db_index);\n".
      $indent.$tab."}\n".
      $indent.$tab."function fixPersistedPage(e) {\n".
      $indent.$tab.$tab."if (e.persisted) fixPage(e);\n".
      $indent.$tab."}\n".
      $indent.$tab."function storePageState(e) {\n".
      $indent.$tab.$tab."last_db_index = document.getElementById('$name').selectedIndex;\n".
      $indent.$tab."}\n".
      $indent.$tab."if (window.addEventListener) {\n".
      $indent.$tab.$tab."window.addEventListener('load', fixPage, false);\n".
      $indent.$tab.$tab."window.addEventListener( 'pageshow', fixPersistedPage, false );\n".
      $indent.$tab.$tab."window.addEventListener( 'pagehide', storePageState, false );\n".
      $indent.$tab."} else if (window.attachEvent) {\n".
      $indent.$tab.$tab."window.attachEvent('onload', fixPage);\n".
      $indent.$tab.$tab."window.attachEvent('onpageshow', fixPersistedPage);\n".
      $indent.$tab.$tab."window.attachEvent('onpagehide', storePageState);\n".
      $indent.$tab."} else {\n".
      $indent.$tab.$tab."window.onload = fixPage;\n".
      $indent.$tab.$tab."window.onpageshow = fixPersistedPage;\n".
      $indent.$tab.$tab."window.onpagehide = storePageState;\n".
      $indent.$tab."}\n".
      $indent."</script>\n";
  return $content;
} # make_supported_databases_field


#
# make upload FASTA field
# 
# Used by 
# fimo.pl
# glam2scan.pl
# mast.pl
# mcast.pl
#
sub make_upload_fasta_field {
  my $self = shift;
  die("Expected Utils object") unless ref($self) eq 'MemeWebUtils';
  my $PROGRAM = $self->{PROGRAM};
  my ($name, $maxsize) = @_;

  my $content = qq {
<!-- upload FASTA file -->
Your <a href="../doc/fasta-format.html"><b>FASTA</b></a> sequence file 
($maxsize sequence characters maximum):
<br />
<div id="upload_fasta_div">
  <input class="maininput" name="$name" type="file">
  <a onclick="clearFileInputField('upload_fasta_div')" href="javascript:noAction();"><b>Clear</b></a>
</div>
<br />
<a href="../examples/sample-kabat.seq"><b>Sample</b></a> DNA database.
  }; # end quote

  return($content);
} # make_upload_fasta_field

#
# make upload sequences field
# 
# Used by
# meme.pl
# glam2.pl
# for MEME-seq we no longer enforce maxsize but insist on
# DNA sequences: signal this by $maxsize == undef
sub make_upload_sequences_field {
  my $self = shift;
  die("Expected Utils object") unless ref($self) eq 'MemeWebUtils';
  my $PROGRAM = $self->{PROGRAM};
  my ($name1, $name2, $maxsize, $seq_doc, $alpha_doc,
    $format_doc,
    $filename_doc,
    $paste_doc,
    $sample_file,
    $sample_alphabet,
    $target
  ) = @_;
  # Allow target to be optional so define the default as if there was no target
  $target = "_self" unless defined $target;
  my $sizeinfo = defined($maxsize)?
  qq {The sequences may contain no more than <b>$maxsize</b>
      <a href="$alpha_doc"><b>characters</b></a>
      <br />
      total total in any of a large number of
      <a href="$format_doc"><b>formats</b></a>.} : 
  qq {The DNA sequences must be in <a href="$format_doc"><b>FASTA format</b></a>.};
  my $content = qq {
<br />
<!-- sequences fields -->
Please enter the <a href="$seq_doc">
<b>} . (defined($maxsize)?"":"DNA ") . qq{
sequences</b></a> which you believe share one or more
<br />
motifs.  $sizeinfo
<br />
<br />
Enter the <a href="$filename_doc"><b>name of a file</b></a>
containing the sequences here: 
<br />
<div id="upload_seqs_div">
  <input class="maininput" name="$name1" type="file">
  <a onclick="clearFileInputField('upload_seqs_div')" href="javascript:noAction();"><b>Clear</b></a>
</div>
<br />
<b>or</b>
<br />
the <a href="$paste_doc"><b>actual sequences</b>
</a> here (<a href="$sample_file" target="$target"><b>Sample $sample_alphabet Input Sequences</b></a>): 
<br />
<textarea name = "$name2" rows="5" cols="60"></textarea>
  }; # end quote
} # make_upload_sequences_field

#
# make radio buttons
#
# Values may be comma-separated "v1,v2"; v1 is printed.
# 
# Used by
# meme.pl
# gomo.pl
#
sub make_radio_field {
  my $self = shift;
  die("Expected Utils object") unless ref($self) eq 'MemeWebUtils';
  my $PROGRAM = $self->{PROGRAM};
  my ($text, $name, $checked, $values, $indent_lvl, $tab) = @_;
  $indent_lvl = 0 unless $indent_lvl;
  $tab = "\t" unless $tab;
  my $indent = $tab x $indent_lvl;
  my $content = $indent.$text."\n";

  foreach my $value (@$values) {
    my ($v1, $v2) = split(/,/, $value);
    if ($v2 eq $checked) {
      $content .= $indent."<input class=\"mainbutton\" type=\"radio\" name=\"$name\" value=\"$v2\" checked=\"checked\" > $v1\n";
    } else {
      $content .= $indent."<input class=\"mainbutton\" type=\"radio\" name=\"$name\" value=\"$v2\" > $v1\n";
    }
  }

  return($content);
} # make_radio_field

#
# make option value list 
#
# Values may be comma-separated "v1,v2"; v2 is printed,
# and "v1,v2" is the value of the field selected.
# If there is no ",v2", then v1 is used as the printed text.
#
# Used by
# fimo.pl
# glam2scan.pl
# mast.pl
# mcast.pl
#
sub make_select_field {
  my $self = shift;
  die("Expected Utils object") unless ref($self) eq 'MemeWebUtils';
  my $PROGRAM = $self->{PROGRAM};
  my ($text, $name, $selected, @values) = @_;

  my $options = "";
  foreach my $value (@values) {
    my ($v1, $v2) = split(/,/, $value); 
    $v2 = $v1 unless $v2;
    if ($value eq $selected) {
      $options .= "<option selected value='$value'> $v2\n";
    } else {
      $options .= "<option value='$value'> $v2\n";
    }
  }

  my $content = qq {
<!-- $name select field -->
$text
<select name='$name'>
$options
</select>
  }; # end quote

  return($content);
} # make_select_field

#
# print submit button, reset button, email contact
#
# Used by
# meme.pl
# fimo.pl
# glam2.pl
# glam2scan.pl
# gomo.pl
# mast.pl
# mcast.pl
#
sub make_submit_button {
  my $self = shift;
  die("Expected Utils object") unless ref($self) eq 'MemeWebUtils';
  my $PROGRAM = $self->{PROGRAM};
  my ($value, $email_contact, $indent_lvl, $tab) = @_;
  
  $indent_lvl = 0 unless $indent_lvl;
  $tab = "\t" unless $tab;

  my $indent = $tab x $indent_lvl;

  my $content = 
      $indent."<!-- submit and reset buttons -->\n".
      $indent."<center>\n".
      $indent.$tab."<input type=\"SUBMIT\" name=\"target_action\" value=\"$value\" onClick=\"return check(this.form)\">\n".
      $indent.$tab."&nbsp; &nbsp; &nbsp;\n".
      $indent.$tab."<input type=\"RESET\" value=\"Clear Input\">\n".
      $indent."</center>\n";

  return($content);
} # make_submit_button

# 
# make checkbox
#
# Note: $descr should include a </a> tag.
#
# Used by
# meme.pl
# fimo.pl
# glam2.pl
# glam2scan.pl
# mast.pl
#
sub make_checkbox {
  my $self = shift;
  die("Expected Utils object") unless ref($self) eq 'MemeWebUtils';
  my $PROGRAM = $self->{PROGRAM};
  my ($name, $value, $descr, $checked) = @_;
  my ($check) = $checked ? " checked" : "";

  my $content = qq {
<input class="mainbutton" type="checkbox" name="$name" value="$value"$check>
$descr
  }; # end quote

  return($content);
} # make_checkbox

#
# make dna-only options
# 
# Used by
# meme.pl
# glam2.pl
# glam2scan.pl
# mast.pl
#
sub make_dna_only {
  my $self = shift;
  die("Expected Utils object") unless ref($self) eq 'MemeWebUtils';
  my $PROGRAM = $self->{PROGRAM};
  my ($options) = @_;

  my $content = qq {
<p>
<center>
<b>DNA-ONLY OPTIONS</b>
<br />
(Ignored for protein searches)
</center>
</p>
$options
  }; # end quote

  return($content);
} # make_dna_only

#
# make the complete input form
#
# Used by
# meme.pl
# fimo.pl
# glam2.pl
# glam2scan.pl
# gomo.pl
# mast.pl
# mcast.pl
#
sub make_submission_form {
  my $self = shift;
  die("Expected Utils object") unless ref($self) eq 'MemeWebUtils';
  my $PROGRAM = $self->{PROGRAM};
  my ($header, $form_top, $required, $optional, $submit, $form_bottom, $tailer, $indent_lvl, $tab)  = @_;
  $indent_lvl = 0 unless $indent_lvl;
  $tab = "\t" unless $tab;
  my $indent = $tab x $indent_lvl;
  my $indent2 = $tab x 6;
  my $content = 
      $header.
      $indent."<!-- form body -->\n".
      $indent."<body class=\"body\">\n".
      $form_top.
      $indent.$indent2."<fieldset>\n".
      $indent.$indent2.$tab."<legend>Data Submission Form</legend>\n".
      $required.
      $optional.
      $submit.
      $indent.$indent2."</fieldset>\n".
      $form_bottom.
      $tailer;

  return($content);
} # make_submission_form

#
# print the headers for a response form
# 
# Used by
# Utils
#
sub print_html_top {
  my $self = shift;
  die("Expected Utils object") unless ref($self) eq 'MemeWebUtils';
  my $PROGRAM = $self->{PROGRAM};
  my ($program) = @_;

  print <<END;
<!DOCTYPE html>
<html>
  <title> $program - Verification </title>
  <body background=\"../images/bkg.jpg\">
    <hr />
END
} # print_html_top

#
# print the tailer for a response form
#
# Uses global variable $self->{NERRORS}.
# 
# Used by
# meme.pl
# fimo.pl
# glam2.pl
# glam2scan.pl
# gomo.pl
# mast.pl
# mcast.pl
#
sub print_tailers {
  my $self = shift;
  die("Expected Utils object") unless ref($self) eq 'MemeWebUtils';
  my $NERRORS = $self->{NERRORS};

  # print error message summary
  if ($self->{NERRORS}) {
    my ($tobe, $booboo, $pronoun);
    if ($NERRORS == 1) {
      $tobe = "was";
      $booboo = "error";
      $pronoun = "it";
    } else {
      $tobe = "were";
      $booboo = "errors";
      $pronoun = "them";
    }
    print "</b></ol>\n";
    print "<b>There $tobe $NERRORS $booboo on the form.\n";
    print "Please correct $pronoun and try again.</b>\n";
  }

  #
  # finish the response form
  #
  print "<hr /></body></html>";
} # print_tailers

#
# Verify the job to the user via response page and email.
#
# Uses global variables $PROGRAM.
#
# Used by
# meme.pl
# fimo.pl
# glam2.pl
# glam2scan.pl
# gomo.pl
# mast.pl
# mcast.pl
# tomtom.pl
# spamo.pl
#
sub verify_opal_job {
  my $self = shift;
  die("Expected Utils object") unless ref($self) eq 'MemeWebUtils';
  my $PROGRAM = $self->{PROGRAM};
  my (
    $result,             # return from launchJob
    $address,            # user's address
    $email_contact,          # email of support desk
    $message            # HTML text of message
  ) = @_;

  unless (eval {$result->fault}) {
    my $jobid = $result->getJobID();
    my $out_url = $result->getBaseURL();

    # make a link to the querystatus.cgi page
    my $query_url = "http://gimme/meme/cgi-bin/querystatus.cgi";
    $query_url .= "?jobid=$jobid&service=$PROGRAM";

    # create the verification message
    my $verify = $self->make_verify_header($jobid, $query_url) . $message;

    # email the verification
    $self->send_verification($address, $email_contact, $jobid, $verify);

    # print the response form
    $self->print_html_top($PROGRAM);
    print $verify;
    print "You will also receive a confirming message at your email address: <b>$address</b>.";
  } else {
    my $code = $result->faultcode;
    my $errmsg = $result->faultstring;
    $self->whine("Your job submission resulted in a fault.<br />", "Code: $code<br />", "Message: $errmsg<br />");   
  }

} # verify_opal_job

# 
# Private Method
#
# create the header for verification message
# 
# Used by
# Utils
#
sub make_verify_header {
  my $self = shift;
  die("Expected Utils object") unless ref($self) eq 'MemeWebUtils';
  my $PROGRAM = $self->{PROGRAM};
  my ($jobid, $query_url) = @_;
  my $service_url = "no";
  my $activity_url;
  if (substr $service_url, -1, 1 eq '/') {
    $activity_url = "$service_url../dashboard?command=statistics";
  }
  else {
    $activity_url = "$service_url/../dashboard?command=statistics";
  }
  my $verify = "Your job id is: <b> $jobid </b> <br />\n";
  $verify .= "You can view your job results at: <a href=\"$query_url\">$query_url</a> <br />";
  $verify .= "You can view server activity <a href=\"$activity_url\">here</a>.<br />";
  return($verify);
} # make_verify_header

#
# print an error message, bump the global error count and continue 
# Uses globals $self->{NERRORS} and $PROGRAM
#
# Used by
# Utils
# meme.pl
# fimo.pl
# glam2.pl
# glam2scan.pl
# gomo.pl
# mast.pl
# mcast.pl
#
sub whine {
  my $self = shift;
  die("Expected Utils object") unless ref($self) eq 'MemeWebUtils';
  my $PROGRAM = $self->{PROGRAM};
  my @msg = @_;
  #TODO make use of the multiple lines to correctly indent
  my $msg_str = join("\n", @msg);
  if ($self->{NERRORS} == 0) {
    print "Content-type: text/html\n\n";
    $self->print_html_top($PROGRAM);
    print "
      <h1>Error Report:</h1>       <hr />       <ol>
      <b>
    ";
  }
  print "<li><b>$msg_str</b>\n";
  $self->{NERRORS}++;
} # whine

#
# Private Method
#
# copy a file to standard output
#
# Used by
# Utils
#
sub copy_stdout
{
  my $self = shift;
  die("Expected Utils object") unless ref($self) eq 'MemeWebUtils';
  my $PROGRAM = $self->{PROGRAM};
  open (F, "@_");
  print "<pre>";
  while (<F>) {
    print $_;
  }
  print "</pre>";
} # copy_stdout

#
# Private Method
#
# find_bad_sequence_data
# Find occurences of unknown symbols in sequence data.
#
# Returns an array of strings describing occurences of unknown symbols.
#
# Used by 
# Utils
#
sub find_bad_sequence_data {
  my $self = shift;
  die("Expected Utils object") unless ref($self) eq 'MemeWebUtils';
  my $PROGRAM = $self->{PROGRAM};
  my ($bad_symbols, $fasta_data) = @_;
  my @lines = split "\n", $fasta_data;
  my $num_lines = scalar @lines;
  my (@bad_lines, $seq_name);
  for (my $i = 1; $i <= $num_lines; ++$i) {
    my $line = $lines[$i - 1];
    if ($line =~ m/>/) {
        $seq_name = $line;
        next;
    }
    if ($line =~ m/[$bad_symbols]/i) {
        push @bad_lines, "<br/>line number: $i<br/> sequence name: $seq_name<br/>sequence: $`<font color='red'>$&</font>$'\n";
    }
  }
  return @bad_lines;
} # find_bad_sequence_data

1; #modules must return true
