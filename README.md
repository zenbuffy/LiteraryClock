# LiteraryClock
A repo to host improvements to the literary clock project kicked off by Jaap Meijers

Jaap Meijers shared instructions to create a literary clock using an old Kindle here: https://www.instructables.com/id/Literary-Clock-Made-From-E-reader/

I wanted to make some changes to the scripts, and to the provided CSV files.

# Scripts
I've modified the quote_to_php file so that it first checks to see if an image already exists before creating it. This means that you can run the script against the provided image folder without worrying about overwriting the existing images there, and also makes the script run more efficiently, as it only does the more intensive work of guessing font sizes, fitting the quotes, and creating the images, if the image doesn't already exist. 

# CSV file
I've begun filling in some extra times with books I enjoy. In some cases, I've simply added to times where there already were some entries, to include books I like. I have also added some entries where times did not exist already.
