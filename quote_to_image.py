#!/usr/bin/env python3
"""Generate literary clock images from litclock.yaml."""

import argparse
import os
import sys
from functools import partial
from multiprocessing import Pool, cpu_count

import yaml
from PIL import Image, ImageDraw, ImageFont

DEVICE_PRESETS = {
    'kindle':           (600,  800),
    'basic':            (1072, 1448),
    'paperwhite':       (758,  1024),
    'paperwhite5':      (1236, 1648),
    'oasis':            (1264, 1680),
    'scribe':           (1860, 2480),
    'clara':            (1072, 1448),
    'libra':            (1264, 1680),
    'sage':             (1440, 1920),
    'elipsa':           (1404, 1872),
    'remarkable':       (1404, 1872),
    'remarkablepro':    (1620, 2160),
    'inkyphat':         (104,  212),
    'inkyphat_l':       (212,  104),
    'inkywhat':         (300,  400),
    'inkywhat_l':       (400,  300),
    'inkyimpression':   (448,  600),
    'inkyimpression_l': (600,  448),
    'waveshare75':      (480,  800),
    'waveshare75_l':    (800,  480),
    'it8951':           (1404, 1872),
    'it8951_l':         (1872, 1404),
}


def resolve_font(ttf, otf):
    """Return ttf path if it exists, otf path if not, or None if neither."""
    if os.path.exists(ttf):
        return ttf
    if os.path.exists(otf):
        return otf
    print(f'ERROR: Unable to find font file: {ttf} or {otf}', file=sys.stderr)
    return None


def measure_layout(words, width, font_size, time_start, time_count, margin,
                   regular_path, bold_path):
    """
    Simulate word layout at font_size without creating an image.
    Returns the final y position (paragraph height), or None if a single word is too wide.
    """
    regular = ImageFont.truetype(regular_path, font_size)
    bold    = ImageFont.truetype(bold_path,    font_size)

    x = margin
    y = margin + font_size

    for i, word in enumerate(words):
        font = bold if time_start <= i <= time_start + time_count else regular
        w = int(font.getlength(word + ' '))

        if w > width - margin:
            return None  # single word too wide at this size

        if x + w >= width - margin:
            x  = margin
            y += int(font_size * 1.618)  # golden ratio line height

        x += w

    return y


def render_image(words, width, height, font_size, time_start, time_count, margin,
                 regular_path, bold_path):
    """
    Render words onto a greyscale PIL Image at the given font_size.
    Time-string words: black + bold. All others: grey + regular.
    """
    regular = ImageFont.truetype(regular_path, font_size)
    bold    = ImageFont.truetype(bold_path,    font_size)

    img  = Image.new('L', (width, height), 255)
    draw = ImageDraw.Draw(img)

    x = margin
    y = margin + font_size

    for i, word in enumerate(words):
        if time_start <= i <= time_start + time_count:
            font  = bold
            color = 0    # black
        else:
            font  = regular
            color = 125  # grey

        w = int(font.getlength(word + ' '))

        if x + w >= width - margin:
            x  = margin
            y += int(font_size * 1.618)

        draw.text((x, y), word, font=font, fill=color, anchor='ls')
        x += w

    return img


def fit_text(words, width, height, font_size, time_start, time_count, margin,
             regular_path, bold_path):
    """
    Find the largest font size where text fits within height - 100.
    Returns a rendered PIL Image, or None if the minimum size doesn't fit.
    """
    best = None
    size = font_size

    while True:
        h = measure_layout(words, width, size, time_start, time_count, margin,
                           regular_path, bold_path)
        if h is None or h >= height - 100:
            break
        best = size
        size += 1

    if best is None:
        return None

    return render_image(words, width, height, best, time_start, time_count, margin,
                        regular_path, bold_path)


def _draw_credits(img, width, height, margin, credit_path, source, author):
    """Draw right-aligned credits onto img in-place."""
    draw        = ImageDraw.Draw(img)
    credit_font = ImageFont.truetype(credit_path, 18)
    em_dash     = '\u2014'
    credits     = f'{source}, {author}'
    full_text   = f'{em_dash}{credits}'
    text_width  = int(credit_font.getlength(full_text))

    if text_width > 500:
        # split credits (without dash) into two balanced lines
        words_c = credits.split()
        line1, line2 = credits, ''
        for i in range(1, len(words_c)):
            l1 = ' '.join(words_c[:-i])
            l2 = ' '.join(words_c[-i:])
            if len(l2) + 5 > len(l1):
                break
            line1, line2 = l1, l2

        full_line1  = f'{em_dash}{line1}'
        w1          = int(credit_font.getlength(full_line1))
        w2          = int(credit_font.getlength(line2))
        bbox1       = credit_font.getbbox(full_line1)
        line_height = int((bbox1[3] - bbox1[1]) * 1.1)

        draw.text((width - w1 - margin, height - margin - line_height),
                  full_line1, font=credit_font, fill=0, anchor='ls')
        draw.text((width - w2 - margin, height - margin),
                  line2, font=credit_font, fill=0, anchor='ls')
    else:
        draw.text((width - text_width - margin, height - margin),
                  full_text, font=credit_font, fill=0, anchor='ls')


