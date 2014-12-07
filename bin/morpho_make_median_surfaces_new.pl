#! /usr/bin/env perl

use strict;
use File::Basename;
use File::Temp qw/ tempdir /;
use Env;

chomp(my $prog = `basename $0`);
my $tmpdir = &tempdir("$prog-XXXXXXXXXXX", TMPDIR =>1, CLEANUP =>1);



my $output_median_surface = shift;

my $current_file;

my $flag = 0;
my $num_poly = 0;
my $head;
my $the_rest;

while($current_file=shift){

  if(!(-e $current_file)){ die "No such file: ${current_file} \n";}
  else{

   
   my $b = &basename($current_file, ".obj");
    do_cmd('dump_points', $current_file, "${tmpdir}/${b}.txt");

   my $x_coords = "cat ${tmpdir}/${b}.txt | awk {\'print \$1\'} > ${tmpdir}/${b}_xcoords.txt";
   do_cmd($x_coords);

   my $y_coords = "cat ${tmpdir}/${b}.txt | awk {\'print \$2\'} > ${tmpdir}/${b}_ycoords.txt";
   do_cmd($y_coords);

    my $z_coords = "cat ${tmpdir}/${b}.txt | awk {\'print \$3\'} > ${tmpdir}/${b}_zcoords.txt";
   do_cmd($z_coords);

    if($flag == 0){

      my @dummy = split(/\n/, `cat  ${tmpdir}/${b}_zcoords.txt`);
      $num_poly = $#dummy;
      $head = `cat $current_file | head -1`;
   

      my @end = split(/\s+/, `cat $current_file | wc`);


      my $beginning_of_the_rest = 2*$num_poly + 5;
      $the_rest = `cat $current_file | awk \'NR==${beginning_of_the_rest},0\'`;
    
      $flag ++;

    }

   my $start = $num_poly + 4;
   my $finish = 2*$num_poly + 4;

   my $x_normals = "cat $current_file | awk \'NR==${start},NR==${finish}\' | awk {\'print \$1\'} > ${tmpdir}/${b}_xnormals.txt";
   do_cmd($x_normals);
   my $y_normals = "cat $current_file | awk \'NR==${start},NR==${finish}\' | awk {\'print \$2\'} > ${tmpdir}/${b}_ynormals.txt";
   do_cmd($y_normals);
   my $z_normals = "cat $current_file | awk \'NR==${start},NR==${finish}\' | awk {\'print \$3\'} > ${tmpdir}/${b}_znormals.txt";
   do_cmd($z_normals);  

    

  }

}


my @x = split(/\n/, `ls -1  ${tmpdir}/*_xcoords.txt`);
my @y = split(/\n/, `ls -1  ${tmpdir}/*_ycoords.txt`);
my @z = split(/\n/, `ls -1  ${tmpdir}/*_zcoords.txt`);
my @x_norm = split(/\n/, `ls -1  ${tmpdir}/*_xnormals.txt`);
my @y_norm = split(/\n/, `ls -1  ${tmpdir}/*_ynormals.txt`);
my @z_norm = split(/\n/, `ls -1  ${tmpdir}/*_znormals.txt`);

my $x_paste = "paste @x -d\",\" > ${tmpdir}/all_xcoords.csv";
do_cmd($x_paste);

my $y_paste = "paste @y -d\",\" > ${tmpdir}/all_ycoords.csv";
do_cmd($y_paste);

my $z_paste = "paste @z -d\",\" > ${tmpdir}/all_zcoords.csv";
do_cmd($z_paste);

my $x_norm_paste = "paste @x_norm -d\",\" > ${tmpdir}/all_xnorms.csv";
do_cmd($x_norm_paste);

my $y_norm_paste = "paste @y_norm -d\",\" > ${tmpdir}/all_ynorms.csv";
do_cmd($y_norm_paste);

my $z_norm_paste = "paste @z_norm -d\",\" > ${tmpdir}/all_znorms.csv";
do_cmd($z_norm_paste);


my $R_command_points = "R --slave --no-save --silent ".
  "--args  ${tmpdir}/all_xcoords.csv ".
  "${tmpdir}/all_ycoords.csv ".
  "${tmpdir}/all_zcoords.csv ".
  "${tmpdir}/median_xcoords.csv ".
  "${tmpdir}/median_ycoords.csv ".
  "${tmpdir}/median_zcoords.csv ".
  "< $PWD/barf_medians_driver.R ";
do_cmd($R_command_points);
  #"< /projects/mallar/NIH_COS_2/Median_surface_code/barf_medians_driver.R ";

my $R_command_normals = "R --slave --no-save --silent ".
  "--args  ${tmpdir}/all_xnorms.csv ".
  "${tmpdir}/all_ynorms.csv ".
  "${tmpdir}/all_znorms.csv ".
  "${tmpdir}/median_xnorms.csv ".
  "${tmpdir}/median_ynorms.csv ".
  "${tmpdir}/median_znorms.csv ".
  "< $PWD/barf_medians_driver.R ";
do_cmd($R_command_normals);
  #"< /projects/mallar/NIH_COS_2/Median_surface_code/barf_medians_driver.R ";


my $median_points_paste = "paste ${tmpdir}/median_xcoords.csv ".
  "${tmpdir}/median_ycoords.csv ".
  "${tmpdir}/median_zcoords.csv ".
  "-d\" \" > ${tmpdir}/all_points_median.txt ";
system($median_points_paste);

my $median_normals_paste = "paste ${tmpdir}/median_xnorms.csv ".
  "${tmpdir}/median_xnorms.csv ".
  "${tmpdir}/median_xnorms.csv ".
  "-d\" \" > ${tmpdir}/all_norms_median.txt "; 
system($median_normals_paste);


print "Creating final median surface \n\n";

open(object, ">${output_median_surface}");

my $final_points = `cat ${tmpdir}/all_points_median.txt`;
my $final_normals = `cat ${tmpdir}/all_norms_median.txt`;


print object "$head";
print object "$final_points \n";
print object "$final_normals \n";
print object "$the_rest \n";

close(object);




sub do_cmd{

#  print "@_ \n";
  system(@_) == 0 or die;
#
    }
#    
