<?php

// this script turns quotes from books into images for use in a Kindle clock.
// Jaap Meijers, 2018

require __DIR__ . '/vendor/autoload.php';

use Symfony\Component\Yaml\Yaml;

if (realpath(__FILE__) === realpath($_SERVER['SCRIPT_FILENAME'] ?? '')) {
    error_reporting(E_ALL);
    ini_set('display_errors', 1);
    ini_set('max_execution_time', 3000);

    if (!is_dir('images/metadata') && !mkdir('images/metadata', 0777, true)) {
        throw new \RuntimeException(sprintf('Directory "%s" was not created', 'images/metadata'));
    }

    $imagenumber = 0;
    $previoustime = 0;

    putenv('GDFONTPATH=' . realpath('.'));

    InitializeFonts();

    // Check for --all flag (include NSFW quotes); strip it before device parsing
    $includeNsfw = in_array('--all', $argv);
    $filteredArgv = array_values(array_filter($argv, fn($a) => $a !== '--all'));
    setDevice($filteredArgv);

    // get the quotes (including title and author) from the YAML file,
    // and create unique images for them, one without and one with title and author
    $entries = Yaml::parseFile('litclock.yaml');
    foreach ($entries as $entry) {
        // Skip NSFW quotes unless --all flag is set.
        // Entries without an 'sfw' field (original entries) are treated as SFW.
        if (!$includeNsfw && isset($entry['sfw']) && $entry['sfw'] === 'no') {
            continue;
        }

        $time       = $entry['time'];
        $timestring = trim($entry['time_name']);
        $quote      = trim(preg_replace('/\s+/', ' ', $entry['quote']));
        $title      = trim($entry['source']);
        $author     = trim($entry['author']);

        TurnQuoteIntoImage($time, $quote, $timestring, $title, $author);
    }
}

function setDevice($argv) {
    global $deviceWidth;
    global $deviceHeight;

    // default to Kindle size
    $deviceWidth = 600;
    $deviceHeight = 800;

    if (!empty($argv[1])) {
        $device = strtoupper($argv[1]);

        if ($device == "PAPERWHITE") {
            // Kindle Paperwhite 1–3 (older)
            $deviceWidth = 758;
            $deviceHeight = 1024;
        } elseif ($device == "PAPERWHITE5") {
            // Kindle Paperwhite 11th gen (2021), 6.8"
            $deviceWidth = 1236;
            $deviceHeight = 1648;
        } elseif ($device == "KINDLE" || $device == "BASIC") {
            // Kindle 11th gen (2022), 6"
            $deviceWidth = 1072;
            $deviceHeight = 1448;
        } elseif ($device == "OASIS") {
            // Kindle Oasis (10th gen), 7"
            $deviceWidth = 1264;
            $deviceHeight = 1680;
        } elseif ($device == "SCRIBE") {
            // Kindle Scribe, 10.2"
            $deviceWidth = 1860;
            $deviceHeight = 2480;
        } elseif ($device == "CLARA") {
            // Kobo Clara 2E / Clara BW, 6"
            $deviceWidth = 1072;
            $deviceHeight = 1448;
        } elseif ($device == "LIBRA") {
            // Kobo Libra 2 / Libra Colour, 7"
            $deviceWidth = 1264;
            $deviceHeight = 1680;
        } elseif ($device == "SAGE") {
            // Kobo Sage, 8"
            $deviceWidth = 1440;
            $deviceHeight = 1920;
        } elseif ($device == "ELIPSA") {
            // Kobo Elipsa 2E, 10.3"
            $deviceWidth = 1404;
            $deviceHeight = 1872;
        } elseif ($device == "REMARKABLE") {
            // reMarkable 2, 10.3"
            $deviceWidth = 1404;
            $deviceHeight = 1872;
        } elseif ($device == "REMARKABLEPRO") {
            // reMarkable Paper Pro, 11.8"
            $deviceWidth = 1620;
            $deviceHeight = 2160;
        } elseif ($device == "INKYPHAT") {
            // Inky pHAT (portrait)
            $deviceWidth = 104;
            $deviceHeight = 212;
        } elseif ($device == "INKYPHAT_L") {
            // Inky pHAT (landscape)
            $deviceWidth = 212;
            $deviceHeight = 104;
        } elseif ($device == "INKYWHAT") {
            // Inky wHAT (portrait)
            $deviceWidth = 300;
            $deviceHeight = 400;
        } elseif ($device == "INKYWHAT_L") {
            // Inky wHAT (landscape)
            $deviceWidth = 400;
            $deviceHeight = 300;
        } elseif ($device == "INKYIMPRESSION") {
            // Inky Impression (portrait)
            $deviceWidth = 448;
            $deviceHeight = 600;
        } elseif ($device == "INKYIMPRESSION_L") {
            // Inky Impression (landscape)
            $deviceWidth = 600;
            $deviceHeight = 448;
        } elseif ($device == "WAVESHARE75") {
            // Waveshare 7.5" (portrait)
            $deviceWidth = 480;
            $deviceHeight = 800;
        } elseif ($device == "WAVESHARE75_L") {
            // Waveshare 7.5" (landscape)
            $deviceWidth = 800;
            $deviceHeight = 480;
        } elseif ($device == "IT8951") {
            // IT8951 10.3" e-ink panel (portrait)
            $deviceWidth = 1404;
            $deviceHeight = 1872;
        } elseif ($device == "IT8951_L") {
            // IT8951 10.3" e-ink panel (landscape)
            $deviceWidth = 1872;
            $deviceHeight = 1404;
        } elseif ($device == "CUSTOM") {
            $deviceWidth = $argv[2];
            $deviceHeight = $argv[3];
        }
        // unrecognised device falls through to defaults set above
    }
}

