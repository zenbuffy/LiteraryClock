# LiteraryClock
A repo to host improvements to the literary clock project kicked off by Jaap Meijers

Jaap Meijers shared instructions to create a literary clock using an old Kindle here: https://www.instructables.com/id/Literary-Clock-Made-From-E-reader/

I wanted to make some changes to the scripts, and to the provided CSV files.

# Prerequisites
To get the PHP script working on my Linux box, I need to install the following pckages:
* php7.0-cli
* php-gd
* php-imagick
* imagemagick

And download the fonts from here: 
https://sourceforge.net/projects/linuxlibertine/

Which I unpacked into the same directory as the PHP script.

# Scripts
I've modified the quote_to_image file so that it first checks to see if an image already exists before creating it. This means that you can run the script against the provided image folder without worrying about overwriting the existing images there, and also makes the script run more efficiently, as it only does the more intensive work of guessing font sizes, fitting the quotes, and creating the images, if the image doesn't already exist. 

It just does this check in the images directory, not the metadata directory. If you want to force the regeneration of a specific image for any reason (e.g. you fixed a typo), just delete that image from the "images" directory, no need to touch the metadata directory, and it'll regenerate both.

# CSV file
I've begun filling in some extra times with books I enjoy. In some cases, I've simply added to times where there already were some entries, to include books I like. I have also added some entries where times did not exist already.

# Missing Times

As of right now, the times are complete (afaik). However, there is still a Google Form to gather any times people come across while reading: https://docs.google.com/forms/d/1TpjlPc1VI9-tnI7yPSvtHE6FefLJ4IbbtVKwfy7C9ds/edit

Feel free to add one if you come across a time while reading, or to fork this repo to make updates to the source CSV file!