def render_entry(entry, width, height, font_paths):
    """
    Render quote and credits images for one entry.
    Top-level function (required for multiprocessing pickling).
    """
    regular_path, bold_path, credit_path = font_paths

    time_key = entry['time'].replace(':', '')
    idx      = entry['idx']

    quote_out   = os.path.join('images', f'quote_{time_key}_{idx}.png')
    credits_out = os.path.join('images', 'metadata', f'quote_{time_key}_{idx}_credits.png')

    if os.path.exists(quote_out) and os.path.exists(credits_out):
        return

    margin     = 26
    timestring = entry['time_name'].strip()
    quote      = ' '.join(entry['quote'].split())  # normalise whitespace
    words      = quote.split()

    # find word index where the time string begins (case-insensitive)
    lower_quote = quote.lower()
    lower_time  = timestring.lower()
    pos = lower_quote.find(lower_time)
    if pos == -1:
        time_start = 0
        time_count = 0
    else:
        # snap back to the nearest word boundary so a mid-word pos doesn't
        # cause before.split() to count the preceding partial word
        while pos > 0 and quote[pos - 1] != ' ':
            pos -= 1
        before     = quote[:pos]
        time_start = len(before.split())
        time_count = len(timestring.split()) - 1

    print(f'Making image for {time_key}_{idx}')

    img = fit_text(words, width, height, 18, time_start, time_count, margin,
                   regular_path, bold_path)
    if img is None:
        print(f'WARNING: could not fit text for {time_key}_{idx}, skipping',
              file=sys.stderr)
        return

    img.save(quote_out)

    _draw_credits(img, width, height, margin, credit_path,
                  entry['source'].strip(), entry['author'].strip())
    img.save(credits_out)


def main():
    parser = argparse.ArgumentParser(
        description='Generate literary clock images from litclock.yaml.')
    parser.add_argument(
        '--device', default='kindle',
        help=f'Device preset, case-insensitive (default: kindle). '
             f'Known: {", ".join(DEVICE_PRESETS)}')
    parser.add_argument('--width',   type=int, help='Override image width in pixels')
    parser.add_argument('--height',  type=int, help='Override image height in pixels')
    parser.add_argument('--all',     action='store_true', dest='include_nsfw',
                        help='Include NSFW quotes (omitted by default)')
    parser.add_argument('--workers', type=int, default=cpu_count(),
                        help='Parallel worker processes (default: CPU count)')
    args = parser.parse_args()

    device = args.device.lower()
    if device not in DEVICE_PRESETS:
        print(f"ERROR: Unknown device '{args.device}'. "
              f"Known: {', '.join(DEVICE_PRESETS)}", file=sys.stderr)
        sys.exit(1)

    width, height = DEVICE_PRESETS[device]
    if args.width is not None:
        width = args.width
    if args.height is not None:
        height = args.height

    regular_path = resolve_font('LinLibertine_RZ.ttf',  'LinLibertine_RZ.otf')
    bold_path    = resolve_font('LinLibertine_RB.ttf',  'LinLibertine_RB.otf')
    credit_path  = resolve_font('LinLibertine_RZI.ttf', 'LinLibertine_RZI.otf')

    if None in (regular_path, bold_path, credit_path):
        print('ERROR: Missing font files. Download LinLibertine from '
              'https://sourceforge.net/projects/linuxlibertine/', file=sys.stderr)
        sys.exit(1)

    os.makedirs(os.path.join('images', 'metadata'), exist_ok=True)

    with open('litclock.yaml', encoding='utf-8') as f:
        entries = yaml.safe_load(f)

    if not args.include_nsfw:
        entries = [e for e in entries if e.get('sfw', 'yes') != 'no']

    # assign indices before parallelising — order must be preserved
    time_counts: dict = {}
    tasks = []
    for entry in entries:
        t   = entry['time'].replace(':', '')
        idx = time_counts.get(t, 0)
        time_counts[t] = idx + 1
        tasks.append({**entry, 'idx': idx})

    font_paths = (regular_path, bold_path, credit_path)
    worker     = partial(render_entry, width=width, height=height, font_paths=font_paths)

    with Pool(args.workers) as pool:
        pool.map(worker, tasks)


if __name__ == '__main__':
    main()