function resolveFont($ttf, $otf) {
    if (file_exists($ttf)) {
        return $ttf;
    } elseif (file_exists($otf)) {
        return $otf;
    }
    print "ERROR: Unable to find font file: " . $ttf . " or " . $otf . PHP_EOL;
    return null;
}

function InitializeFonts()
{
    global $font_path;
    global $font_path_bold;
    global $creditFont;

    $font_path      = resolveFont('LinLibertine_RZ.ttf',  'LinLibertine_RZ.otf');
    $font_path_bold = resolveFont('LinLibertine_RB.ttf',  'LinLibertine_RB.otf');
    $creditFont     = resolveFont('LinLibertine_RZI.ttf', 'LinLibertine_RZI.otf');

    if ($font_path === null || $font_path_bold === null || $creditFont === null) {
        print "ERROR loading fonts!" . PHP_EOL;
        print "Please download and install the fonts from here: https://sourceforge.net/projects/linuxlibertine/ into the current directory." . PHP_EOL;
        exit;
    }
}


function TurnQuoteIntoImage($time, $quote, $timestring, $title, $author)
{
    global $font_path;
    global $font_path_bold;
    global $creditFont;
    global $deviceWidth;
    global $deviceHeight;

    $width  = $deviceWidth;
    $height = $deviceHeight;
    $margin = 26;

    // find the position and length of the timestring within the quote
    $timestringStarts     = count(explode(' ', stristr($quote, $timestring, true))) - 1;
    $timestring_wordcount = count(explode(' ', $timestring)) - 1;
    $quote_array          = explode(' ', $quote);

    $time      = substr($time, 0, 2) . substr($time, 3, 2);
    $font_size = 18;

    // serial number for when there is more than one quote for a certain minute
    global $imagenumber;
    global $previoustime;
    if ($time == $previoustime) {
        $imagenumber++;
    } else {
        $imagenumber = 0;
    }
    $previoustime = $time;

    $quotePath   = 'images/quote_' . $time . '_' . $imagenumber . '.png';
    $creditsPath = 'images/metadata/quote_' . $time . '_' . $imagenumber . '_credits.png';

    // Does the image already exist? No point in creating it again.
    if (file_exists($quotePath)) {
        return;
    }

    printf('Making a new image for ' . $time . PHP_EOL);
    if (PHP_SAPI !== 'cli') echo '<br />';

    ///// QUOTE /////
    // find the font size (recursively) for an optimal fit and create the image
    list($png_image) = fitText($quote_array, $width, $height, $font_size, $timestringStarts, $timestring_wordcount, $margin);

    print 'Image for ' . $time . '_' . $imagenumber . PHP_EOL;
    if (PHP_SAPI !== 'cli') echo '<br /><br />';

    imagepng($png_image, $quotePath);

    ///// METADATA /////
    // create another version, with title and author in the image
    $black   = imagecolorallocate($png_image, 0, 0, 0);
    $dash    = '—';
    $credits = $title . ', ' . $author;
    $creditFont_size = 18;

    list($metawidth, , $metaleft) = measureSizeOfTextbox($creditFont_size, $creditFont, $dash . $credits);

    if ($metawidth > 500) {
        $creditsArray = explode(' ', $credits);
        $newCredits   = array();
        $i = 1;

        while (true) {
            $tmp0 = implode(' ', array_slice($creditsArray, 0, count($creditsArray) - $i));
            $tmp1 = implode(' ', array_slice($creditsArray, 0 - $i));

            // once the second line is (almost) longer than the first, stop
            if (strlen($tmp1) + 5 > strlen($tmp0)) {
                break;
            }
            $newCredits[0] = $tmp0;
            $newCredits[1] = $tmp1;
            $i++;
        }

        list($textWidth1, $textheight1) = measureSizeOfTextbox($creditFont_size, $creditFont, $dash . $newCredits[0]);
        list($textWidth2)               = measureSizeOfTextbox($creditFont_size, $creditFont, $newCredits[1]);

        $metadataX1 = $width - ($textWidth1 + $margin);
        $metadataX2 = $width - ($textWidth2 + $margin);
        $metadataY  = $height - $margin;

        imagettftext($png_image, $creditFont_size, 0, $metadataX1, $metadataY - (int)($textheight1 * 1.1), $black, $creditFont, $dash . $newCredits[0]);
        imagettftext($png_image, $creditFont_size, 0, $metadataX2, $metadataY, $black, $creditFont, $newCredits[1]);
    } else {
        $metadataX = ($width - $metaleft) - $margin;
        $metadataY = $height - $margin;
        imagettftext($png_image, $creditFont_size, 0, $metadataX, $metadataY, $black, $creditFont, $dash . $credits);
    }

    imagepng($png_image, $creditsPath);
    imagedestroy($png_image);
}


