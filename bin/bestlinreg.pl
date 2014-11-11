#! /usr/bin/env perl
#
# linear fitting using parameters optimised by Claude Lepage,
# using a brain mask for the source and the target. This was
# greatly inspired by best1stepnlreg.pl by Steve Robbins.
#
# Claude Lepage - claude@bic.mni.mcgill.ca
# Andrew Janke - rotor@cmr.uq.edu.au
# Center for Magnetic Resonance
# The University of Queensland
# http://www.cmr.uq.edu.au/~rotor
#
# Copyright Andrew Janke, The University of Queensland.
# Permission to use, copy, modify, and distribute this software and its
# documentation for any purpose and without fee is hereby granted,
# provided that the above copyright notice appear in all copies.  The
# author and the University of Queensland make no representations about the
# suitability of this software for any purpose.  It is provided "as is"
# without express or implied warranty.

use strict;
use warnings "all";
use Getopt::Tabular;
use File::Basename;
use File::Temp qw/ tempdir /;

my @conf = (

   { type        => "blur",
     trans       => [qw/-est_translations/],
     blur_fwhm   => 16,
     steps       => [qw/8 8 8/],
     tolerance   => 0.01,
     simplex     => 32 },

   { type        => "blur",
     trans       => undef,
     blur_fwhm   => 8,
     steps       => [qw/4 4 4/],
     tolerance   => 0.004,
     simplex     => 16 },

   { type        => "blur",
     trans       => undef,
     blur_fwhm   => 4,
     steps       => [qw/4 4 4/],
     tolerance   => 0.004,
     simplex     => 8 },

   { type        => "dxyz",
     trans       => undef,
     blur_fwhm   => 8,
     steps       => [qw/4 4 4/],
     tolerance   => 0.004,
     simplex     => 4 },

   { type        => "dxyz",
     trans       => undef,
     blur_fwhm   => 4,
     steps       => [qw/4 4 4/],
     tolerance   => 0.004,
     simplex     => 2 }
     
   );


my($Help, $Usage, $me);
my(@opt_table, %opt, $source, $target, $outxfm, $outfile, @args, $tmpdir);

$me = &basename($0);
%opt = (
   'verbose'     => 1,
   'clobber'     => 0,
   'fake'        => 0,
   'init_xfm'    => undef,
   'source_mask' => undef,
   'target_mask' => undef,
   'lsqtype'     => "-lsq9",
   'noresample'  => undef
   );

$Help = <<HELP;
| $me does hierachial linear fitting between two files.
|    you will have to edit the script itself to modify the
|    fitting levels themselves
| 
| Problems or comments should be sent to: claude\@bic.mni.mcgill.ca
HELP

$Usage = "Usage: $me [options] source.mnc target.mnc output.xfm [output.mnc]\n".
         "       $me -help to list options\n\n";

@opt_table = (
   ["-verbose", "boolean", 0, \$opt{verbose},
      "be verbose" ],
   ["-clobber", "boolean", 0, \$opt{clobber},
      "clobber existing check files" ],
   ["-fake", "boolean", 0, \$opt{fake},
      "do a dry run, (echo cmds only)" ],
   ["-init_xfm", "string", 1, \$opt{init_xfm},
      "initial transformation (default identity)" ],
   ["-noresample", "boolean", 0, \$opt{noresample},
      "do not resample input" ],
   ["-source_mask", "string", 1, \$opt{source_mask},
      "source mask to use during fitting" ],
   ["-target_mask", "string", 1, \$opt{target_mask},
      "target mask to use during fitting" ],
   ["-lsq9", "const", "-lsq9", \$opt{lsqtype},
      "use 9-parameter transformation (default)" ],
   ["-lsq12", "const", "-lsq12", \$opt{lsqtype},
      "use 12-parameter transformation" ],
   ["-lsq6", "const", "-lsq6", \$opt{lsqtype},
      "use 6-parameter transformation" ],
   ["-lsq7", "const", "-lsq7", \$opt{lsqtype},
      "use 7-parameter transformation" ],
   ["-quaternions","const",'-quaternions', \$opt{lsqtype},
      "use quaternion transformation" ],
   );

