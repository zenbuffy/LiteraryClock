# LiteraryClock
A repo to host improvements to the literary clock project kicked off by Jaap Meijers

Jaap Meijers shared instructions to create a literary clock using an old Kindle here: https://www.instructables.com/id/Literary-Clock-Made-From-E-reader/

I wanted to make some changes to the scripts, and to the provided CSV files.

# Prerequisites
To get the PHP script working on my Linux box, I need to install the following php packages:
* php7.0-cli (or any version up to and including PHP 8.1)
* php-gd
* php-imagick
* imagemagick

And download the fonts from here: 
https://sourceforge.net/projects/linuxlibertine/
Which should be unpacked into the same directory as the PHP script. 

# Scripts
I've modified the quote_to_image file so that it first checks to see if an image already exists before creating it. This means that you can run the script against the provided image folder without worrying about overwriting the existing images there, and also makes the script run more efficiently, as it only does the more intensive work of guessing font sizes, fitting the quotes, and creating the images, if the image doesn't already exist. 

It just does this check in the images directory, not the metadata directory. If you want to force the regeneration of a specific image for any reason (e.g. you fixed a typo), just delete that image from the "images" directory, no need to touch the metadata directory, and it'll regenerate both.

# Custom Image Sizes
The image generator now supports custom and pre-configured alternative image sizes. The default size will remain the old Kindle size (600 x 800) but you now have the option to run the script with command line arguments to choose from preconfigured sizes or set your own. 

To use this, simply add your command line argument after the php file when you run it, e.g.
php quote_to_image.php paperwhite

The following preconfigured sizes exist:
* paperwhite
* oasis

You can also set a custom image size using the "custom" argument and providing the width and height immediately after, e.g.
php quote_to_image.php custom 750 1024

# CSV file
I've begun filling in some extra times with books I enjoy. In some cases, I've simply added to times where there already were some entries, to include books I like. I have also added some entries where times did not exist already.

# Missing Times

As of right now, the times are complete (afaik). However, there is still a Google Form to gather any times people come across while reading: https://docs.google.com/forms/d/1TpjlPc1VI9-tnI7yPSvtHE6FefLJ4IbbtVKwfy7C9ds/edit

Feel free to add one if you come across a time while reading, or to fork this repo to make updates to the source CSV file!

# Thanks
Immeasurable thanks to all who have contributed to this repo, fixing typos and code issues. Special thanks to @peterjaap for automating the image generation using git actions!
