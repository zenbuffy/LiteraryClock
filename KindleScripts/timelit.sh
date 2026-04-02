#!/bin/bash

# if the Kindle is not being used as clock, then just quit
test -f /mnt/us/timelit/clockisticking || exit

# sleep between 1am and 6am to save power
hour=$(env TZ=Europe/Dublin date +"%H")
if [ "$hour" -ge 1 ] && [ "$hour" -lt 6 ]; then
	exit
fi

# find the current minute of the day
MinuteOTheDay="$(env TZ=Europe/Dublin date -R +"%H%M")";

# check if there is at least one image for this minute 
lines="$(find /mnt/us/timelit/images/quote_$MinuteOTheDay* 2>/dev/null | wc -l)"
if [ $lines -eq 0 ]; then
	echo 'no images found for '$MinuteOTheDay
	exit
else
	echo $lines' files found for '$MinuteOTheDay
fi


# randomly pick a png file for that minute (since we have multiple for some minutes)
ThisMinuteImage=$( find /mnt/us/timelit/images/quote_$MinuteOTheDay* 2>/dev/null | python -c "import sys; import random; print(''.join(random.sample(sys.stdin.readlines(), int(sys.argv[1]))).rstrip())" 1)

echo $ThisMinuteImage > /mnt/us/timelit/clockisticking

# clear the screen
eips -c

# show that image
eips -g $ThisMinuteImage

# warn if battery is low
battery=$(cat /sys/class/power_supply/*/capacity 2>/dev/null | head -1)
if [ -n "$battery" ] && [ "$battery" -lt 20 ]; then
	eips 0 0 "Battery: ${battery}%"
fi