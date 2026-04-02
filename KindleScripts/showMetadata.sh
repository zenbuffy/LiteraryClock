#!/bin/bash

# listen for keystrokes and show metadata on demand
while true; do
	/usr/bin/waitforkey 104 191 || break

	# see what image is shown at the moment
	current=$(cat /mnt/us/timelit/clockisticking 2>/dev/null)

	# only if a filename is in the clockisticking file, then continue
	if [ -n "$current" ]; then

		# find the matching image with metadata
		currentCredit=$(echo $current | sed 's/.png//')_credits.png
		currentCredit=$(echo $currentCredit | sed 's/images/images\/metadata/')

		# show the image with metadata
		eips -g $currentCredit

	fi
done