// Measures text layout without creating an image. Returns paragraph height, or false if a word is too wide.
function measureLayout($quote_array, $width, $font_size, $timestringStarts, $timestring_wordcount, $margin)
{
    global $font_path_bold;
    global $font_path;

    $position = [$margin, $margin + $font_size];

    foreach ($quote_array as $key => $word) {
        $font = ($key >= $timestringStarts && $key <= $timestringStarts + $timestring_wordcount)
            ? $font_path_bold
            : $font_path;

        list($textwidth) = measureSizeOfTextbox($font_size, $font, $word . ' ');

        if ($textwidth > ($width - $margin)) {
            return false; // single word too wide at this size
        }

        if (($position[0] + $textwidth) >= ($width - $margin)) {
            $position[0] = $margin;
            $position[1] += (int)($font_size * 1.618); // golden ratio line height
        }

        $position[0] += $textwidth;
    }

    return $position[1];
}

// Creates the image at a specific font size.
function renderImage($quote_array, $width, $height, $font_size, $timestringStarts, $timestring_wordcount, $margin)
{
    global $font_path_bold;
    global $font_path;

    $png_image = imagecreate($width, $height)
        or die('Cannot Initialize new GD image stream');
    imagecolorallocate($png_image, 255, 255, 255); // background (first allocation sets fill color)

    $grey  = imagecolorallocate($png_image, 125, 125, 125);
    $black = imagecolorallocate($png_image, 0, 0, 0);

    $position = [$margin, $margin + $font_size];

    foreach ($quote_array as $key => $word) {
        // use bold + black for the timestring words, grey for the rest
        if ($key >= $timestringStarts && $key <= $timestringStarts + $timestring_wordcount) {
            $font      = $font_path_bold;
            $textcolor = $black;
        } else {
            $font      = $font_path;
            $textcolor = $grey;
        }

        list($textwidth) = measureSizeOfTextbox($font_size, $font, $word . ' ');

        if (($position[0] + $textwidth) >= ($width - $margin)) {
            $position[0] = $margin;
            $position[1] += (int)($font_size * 1.618); // golden ratio line height
        }

        imagettftext($png_image, $font_size, 0, $position[0], $position[1], $textcolor, $font, $word);
        $position[0] += $textwidth;
    }

    return [$png_image, $position[1], $font_size];
}

function fitText($quote_array, $width, $height, $font_size, $timestringStarts, $timestring_wordcount, $margin)
{
    // Find the largest font size that fits using measurements only (no image creation).
    $best_size = null;

    for ($size = $font_size; ; $size++) {
        $paragraphHeight = measureLayout($quote_array, $width, $size, $timestringStarts, $timestring_wordcount, $margin);
        if ($paragraphHeight === false || $paragraphHeight >= $height - 100) {
            break;
        }
        $best_size = $size;
    }

    if ($best_size === null) {
        return false;
    }

    return renderImage($quote_array, $width, $height, $best_size, $timestringStarts, $timestring_wordcount, $margin);
}

function measureSizeOfTextbox($font_size, $font_path, $text)
{
    $box = imagettfbbox($font_size, 0, $font_path, $text);

    $min_x = min($box[0], $box[2], $box[4], $box[6]);
    $max_x = max($box[0], $box[2], $box[4], $box[6]);
    $min_y = min($box[1], $box[3], $box[5], $box[7]);
    $max_y = max($box[1], $box[3], $box[5], $box[7]);

    $width  = ($max_x - $min_x);
    $height = ($max_y - $min_y);
    $left   = abs($min_x) + $width;
    $top    = abs($min_y) + $height;

    return array($width, $height, $left, $top);
}