delete $ENV{MINC_COMPRESS} if $ENV{MINC_COMPRESS};

# Check arguments
&Getopt::Tabular::SetHelp($Help, $Usage);
&GetOptions (\@opt_table, \@ARGV) || exit 1;
die $Usage if(! ($#ARGV == 2 || $#ARGV == 3));
$source = shift(@ARGV);
$target = shift(@ARGV);
$outxfm = shift(@ARGV);
$outfile = (defined($ARGV[0])) ? shift(@ARGV) : undef;

# check for files
die "$me: Couldn't find input file: $source\n\n" if (!-e $source);
die "$me: Couldn't find input file: $target\n\n" if (!-e $target);
if(-e $outxfm && !$opt{clobber}){
   die "$me: $outxfm exists, -clobber to overwrite\n\n";
   }
if(defined($outfile) && -e $outfile && !$opt{clobber}){
   die "$me: $outfile exists, -clobber to overwrite\n\n";
   }

my $mask_warning = 0;
if( !defined($opt{source_mask}) ) {
  $mask_warning = 1;
} else {
  if( !-e $opt{source_mask} ) {
    $mask_warning = 1;
  }
}
if( !defined($opt{target_mask}) ) {
  $mask_warning = 1;
} else {
  if( !-e $opt{target_mask} ) {
    $mask_warning = 1;
  }
}
if( $mask_warning == 1 ) {
  print "Warning: For optimal results, you should use masking.\n";
  print "$Usage";
}

# make tmpdir
$tmpdir = &tempdir( "$me-XXXXXXXX", TMPDIR => 1, CLEANUP => 1 );

# set up filename base
my($i, $s_base, $t_base, $tmp_xfm, $tmp_source, $tmp_target, $prev_xfm);
$s_base = &basename($source);
$s_base =~ s/\.mnc(.gz)?$//;
$t_base = &basename($target);
$t_base =~ s/\.mnc$(.gz)?//;

# Mask the source and target once before blurring. Both masks must exist.

my $source_masked = $source;
my $target_masked = $target;

if( defined($opt{source_mask}) and defined($opt{target_mask}) ) { 
  if( -e $opt{source_mask} and -e $opt{target_mask} ) {
    $source_masked = "${tmpdir}/${s_base}_masked.mnc";
    &do_cmd( 'minccalc', '-clobber',
             '-expression', 'if(A[1]>0.5){out=A[0];}else{out=A[1];}',
             $source, $opt{source_mask}, $source_masked );

    $target_masked = "${tmpdir}/${t_base}_masked.mnc";
    &do_cmd( 'minccalc', '-clobber',
             '-expression', 'if(A[1]>0.5){out=A[0];}else{out=A[1];}',
             $target, $opt{target_mask}, $target_masked );
  }
}

# initial transformation supplied by the user, applied to both the 
# source image and its mask.

if( defined $opt{init_xfm} && !$opt{noresample} ) { 
  my $source_resampled = "${tmpdir}/${s_base}_resampled.mnc";
  &do_cmd( 'mincresample', '-clobber', '-like', $target_masked, 
           '-transform', $opt{init_xfm}, $source_masked, $source_resampled );
  $source_masked = $source_resampled;

  #apply it to the mask, if it's defined
  if(defined($opt{source_mask}))
  {
    my $mask_resampled = "${tmpdir}/${s_base}_mask_resampled.mnc";
    &do_cmd( 'mincresample', '-clobber', '-like', $target_masked,
             '-nearest_neighbour', '-transform', $opt{init_xfm}, 
             $opt{source_mask}, $mask_resampled );
    $opt{source_mask} = $mask_resampled;
  }
}

if(defined $opt{init_xfm} && $opt{noresample} )
{
  $prev_xfm = $opt{init_xfm};
  $opt{init_xfm} = undef;
} else {
  $prev_xfm = undef;
}
# a fitting we shall go...
for ($i=0; $i<=$#conf; $i++){
   
   # set up intermediate files
   $tmp_xfm = "$tmpdir/$s_base\_$i.xfm";
   $tmp_source = "$tmpdir/$s_base\_$conf[$i]{blur_fwhm}";
   $tmp_target = "$tmpdir/$t_base\_$conf[$i]{blur_fwhm}";
   
   print STDOUT "-+-------------------------[$i]-------------------------\n".
                " | steps:          @{$conf[$i]{steps}}\n".
                " | blur_fwhm:      $conf[$i]{blur_fwhm}\n".
                " | simplex:        $conf[$i]{simplex}\n".
                " | source:         $tmp_source\_$conf[$i]{type}.mnc\n".
                " | target:         $tmp_target\_$conf[$i]{type}.mnc\n".
                " | xfm:            $tmp_xfm\n".
                "-+-----------------------------------------------------\n".
                "\n";
   
   # blur the masked source and target images
   my @grad_opt = ();
   push( @grad_opt, '-gradient' ) if( $conf[$i]{type} eq "dxyz" );
   
   if($conf[$i]{blur_fwhm}>0) # actually this should be 1
   {
     if(!-e "$tmp_source\_$conf[$i]{type}.mnc") {
       &do_cmd('mincblur', '-clobber', '-no_apodize', '-fwhm', $conf[$i]{blur_fwhm},
               @grad_opt, $source_masked, $tmp_source);
     }
     if(!-e "$tmp_target\_$conf[$i]{type}.mnc") {
       &do_cmd('mincblur', '-clobber', '-no_apodize', '-fwhm', $conf[$i]{blur_fwhm},
               @grad_opt, $target_masked, $tmp_target);
     }
   } else { # noop
     if(!-e "$tmp_source\_$conf[$i]{type}.mnc") {
       do_cmd('ln','-s',$target_masked,"$tmp_source\_$conf[$i]{type}.mnc");
     } 
     if(!-e "$tmp_target\_$conf[$i]{type}.mnc") {
       &do_cmd('ln', '-s', $target_masked, "$tmp_target\_$conf[$i]{type}.mnc");
     }
   }
   # set up registration
   @args = ('minctracc', '-clobber', '-xcorr', $opt{lsqtype},
            '-step', @{$conf[$i]{steps}}, '-simplex', $conf[$i]{simplex},
            '-tol', $conf[$i]{tolerance});

   # Initial transformation will be computed from the from Principal axis 
   # transformation (PAT).
   push(@args, @{$conf[$i]{trans}}) if( defined $conf[$i]{trans} );

   # Current transformation at this step
   push(@args, '-transformation', $prev_xfm ) if( defined $prev_xfm );

   # masks (even if the blurred image is masked, it's still preferable
   # to use the mask in minctracc)
   push(@args, '-source_mask', $opt{source_mask} ) if defined($opt{source_mask});
   push(@args, '-model_mask', $opt{target_mask}) if defined($opt{target_mask});
   
   # add files and run registration
   push(@args, "$tmp_source\_$conf[$i]{type}.mnc", "$tmp_target\_$conf[$i]{type}.mnc", 
        $tmp_xfm);
   &do_cmd(@args);
   
   $prev_xfm = $tmp_xfm;
}

# Concatenate transformations if an initial transformation was given.

if( defined $opt{init_xfm} && !$opt{noresample} ) { 
  &do_cmd( 'xfmconcat', $opt{init_xfm}, $prev_xfm,  $outxfm );
} else {
  &do_cmd( 'mv', '-f', $prev_xfm, $outxfm );
}

# resample if required
if(defined($outfile)){
   print STDOUT "-+- creating $outfile using $outxfm\n".
   &do_cmd( 'mincresample', '-clobber', '-like', $target,
            '-transformation', $outxfm, $source, $outfile );
}


sub do_cmd { 
   print STDOUT "@_\n" if $opt{verbose};
   if(!$opt{fake}){
      system(@_) == 0 or die;
   }
}
       
