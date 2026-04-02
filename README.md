# LiteraryClock
A repo to host improvements to the literary clock project kicked off by Jaap Meijers

Jaap Meijers shared instructions to create a literary clock using an old Kindle here: https://www.instructables.com/id/Literary-Clock-Made-From-E-reader/

I wanted to make some changes to the scripts, and to the provided CSV files.

# Prerequisites
To get the PHP script working on my Linux box, I need to install the following php packages:
* php-cli
* php-gd
* php-imagick
* imagemagick

The Linux Libertine fonts are included in the repository root, so no separate font download is needed.

# Scripts
I've modified the quote_to_image file so that it first checks to see if an image already exists before creating it. This means that you can run the script against the provided image folder without worrying about overwriting the existing images there, and also makes the script run more efficiently, as it only does the more intensive work of guessing font sizes, fitting the quotes, and creating the images, if the image doesn't already exist. 

It just does this check in the images directory, not the metadata directory. If you want to force the regeneration of a specific image for any reason (e.g. you fixed a typo), just delete that image from the "images" directory, no need to touch the metadata directory, and it'll regenerate both.

# Adding a quote

Run `./insert_quote.py` to add a quote to the YAML file, then run `./yaml_to_formats.py` to regenerate the CSV and JSON files from it.

Sample command:
```
$ ./insert_quote.py --time '01:00' --time_human '1 am' --source 'The Best Example Book' --author 'Ian M Banks' "This is a test. Isn't it fun! \"Go forth and have fun\""
$ ./yaml_to_formats.py
```

# Custom Image Sizes
The image generator now supports custom and pre-configured alternative image sizes. The default size will remain the old Kindle size (600 x 800) but you now have the option to run the script with command line arguments to choose from preconfigured sizes or set your own. 

To use this, simply add your command line argument after the php file when you run it, e.g.

`php quote_to_image.php paperwhite`

The following preconfigured sizes exist:

| Argument | Device | Resolution |
|----------|--------|------------|
| *(none)* | Kindle 1st–4th gen (default) | 600 × 800 |
| `paperwhite` | Kindle Paperwhite 1–3 (older) | 758 × 1024 |
| `paperwhite5` | Kindle Paperwhite 11th gen (2021) | 1236 × 1648 |
| `kindle` / `basic` | Kindle 11th gen (2022) | 1072 × 1448 |
| `oasis` | Kindle Oasis (10th gen) | 1264 × 1680 |
| `scribe` | Kindle Scribe | 1860 × 2480 |
| `clara` | Kobo Clara 2E / Clara BW | 1072 × 1448 |
| `libra` | Kobo Libra 2 / Libra Colour | 1264 × 1680 |
| `sage` | Kobo Sage | 1440 × 1920 |
| `elipsa` | Kobo Elipsa 2E | 1404 × 1872 |
| `remarkable` | reMarkable 2 | 1404 × 1872 |
| `remarkablepro` | reMarkable Paper Pro | 1620 × 2160 |

You can also set a custom image size using the "custom" argument and providing the width and height immediately after, e.g.

`php quote_to_image.php custom 750 1024`

# CSV file
I've begun filling in some extra times with books I enjoy. In some cases, I've simply added to times where there already were some entries, to include books I like. I have also added some entries where times did not exist already.

# Missing Times

There are still some times missing — see `missing_times.md` for the current list. There is also a Google Form to gather any times people come across while reading: https://docs.google.com/forms/d/1TpjlPc1VI9-tnI7yPSvtHE6FefLJ4IbbtVKwfy7C9ds/edit

Feel free to add one if you come across a time while reading, or to fork this repo to make updates to the source YAML file!

# Thanks
Immeasurable thanks to all who have contributed to this repo, fixing typos and code issues. Special thanks to @peterjaap for automating the image generation using git actions! Thanks also to the people submitting times via the Google Form:
* Joel Becker
* Jaap Meijers
* Darryl Lee
* and all the anonymous submitters!
