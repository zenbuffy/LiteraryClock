<?php

// this script turns quotes from books into images for use in a Kindle clock.
// Jaap Meijers, 2018

error_reporting(E_ALL);
ini_set('display_errors', 1);
ini_set('max_execution_time', 3000);

if (!is_dir('images/metadata') && !mkdir('images/metadata', 0777, true)) {
    throw new \RuntimeException(sprintf('Directory "%s" was not created', 'images/metadata'));
}

$imagenumber = 0;
$previoustime = 0;

// pad naar font file
putenv('GDFONTPATH=' . realpath('.'));

InitializeFonts();
setDevice($argv);

// get the quotes (including title and author) from a CSV file,
// and create unique images for them, one without and one with title and author
$row = 1;
if (($handle = fopen('litclock_annotated_improved.csv', 'r')) !== FALSE) {
    while (($data = fgetcsv($handle, 1000, '|')) !== FALSE) {
        $num = count($data);
        $row++;
        $time = $data[0];
        $timestring = trim($data[1]);
        $quote = $data[2];
        $quote = trim(preg_replace('/\s+/', ' ', $quote));
        $title = trim($data[3]);
        $author = trim($data[4]);

        TurnQuoteIntoImage($time, $quote, $timestring, $title, $author);

    }
    fclose($handle);
}

function setDevice($argv){
    global $deviceWidth;
    global $deviceHeight;

    //set default as Kindle size
    $deviceWidth = 600;
    $deviceHeight = 800;

    if(!empty($argv[1])){
        

        if(strtoupper($argv[1])=="PAPERWHITE"){
            $deviceWidth = 758;
            $deviceHeight = 1024;
        }
        elseif(strtoupper($argv[1])=="OASIS"){
            $deviceWidth = 1264;
            $deviceHeight = 1680;
        }
        elseif(strtoupper($argv[1])=="CUSTOM"){
            $deviceWidth = $argv[2];
            $deviceHeight = $argv[3];

        }
        else{
            //if we don't have a value for the device or a custom setting, default to kindle size
            $deviceWidth = 600;
            $deviceHeight = 800;
        }
    }
}

