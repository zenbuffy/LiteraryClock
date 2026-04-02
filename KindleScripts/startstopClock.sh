#!/bin/bash

clockrunning=1

# check if the clock 'app' is not running (by checking if the clockisticking file is there) 
test -f /mnt/us/timelit/clockisticking || clockrunning=0

if [ $clockrunning -eq 0 ]; then

	/etc/init.d/powerd stop
	/etc/init.d/framework stop
	
	eips -c  # clear display
	#echo "Clock is not ticking. Lets wind it."
	#eips "Clock is not ticking. Lets wind it."

	# run showMetadata.sh to enable the keystrokes that will show the metadata
	sh /mnt/us/timelit/showMetadata.sh

	touch /mnt/us/timelit/clockisticking
	sh /mnt/us/timelit/timelit.sh

else

	rm /mnt/us/timelit/clockisticking

	eips -c  # clear display
	#echo "Clock is ticking. Make it stop."
	#eips "Clock is ticking. Make it stop."

	# go to home screen
	# echo "send 102">/proc/keypad

	/etc/init.d/framework start
	/etc/init.d/powerd start

fi
