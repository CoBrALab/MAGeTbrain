#! /usr/bin/env perl

my $targetTags = shift or die "Need a target tag set\n";
my $sourceTags = shift or die "Need source tag set\n";
my $outputTags = shift or die "Need and o/p file \n";
my $outputXFM = shift or die "Need an output xfm file to make\n";


my @tTags = split(/\n/, `cat $targetTags`);
my @sTags = split(/\n/, `cat $sourceTags`);


my @targetCoords = ();
my @sourceCoords = ();

my $flag = 0;

foreach(@tTags){
	if($flag == 1){
		push(@targetCoords ,$_);
		}
		
	if($_ =~ /Points/){ $flag = 1};
}
	
$flag = 0;

foreach(@sTags){
	if($flag == 1){
		push(@sourceCoords ,$_);
		}
		
	if($_ =~ /Points/){ $flag = 1};
}

#if($#targetCoords != $#sourceCoords){
#	print "poo \n";
#	die;
#}
my $i = 0;

open(OUTTAG, ">$outputTags");

print OUTTAG "MNI Tag Point File\n";
print OUTTAG "Volumes = 2;\n";
print OUTTAG "\n";
print OUTTAG "Points = \n";

foreach(@targetCoords){
	#my @t = split(/ /, $_);
	#my @s = split(/ /, $sourceCoords[$i]);
	my @t = split();
	
	my @s = split(/ +/,$sourceCoords[$i]);
	
	if($i>0){
		print OUTTAG "\n";
		#print  "\n";
		}
	$t[2]=~s/\;$//; 
	$s[3]=~s/\;$//; 
	print OUTTAG "$t[0] $t[1] $t[2] $s[0] $s[1] $s[2] $s[3] \"\"";
	#print  "$t[0] $t[1] $t[2] $s[1] $s[2] $s[3] \"\"";
	$i++;
	}
	
print OUTTAG "\; \n";
close(OUTTAG);

#do_cmd("cat $outputTags | head -n 23 \> $outputTags");

do_cmd("tagtoxfm", "-lsq6", $outputTags, $outputXFM);
	
sub do_cmd{
	print "@_ \n";
	system(@_)==0 or die;
	}
