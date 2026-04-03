# LiteraryClock
A repo to host improvements to the literary clock project kicked off by Jaap Meijers

Jaap Meijers shared instructions to create a literary clock using an old Kindle here: https://www.instructables.com/id/Literary-Clock-Made-From-E-reader/

I wanted to make some changes to the scripts, and to the provided CSV files.

# Prerequisites

```bash
pip install "Pillow>=9.2" pyyaml
```

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

Quotes are marked as safe for work (SFW) by default. Use `--nsfw` to flag a quote as not safe for work:
```
$ ./insert_quote.py --nsfw --time '23:00' --time_human '11 pm' --source 'Some Book' --author 'Some Author' "An adult quote."
```

# Image Generation

Run `quote_to_image.py` to generate images. By default it generates for the original Kindle size (600 × 800):

```bash
python quote_to_image.py
```

Use `--device` to select a preset, or `--width`/`--height` to set a custom size:

```bash
python quote_to_image.py --device paperwhite
python quote_to_image.py --width 750 --height 1024
python quote_to_image.py --workers 8   # parallel workers, defaults to CPU count
```

The following device presets are available:

| `--device` | Device | Resolution |
|------------|--------|------------|
| *(none / `kindle`)* | Kindle 1st–4th gen (default) | 600 × 800 |
| `paperwhite` | Kindle Paperwhite 1–3 (older) | 758 × 1024 |
| `paperwhite5` | Kindle Paperwhite 11th gen (2021) | 1236 × 1648 |
| `basic` | Kindle 11th gen (2022) | 1072 × 1448 |
| `oasis` | Kindle Oasis (10th gen) | 1264 × 1680 |
| `scribe` | Kindle Scribe | 1860 × 2480 |
| `clara` | Kobo Clara 2E / Clara BW | 1072 × 1448 |
| `libra` | Kobo Libra 2 / Libra Colour | 1264 × 1680 |
| `sage` | Kobo Sage | 1440 × 1920 |
| `elipsa` | Kobo Elipsa 2E | 1404 × 1872 |
| `remarkable` | reMarkable 2 | 1404 × 1872 |
| `remarkablepro` | reMarkable Paper Pro | 1620 × 2160 |
| `inkyphat` | Inky pHAT (portrait) | 104 × 212 |
| `inkyphat_l` | Inky pHAT (landscape) | 212 × 104 |
| `inkywhat` | Inky wHAT (portrait) | 300 × 400 |
| `inkywhat_l` | Inky wHAT (landscape) | 400 × 300 |
| `inkyimpression` | Inky Impression (portrait) | 448 × 600 |
| `inkyimpression_l` | Inky Impression (landscape) | 600 × 448 |
| `waveshare75` | Waveshare 7.5" (portrait) | 480 × 800 |
| `waveshare75_l` | Waveshare 7.5" (landscape) | 800 × 480 |
| `it8951` | IT8951 10.3" (portrait) | 1404 × 1872 |
| `it8951_l` | IT8951 10.3" (landscape) | 1872 × 1404 |

# Content Filtering

By default, the image generator skips quotes marked as not safe for work (NSFW). To generate images for all quotes including NSFW ones, pass the `--all` flag:

```bash
python quote_to_image.py --all
python quote_to_image.py --device paperwhite --all
python quote_to_image.py --width 750 --height 1024 --all
```

