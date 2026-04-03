#!/usr/bin/env python3

# ── Configuration ──────────────────────────────────────────────────────────────
DISPLAY_TYPE = "inky"              # "inky" | "waveshare" | "it8951"
CLOCK_DIR    = "/home/pi/timelit"  # clockisticking flag lives here
IMAGES_DIR   = "/home/pi/timelit/images"
TIMEZONE     = "Europe/Dublin"
SLEEP_START  = 1                   # hour to stop displaying (saves power)
SLEEP_END    = 6                   # hour to resume
# ───────────────────────────────────────────────────────────────────────────────

# Cron entry (run every minute):
# * * * * * /usr/bin/python3 /home/pi/timelit/PiScripts/timelit.py

import glob
import os
import random
import sys
from datetime import datetime

import pytz
from PIL import Image

# Only run if the clockisticking flag file exists.
# Create it with: touch /home/pi/timelit/clockisticking
# Remove it to pause the clock without touching cron.
if not os.path.isfile(os.path.join(CLOCK_DIR, "clockisticking")):
    sys.exit()

# Sleep between SLEEP_START and SLEEP_END to save power.
# The e-ink screen holds its last image without drawing power.
tz = pytz.timezone(TIMEZONE)
now = datetime.now(tz)
if SLEEP_START <= now.hour < SLEEP_END:
    sys.exit()

# Find images for the current minute
minute = now.strftime("%H%M")
images = glob.glob(os.path.join(IMAGES_DIR, f"quote_{minute}*.png"))
if not images:
    sys.exit()

# Pick one at random (multiple quotes may exist for the same minute)
img_path = random.choice(images)

if DISPLAY_TYPE == "inky":
    # pip3 install inky
    from inky.auto import auto
    img = Image.open(img_path)
    display = auto(ask_user=True, verbose=True)
    display.set_image(img)
    display.show()

elif DISPLAY_TYPE == "waveshare":
    # Install from https://github.com/waveshare/e-Paper
    # Uncomment if installed as local source:
    # sys.path.append("/home/pi/e-Paper/RaspberryPi_JetsonNano/python/lib")
    #
    # This example targets the 7.5" V2 module. For other sizes change the import,
    # e.g. epd2in13_V3, epd4in2, epd5in83_V2, etc.
    from waveshare_epd import epd7in5_V2
    img = Image.open(img_path).convert("1")  # dither to 1-bit B&W
    epd = epd7in5_V2.EPD()
    epd.init()
    epd.display(epd.getbuffer(img))
    epd.sleep()

elif DISPLAY_TYPE == "it8951":
    # pip3 install IT8951
    # Uncomment if installed as local source:
    # sys.path.append("/home/pi/IT8951")
    from IT8951 import constants
    from IT8951.display import AutoEPDDisplay
    img = Image.open(img_path).convert("L")  # grayscale — IT8951 supports 16 levels
    display = AutoEPDDisplay(vcom=-2.06)      # adjust vcom to match label on your panel
    display.frame_buf.paste(img)
    display.draw_full(constants.DisplayModes.GC16)
