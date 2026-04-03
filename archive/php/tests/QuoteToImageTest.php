<?php

use PHPUnit\Framework\TestCase;

require_once __DIR__ . '/../quote_to_image.php';

class QuoteToImageTest extends TestCase
{
    // -------------------------------------------------------------------------
    // resolveFont
    // -------------------------------------------------------------------------

    public function testResolveFontReturnsTtfWhenPresent(): void
    {
        $ttf = tempnam(sys_get_temp_dir(), 'font') . '.ttf';
        $otf = tempnam(sys_get_temp_dir(), 'font') . '.otf';
        touch($ttf);

        $result = resolveFont($ttf, $otf);

        $this->assertSame($ttf, $result);

        unlink($ttf);
    }

    public function testResolveFontFallsBackToOtf(): void
    {
        $ttf = sys_get_temp_dir() . '/nonexistent.ttf';
        $otf = tempnam(sys_get_temp_dir(), 'font') . '.otf';
        touch($otf);

        $result = resolveFont($ttf, $otf);

        $this->assertSame($otf, $result);

        unlink($otf);
    }

    public function testResolveFontReturnsNullWhenNeither(): void
    {
        $this->expectOutputRegex('/ERROR/');

        $result = resolveFont('/nonexistent.ttf', '/nonexistent.otf');

        $this->assertNull($result);
    }

    // -------------------------------------------------------------------------
    // setDevice
    // -------------------------------------------------------------------------

    public function testSetDeviceDefaultsToKindleSize(): void
    {
        setDevice([]);
        $this->assertSame(600, $GLOBALS['deviceWidth']);
        $this->assertSame(800, $GLOBALS['deviceHeight']);
    }

    public function testSetDevicePaperwhite(): void
    {
        setDevice(['script', 'paperwhite']);
        $this->assertSame(758, $GLOBALS['deviceWidth']);
        $this->assertSame(1024, $GLOBALS['deviceHeight']);
    }

    public function testSetDeviceOasis(): void
    {
        setDevice(['script', 'oasis']);
        $this->assertSame(1264, $GLOBALS['deviceWidth']);
        $this->assertSame(1680, $GLOBALS['deviceHeight']);
    }

    public function testSetDeviceCustom(): void
    {
        setDevice(['script', 'custom', 1024, 1366]);
        $this->assertSame(1024, $GLOBALS['deviceWidth']);
        $this->assertSame(1366, $GLOBALS['deviceHeight']);
    }

    public function testSetDeviceUnknownFallsBackToDefault(): void
    {
        setDevice(['script', 'unknown_device']);
        $this->assertSame(600, $GLOBALS['deviceWidth']);
        $this->assertSame(800, $GLOBALS['deviceHeight']);
    }

    public function testSetDeviceCaseInsensitive(): void
    {
        setDevice(['script', 'PaperWhite']);
        $this->assertSame(758, $GLOBALS['deviceWidth']);
        $this->assertSame(1024, $GLOBALS['deviceHeight']);
    }

    // -------------------------------------------------------------------------
    // Pi e-ink presets
    // -------------------------------------------------------------------------

    public function testSetDeviceInkyPhat(): void
    {
        setDevice(['script', 'inkyphat']);
        $this->assertSame(104, $GLOBALS['deviceWidth']);
        $this->assertSame(212, $GLOBALS['deviceHeight']);
    }

    public function testSetDeviceInkyPhatLandscape(): void
    {
        setDevice(['script', 'inkyphat_l']);
        $this->assertSame(212, $GLOBALS['deviceWidth']);
        $this->assertSame(104, $GLOBALS['deviceHeight']);
    }

    public function testSetDeviceInkyWHat(): void
    {
        setDevice(['script', 'inkywhat']);
        $this->assertSame(300, $GLOBALS['deviceWidth']);
        $this->assertSame(400, $GLOBALS['deviceHeight']);
    }

    public function testSetDeviceInkyWHatLandscape(): void
    {
        setDevice(['script', 'inkywhat_l']);
        $this->assertSame(400, $GLOBALS['deviceWidth']);
        $this->assertSame(300, $GLOBALS['deviceHeight']);
    }

    public function testSetDeviceInkyImpression(): void
    {
        setDevice(['script', 'inkyimpression']);
        $this->assertSame(448, $GLOBALS['deviceWidth']);
        $this->assertSame(600, $GLOBALS['deviceHeight']);
    }

    public function testSetDeviceInkyImpressionLandscape(): void
    {
        setDevice(['script', 'inkyimpression_l']);
        $this->assertSame(600, $GLOBALS['deviceWidth']);
        $this->assertSame(448, $GLOBALS['deviceHeight']);
    }

    public function testSetDeviceWaveshare75(): void
    {
        setDevice(['script', 'waveshare75']);
        $this->assertSame(480, $GLOBALS['deviceWidth']);
        $this->assertSame(800, $GLOBALS['deviceHeight']);
    }

    public function testSetDeviceWaveshare75Landscape(): void
    {
        setDevice(['script', 'waveshare75_l']);
        $this->assertSame(800, $GLOBALS['deviceWidth']);
        $this->assertSame(480, $GLOBALS['deviceHeight']);
    }

    public function testSetDeviceIT8951(): void
    {
        setDevice(['script', 'it8951']);
        $this->assertSame(1404, $GLOBALS['deviceWidth']);
        $this->assertSame(1872, $GLOBALS['deviceHeight']);
    }

    public function testSetDeviceIT8951Landscape(): void
    {
        setDevice(['script', 'it8951_l']);
        $this->assertSame(1872, $GLOBALS['deviceWidth']);
        $this->assertSame(1404, $GLOBALS['deviceHeight']);
    }

    // -------------------------------------------------------------------------
    // Smoke test — skipped locally if GD or Imagick are unavailable
    // -------------------------------------------------------------------------

    public function testGeneratesImagesForSmallYaml(): void
    {
        if (!extension_loaded('gd')) {
            $this->markTestSkipped('GD extension not available');
        }
        if (!extension_loaded('imagick')) {
            $this->markTestSkipped('Imagick extension not available');
        }

        $workdir = sys_get_temp_dir() . '/litclock_test_' . uniqid();
        mkdir($workdir . '/images/metadata', 0777, true);

        // symlink fonts from the real project directory
        $projectDir = dirname(__DIR__);
        foreach (glob($projectDir . '/*.{ttf,otf}', GLOB_BRACE) as $font) {
            symlink($font, $workdir . '/' . basename($font));
        }

        $yaml = <<<YAML
- author: Herman Melville
  quote: It was the hour of noon, and the sea was calm.
  source: Moby-Dick
  time: '12:00'
  time_name: noon
- author: Jane Austen
  quote: It was half-past twelve, and she had not yet appeared.
  source: Pride and Prejudice
  time: '12:30'
  time_name: half past twelve
YAML;
        file_put_contents($workdir . '/litclock.yaml', $yaml);

        $cmd = sprintf(
            'cd %s && php %s/quote_to_image.php 2>&1',
            escapeshellarg($workdir),
            escapeshellarg($projectDir)
        );
        exec($cmd, $output, $exitCode);

        $this->assertSame(0, $exitCode, implode("\n", $output));

        $this->assertFileExists($workdir . '/images/quote_1200_0.png');
        $this->assertFileExists($workdir . '/images/metadata/quote_1200_0_credits.png');
        $this->assertGreaterThan(0, filesize($workdir . '/images/quote_1200_0.png'));

        $this->assertFileExists($workdir . '/images/quote_1230_0.png');
        $this->assertFileExists($workdir . '/images/metadata/quote_1230_0_credits.png');
    }
}