function InitializeFonts()
{
    global $font_path;
    global $font_path_bold;
    global $creditFont;

    $tff_font_path = 'LinLibertine_RZ.ttf';
    $tff_font_path_bold = 'LinLibertine_RB.ttf';
    $tff_creditFont = 'LinLibertine_RZI.ttf';

    // Depending on how fonts are installed, this may be what you want instead:
    $otf_font_path = 'LinLibertine_RZ.otf';
    $otf_font_path_bold = 'LinLibertine_RB.otf';
    $otf_creditFont = 'LinLibertine_RZI.otf';

    $font_error = false;

    if (file_exists($tff_font_path)) {
        $font_path = $tff_font_path;
    } elseif (file_exists($otf_font_path)) {
        $font_path = $otf_font_path;
    } else {
        print "ERROR: Unable to find font file: " . $tff_font_path . " or " . $otf_font_path;
        $font_error = true;
    }

    if (file_exists($tff_font_path_bold)) {
        $font_path_bold = $tff_font_path_bold;
    } elseif (file_exists($otf_font_path_bold)) {
        $font_path_bold = $otf_font_path_bold;
    } else {
        print "ERROR: Unable to find font file: " . $tff_font_path_bold . " or " . $otf_font_path_bold;
        $font_error = true;
    }


    if (file_exists($tff_creditFont)) {
        $creditFont = $tff_creditFont;
    } elseif (file_exists($otf_creditFont)) {
        $creditFont = $otf_creditFont;
    } else {
        print "ERROR: Unable to find font file: " . $tff_creditFont . " or " . $otf_creditFont . PHP_EOL;
        $font_error = true;
    }

    if ($font_error) {
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
    //image dimensions
    $width = $deviceWidth;
    $height = $deviceHeight;

    //text margin
    $margin = 26;

    // first, find the timestring to be highlighted in the quote
    // determine the position of the timestring in the quote (so after how many words it appears)
    $timestringStarts = count(explode(' ', stristr($quote, $timestring, true))) - 1;
    // how many words long the timestring is
    $timestring_wordcount = count(explode(' ', $timestring)) - 1;

    // divide text in an array of words, based on spaces
    $quote_array = explode(' ', $quote);

    $time = substr($time, 0, 2) . substr($time, 3, 2);


    // font size to start with looking for a fit. a long quote of 125 words or 700 characters gives us a font size of 23, so 18 is a safe start.
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

    // Does the image already exist? No point in creating it again.
    $checkpath = realpath('images/quote_' . $time . '_' . $imagenumber . '.png');

    if (!file_exists($checkpath)) {
        printf('Making a new image for ' . $time . PHP_EOL);
        if (PHP_SAPI !== 'cli') echo '<br />';
        ///// QUOTE /////
        // find the font size (recursively) for an optimal fit of the text in the bounding box
        // and create the image.
        list($png_image) = fitText($quote_array, $width, $height, $font_size, $timestringStarts, $timestring_wordcount, $margin);


        print 'Image for ' . $time . '_' . $imagenumber . PHP_EOL;
        if (PHP_SAPI !== 'cli') echo '<br /><br />';


        // Save the image
        imagepng($png_image, 'images/quote_' . $time . '_' . $imagenumber . '.png');


        ///// METADATA /////
        // create another version, with title and author in the image

        // define text color
        $grey = imagecolorallocate($png_image, 125, 125, 125);
        $black = imagecolorallocate($png_image, 0, 0, 0);

        $dash = '—';

        $credits = $title . ', ' . $author;
        $creditFont_size = 18;

        // if the metadata are longer than 45 characters, replace a space by a newline from the end,
        // just as long the paragraph is getting smaller. stop when the box gets wider again.
        list($metawidth, $metaheight, $metaleft, $metatop) = measureSizeOfTextbox($creditFont_size, $creditFont, $dash . $credits);

        if ($metawidth > 500) {

            $newCredits = array();

            $creditsArray = explode(' ', $credits);

            $i = 1;

            while (True) {

                // cut the metadata in two lines
                $tmp0 = implode(' ', array_slice($creditsArray, 0, count($creditsArray) - $i));
                $tmp1 = implode(' ', array_slice($creditsArray, 0 - $i));

                // once the second line is (almost) longer than the first line, stop
                if (strlen($tmp1) + 5 > strlen($tmp0)) {
                    break;
                } else {
                    // if the second line is still shorter than the first, save it to a new string, but continue to look at a new fit.
                    $newCredits[0] = $tmp0;
                    $newCredits[1] = $tmp1;
                }

                $i++;

            }

            list($textWidth1, $textheight1) = measureSizeOfTextbox($creditFont_size, $creditFont, $dash . $newCredits[0]);
            list($textWidth2, $textheight2) = measureSizeOfTextbox($creditFont_size, $creditFont, $newCredits[1]);

            $metadataX1 = $width - ($textWidth1 + $margin);
            $metadataX2 = $width - ($textWidth2 + $margin);
            $metadataY = $height - $margin;

            imagettftext($png_image, $creditFont_size, 0, $metadataX1, $metadataY - (int) ($textheight1 * 1.1), $black, $creditFont, $dash . $newCredits[0]);
            imagettftext($png_image, $creditFont_size, 0, $metadataX2, $metadataY, $black, $creditFont, $newCredits[1]);

        } else {

            // position of single line metadata
            $metadataX = ($width - $metaleft) - $margin;
            $metadataY = $height - $margin;

            imagettftext($png_image, $creditFont_size, 0, $metadataX, $metadataY, $black, $creditFont, $dash . $credits);

        }

        // Save the image with metadata
        imagepng($png_image, 'images/metadata/quote_' . $time . '_' . $imagenumber . '_credits.png');

        // Free up memory
        imagedestroy($png_image);

        // convert the image we made to greyscale
        $im = new Imagick();
        $im->readImage('images/quote_' . $time . '_' . $imagenumber . '.png');
        $im->setImageType(Imagick::IMGTYPE_GRAYSCALE);
        unlink('images/quote_' . $time . '_' . $imagenumber . '.png');
        $im->writeImage('images/quote_' . $time . '_' . $imagenumber . '.png');

        // convert the image we made to greyscale
        $im = new Imagick();
        $im->readImage('images/metadata/quote_' . $time . '_' . $imagenumber . '_credits.png');
        $im->setImageType(Imagick::IMGTYPE_GRAYSCALE);
        unlink('images/metadata/quote_' . $time . '_' . $imagenumber . '_credits.png');
        $im->writeImage('images/metadata/quote_' . $time . '_' . $imagenumber . '_credits.png');

    }

}


function fitText($quote_array, $width, $height, $font_size, $timestringStarts, $timestring_wordcount, $margin)
{

    global $font_path_bold;
    global $font_path;

    // create image
    $png_image = imagecreate($width, $height)
    or die('Cannot Initialize new GD image stream');
    $background_color = imagecolorallocate($png_image, 255, 255, 255);

    // define text color
    $grey = imagecolorallocate($png_image, 125, 125, 125);
    $black = imagecolorallocate($png_image, 0, 0, 0);

    $timeLocation = 0;
    $lineWidth = 0;

    // variable to hold the x and y position of words
    $position = array($margin, $margin + $font_size);

    // echo 'try ' . $font_size . ', ';

    foreach ($quote_array as $key => $word) {

        # change the look of the text if it is part of the time string
        if (in_array($key, range($timestringStarts, $timestringStarts + $timestring_wordcount))) {
            $font = $font_path_bold;
            $textcolor = $black;
        } else {
            $font = $font_path;
            $textcolor = $grey;
        }

        // measure the word's width
        list($textwidth, $textheight) = measureSizeOfTextbox($font_size, $font, $word . ' ');

        //// write every word to image, and record its position for the next word ////

        // if one word exceeds the width of the image (this sometimes happens when the quote is very short),
        // then stop trying to make the font size even bigger.
        if ($textwidth > ($width - $margin)) {
            return False;
        }

        // if the line plus the extra word is too wide for the specified width, then write the word one the next line.
        if (($position[0] + $textwidth) >= ($width - $margin)) {

            # 'carriage return':
            # reset x to the beginning of the line and push y down a line
            $position[0] = $margin;
            $position[1] = $position[1] + (int) ($font_size * 1.618); // 'golden ratio' line height

            # write the word to the image
            imagettftext($png_image, $font_size, 0, $position[0], $position[1], $textcolor, $font, $word);

            // if the line isn't too long, just add it.
        } else {

            # write the word to the image
            imagettftext($png_image, $font_size, 0, $position[0], $position[1], $textcolor, $font, $word);

        }

        # add the word's width
        $position[0] += $textwidth;

    }

    // if the height of the whole text is smaller than the height of the image, then call this same function again
    $paragraphHeight = $position[1];
    if ($paragraphHeight < $height - 100) { // leaving room for the credits below
        $result = fitText($quote_array, $width, $height, $font_size + 1, $timestringStarts, $timestring_wordcount, $margin);
        if ($result !== False) {
            list($png_image, $paragraphHeight, $font_size, $timeLocation) = $result;
        };
    } else {
        // if this call to fitText returned a paragraph that is in fact higher than the height of the image,
        // then return without those values
        return False;
    }

    return array($png_image, $paragraphHeight, $font_size, $timeLocation);

}

function measureSizeOfTextbox($font_size, $font_path, $text)
{

    $box = imagettfbbox($font_size, 0, $font_path, $text);

    $min_x = min(array($box[0], $box[2], $box[4], $box[6]));
    $max_x = max(array($box[0], $box[2], $box[4], $box[6]));
    $min_y = min(array($box[1], $box[3], $box[5], $box[7]));
    $max_y = max(array($box[1], $box[3], $box[5], $box[7]));

    $width = ($max_x - $min_x);
    $height = ($max_y - $min_y);
    $left = abs($min_x) + $width;
    $top = abs($min_y) + $height;

    return array($width, $height, $left, $top);

}
