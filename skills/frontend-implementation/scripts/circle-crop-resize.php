<?php
// Circle-crop (center square) + resize an image using Windows PHP GD.
// Usage: php.exe circle-crop-resize.php <src> <dst> <size>
// Windows PHP does NOT create missing dirs — mkdir the destination dir first.
$src = $argv[1] ?? null;
$dst = $argv[2] ?? null;
$size = (int) ($argv[3] ?? 512);
if (!$src || !$dst) { fwrite(STDERR, "usage: php circle-crop-resize.php <src> <dst> <size>\n"); exit(1); }

$img = imagecreatefromjpeg($src);
if (!$img) { fwrite(STDERR, "load failed: $src\n"); exit(1); }

$w = imagesx($img);
$h = imagesy($img);
$s = min($w, $h);
$sq = imagecrop($img, [
    'x' => (int) (($w - $s) / 2),
    'y' => (int) (($h - $s) / 2),
    'width' => $s,
    'height' => $s,
]);
if (!$sq) { fwrite(STDERR, "crop failed\n"); exit(1); }

$out = imagescale($sq, $size, $size);
if (!$out) { fwrite(STDERR, "scale failed\n"); exit(1); }

imagejpeg($out, $dst, 85);
echo "ok: {$w}x{$h} -> {$size}x{$size} -> {$dst}\n";
