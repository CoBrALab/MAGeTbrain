
cat $1 | swapnan.sh > $1.new

rm $1

mv $1.new $1


