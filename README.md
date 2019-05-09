# LiteraryClock
A repo to host improvements to the literary clock project kicked off by Jaap Meijers

Jaap Meijers shared instructions to create a literary clock using an old Kindle here: https://www.instructables.com/id/Literary-Clock-Made-From-E-reader/

I wanted to make some changes to the scripts, and to the provided CSV files.

# Scripts
I've modified the quote_to_image file so that it first checks to see if an image already exists before creating it. This means that you can run the script against the provided image folder without worrying about overwriting the existing images there, and also makes the script run more efficiently, as it only does the more intensive work of guessing font sizes, fitting the quotes, and creating the images, if the image doesn't already exist. 

It just does this check in the images directory, not the metadata directory. If you want to force the regeneration of a specific image for any reason (e.g. you fixed a typo), just delete that image from the "images" directory, no need to touch the metadata directory, and it'll regenerate both.

# CSV file
I've begun filling in some extra times with books I enjoy. In some cases, I've simply added to times where there already were some entries, to include books I like. I have also added some entries where times did not exist already.

# Missing Times
I've written a script to filter the csv and pull out a list of missing times, which I will keep up to date in a publicly accessible google spreadsheet for now - https://docs.google.com/spreadsheets/d/1yBXgmuMIZrLkkigTW2vqU3ugJMpyWyEhQPGm9qNHuZ8/edit?usp=sharing

There is also a Google Form to gather any times people come across while reading: https://docs.google.com/forms/d/1TpjlPc1VI9-tnI7yPSvtHE6FefLJ4IbbtVKwfy7C9ds/edit

Feel free to add one if you come across a time while reading!