Note: quotes imported from the original data set predate this classification and are treated as SFW. Only quotes sourced from the [literature-clock](https://github.com/flisoldf/literature-clock) project carry explicit `sfw: yes/no` metadata.

# Kindle Scripts

The scripts in `KindleScripts/` run on the Kindle itself and are deployed to `/mnt/us/timelit/` on the device.

## timelit.sh

This is the main display script, called every minute by cron. It has been updated with the following features:

**Timezone** — Set to `Europe/Dublin`. Change the `TZ=Europe/Dublin` value on the `MinuteOTheDay` line (and the sleep-hour check above it) to match your local timezone, using a tz database name (e.g. `Europe/London`, `America/New_York`).

**Sleep hours** — The script exits without updating the display between 1am and 6am to save power. The e-ink screen holds the last image without drawing any power. Adjust the hours in the `if [ "$hour" -ge 1 ] && [ "$hour" -lt 6 ]` check if needed.

**Battery warning** — If the Kindle's battery drops below 20%, the current charge percentage is overlaid on the displayed image. This threshold can be adjusted by changing `[ "$battery" -lt 20 ]`.

## synctime.sh

This script briefly enables WiFi to allow the Kindle's NTP client to sync the system clock, then disables WiFi again. It is intended to run once a day just before the clock wakes from its sleep hours.

**Deployment:** Copy `synctime.sh` to `/mnt/us/timelit/synctime.sh` on the Kindle.

**Cron entry:** Add the following to the Kindle's crontab (at `/etc/crontab/root`, after remounting the filesystem read-write with `mntroot rw`):

```
55 5 * * * sh /mnt/us/timelit/synctime.sh
```

This runs the sync at 05:55, giving it time to complete before the clock resumes at 06:00.

## literary_clock.sh (Scriptlet)

A modern alternative to the multi-script SSH+Launchpad approach. A single file that appears in your Kindle's library and runs when tapped — no SSH, no Launchpad, no pre-generated images required (when FBInk is available).

### Prerequisites

- Kindle jailbroken with [Winterbreak](https://kindlemodding.org)
- **FBInk** installed — binaries in [NiLuJe's MobileRead thread](https://www.mobileread.com/forums/showthread.php?t=299620), source at [github.com/NiLuJe/FBInk](https://github.com/NiLuJe/FBInk) *(optional — see fallback below)*

### FBInk path (recommended — no images needed)

Connect the Kindle via USB — it appears as a removable drive (e.g. `Kindle (E:)` on Windows). The drive root maps to `/mnt/us/` on the device. Copy three files:

| Source (repo) | Destination on Kindle drive |
|---|---|
| `KindleScripts/literary_clock.sh` | `documents\literary_clock.sh` |
| `litclock_annotated_improved.csv` | `timelit\litclock_annotated_improved.csv` |
| `LinLibertine_RZ.ttf` (repo root) | `timelit\LinLibertine_RZ.ttf` |

Create the `timelit` folder on the drive if it doesn't exist. The `documents` folder should already be there.

The scriptlet will appear in your Kindle library as **Literary Clock**. Tap it to start the clock. Tap it again to stop.

### eips fallback path (no FBInk required)

If FBInk is not installed, the scriptlet automatically falls back to displaying pre-generated PNG images via `eips`. First generate images for your device (see Image Generation table above for presets):

```bash
python quote_to_image.py --device basic
```

Then copy to the Kindle drive:

| Source (repo) | Destination on Kindle drive |
|---|---|
| `KindleScripts/literary_clock.sh` | `documents\literary_clock.sh` |
| `images/` folder | `timelit\images\` |

### Usage

- **Start clock:** tap *Literary Clock* in your library
- **Stop clock:** navigate home, tap *Literary Clock* again
- The display updates at each minute boundary
- Timezone is read from the Kindle system clock (set via your Amazon account)

# Pi Scripts

The scripts in `PiScripts/` run on a Raspberry Pi with an e-ink HAT, and are deployed to `/home/pi/timelit/` on the device (the path is configurable).

## Prerequisites

Enable SPI on the Pi if you haven't already: `sudo raspi-config` → Interface Options → SPI → Enable.

Install Python dependencies on the Pi:

```
pip3 install pillow pytz
```

Then install the library for your display:

| Display | Library |
|---|---|
| Inky (pHAT / wHAT / Impression) | `pip3 install inky` |
| Waveshare | Clone [waveshare/e-Paper](https://github.com/waveshare/e-Paper), see note in script |
| IT8951-based panels | `pip3 install IT8951` |

## Generating images for your Pi display

Run `quote_to_image.py` with the preset for your display (see Image Generation table above), then copy the generated `images/` folder to your Pi:

```bash
python quote_to_image.py --device waveshare75
scp -r images/ pi@raspberrypi.local:/home/pi/timelit/
```

## Setup

1. Copy `PiScripts/timelit.py` to `/home/pi/timelit/PiScripts/timelit.py` on the Pi.
2. Edit the config block at the top of `timelit.py` — set `DISPLAY_TYPE`, `CLOCK_DIR`, `IMAGES_DIR` (must point to wherever you copied the images), and `TIMEZONE`.
3. Enable the clock by creating the flag file:
   ```
   touch /home/pi/timelit/clockisticking
   ```
   Remove this file at any time to pause the clock without touching cron.
4. Add the cron entry to run the script every minute:
   ```
   * * * * * /usr/bin/python3 /home/pi/timelit/PiScripts/timelit.py
   ```

## timelit.py

This is the main display script, called every minute by cron.

**Display type** — Set `DISPLAY_TYPE` to `"inky"`, `"waveshare"`, or `"it8951"` to match your hardware. Each branch contains comments for library installation and, where relevant, notes on adapting it to different module sizes within the same family.

**Timezone** — Set `TIMEZONE` to a tz database name matching your location (e.g. `Europe/London`, `America/New_York`).

**Sleep hours** — The script exits without updating the display between `SLEEP_START` and `SLEEP_END` to save power. The e-ink screen holds the last image without drawing any power. Defaults to 1am–6am.

**clockisticking** — The script checks for a flag file at `CLOCK_DIR/clockisticking` before doing anything. If the file is absent, the script exits immediately. This lets you pause the clock without modifying cron.

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

A significant portion of the quote data was merged from the [literature-clock](https://github.com/JohannesNE/literature-clock) project by [Johannes Evoldsen](https://github.com/JohannesNE), itself based on the original work by Jaap Meijers. Many thanks to Johannes and all contributors to that project.
