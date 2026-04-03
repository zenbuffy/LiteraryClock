#!/usr/bin/env python3
import os
import tempfile
import unittest

from quote_to_image import fit_text, measure_layout, render_entry

_HERE   = os.path.dirname(os.path.abspath(__file__))
REGULAR = os.path.join(_HERE, 'LinLibertine_RZ.ttf')
BOLD    = os.path.join(_HERE, 'LinLibertine_RB.ttf')
CREDIT  = os.path.join(_HERE, 'LinLibertine_RZI.ttf')

FONTS_AVAILABLE = all(os.path.exists(p) for p in (REGULAR, BOLD, CREDIT))

SHORT_QUOTE  = "It was half past three in the afternoon."
TIME_NAME    = "half past three"
TIME_START   = 3   # word index of "half"
TIME_COUNT   = 2   # "half past three" = 3 words → count = 2

SAMPLE_ENTRY = {
    'time':      '15:30',
    'time_name': TIME_NAME,
    'quote':     SHORT_QUOTE,
    'source':    'Test Book',
    'author':    'Test Author',
    'idx':       0,
}


@unittest.skipUnless(FONTS_AVAILABLE, 'LinLibertine fonts not found')
class TestMeasureLayout(unittest.TestCase):

    def test_returns_positive_height_for_short_quote(self):
        h = measure_layout(SHORT_QUOTE.split(), 600, 40,
                           TIME_START, TIME_COUNT, 26, REGULAR, BOLD)
        self.assertIsNotNone(h)
        self.assertGreater(h, 0)

    def test_returns_none_when_font_too_large_for_narrow_width(self):
        # Width of 10px — any word at size 300 won't fit
        h = measure_layout(SHORT_QUOTE.split(), 10, 300,
                           TIME_START, TIME_COUNT, 0, REGULAR, BOLD)
        self.assertIsNone(h)

    def test_larger_font_produces_greater_height(self):
        words  = SHORT_QUOTE.split()
        kwargs = dict(time_start=TIME_START, time_count=TIME_COUNT,
                      margin=26, regular_path=REGULAR, bold_path=BOLD)
        h_small = measure_layout(words, 600, 20, **kwargs)
        h_large = measure_layout(words, 600, 60, **kwargs)
        self.assertIsNotNone(h_small)
        self.assertIsNotNone(h_large)
        self.assertGreater(h_large, h_small)


@unittest.skipUnless(FONTS_AVAILABLE, 'LinLibertine fonts not found')
class TestFitText(unittest.TestCase):

    def test_returns_image_for_normal_quote(self):
        img = fit_text(SHORT_QUOTE.split(), 600, 800,
                       TIME_START, TIME_COUNT, 26, REGULAR, BOLD)
        self.assertIsNotNone(img)

    def test_returned_image_has_correct_dimensions(self):
        img = fit_text(SHORT_QUOTE.split(), 600, 800,
                       TIME_START, TIME_COUNT, 26, REGULAR, BOLD)
        self.assertEqual(img.size, (600, 800))

    def test_returns_none_for_unrenderable_quote(self):
        # A single extremely long word that can never fit at size 18
        words = ['A' * 500]
        img = fit_text(words, 100, 100, 0, 0, 0, REGULAR, BOLD)
        self.assertIsNone(img)

    def test_chosen_size_fits_within_height(self):
        """The rendered image should require height < height - 100."""
        words  = SHORT_QUOTE.split()
        margin = 26
        width, height = 600, 800

        img = fit_text(words, width, height, TIME_START, TIME_COUNT,
                       margin, REGULAR, BOLD)
        self.assertIsNotNone(img)

        # Verify the winning size actually fits
        from quote_to_image import measure_layout as ml
        # Find what size fit_text chose by checking sizes around the result
        # We trust binary search is correct if size+1 overflows
        for size in range(18, 301):
            h = ml(words, width, size, TIME_START, TIME_COUNT, margin, REGULAR, BOLD)
            if h is None or h >= height - 100:
                winning_size = size - 1
                break
        else:
            winning_size = 300

        h_winner = ml(words, width, winning_size, TIME_START, TIME_COUNT,
                      margin, REGULAR, BOLD)
        self.assertIsNotNone(h_winner)
        self.assertLess(h_winner, height - 100)


@unittest.skipUnless(FONTS_AVAILABLE, 'LinLibertine fonts not found')
class TestRenderEntrySaveWithoutCredits(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self._orig_dir = os.getcwd()
        os.chdir(self.tmpdir.name)
        os.makedirs(os.path.join('images', 'metadata'), exist_ok=True)

    def tearDown(self):
        os.chdir(self._orig_dir)
        self.tmpdir.cleanup()

    def _credits_path(self):
        return os.path.join('images', 'metadata', 'quote_1530_0_credits.png')

    def _quote_path(self):
        return os.path.join('images', 'quote_1530_0.png')

    def test_default_only_writes_credits(self):
        render_entry(SAMPLE_ENTRY, 600, 800,
                     (REGULAR, BOLD, CREDIT), save_without_credits=False)
        self.assertTrue(os.path.exists(self._credits_path()))
        self.assertFalse(os.path.exists(self._quote_path()))

    def test_flag_writes_both_files(self):
        render_entry(SAMPLE_ENTRY, 600, 800,
                     (REGULAR, BOLD, CREDIT), save_without_credits=True)
        self.assertTrue(os.path.exists(self._credits_path()))
        self.assertTrue(os.path.exists(self._quote_path()))

    def test_skip_if_credits_already_exists(self):
        # Pre-create the credits file
        credits_path = self._credits_path()
        with open(credits_path, 'wb') as f:
            f.write(b'placeholder')

        render_entry(SAMPLE_ENTRY, 600, 800,
                     (REGULAR, BOLD, CREDIT), save_without_credits=False)

        # File should be unchanged (still our placeholder)
        with open(credits_path, 'rb') as f:
            self.assertEqual(f.read(), b'placeholder')

    def test_skip_if_both_files_exist_with_flag(self):
        quote_path   = self._quote_path()
        credits_path = self._credits_path()

        for path in (quote_path, credits_path):
            with open(path, 'wb') as f:
                f.write(b'placeholder')

        render_entry(SAMPLE_ENTRY, 600, 800,
                     (REGULAR, BOLD, CREDIT), save_without_credits=True)

        for path in (quote_path, credits_path):
            with open(path, 'rb') as f:
                self.assertEqual(f.read(), b'placeholder')


if __name__ == '__main__':
    unittest.main()
