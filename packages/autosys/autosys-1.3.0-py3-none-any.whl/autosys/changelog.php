<?php

$NL = "\n";

function br($n=1)
{
    echo $NL * $n;
}
// The changelog path
$changelog_path = '../CHANGELOG.md';
$changelog_path = '/Users/skeptycal/Documents/coding/python/autosys/CHANGELOG.md';
echo $changelog_path;
br();
// Format the changelog from .md to HTML
$changelog = file_get_contents( $changelog_path );
echo $changelog;
// $changelog = preg_replace( "/###[ ]?([0-9\.]+): ([A-Z0-9 ,]+)/i", "<h3>$1</h3>" . PHP_EOL . "<i>$2</i>" . PHP_EOL . "<ul>", $changelog );
// $changelog = preg_replace( "/\* ([A-Z0-9 \._,'\(\)\/\-&\"\']+)/i", "<li>$1</li>", $changelog );
// $changelog = preg_replace( "/" . PHP_EOL . "<h3>/i", "</ul>" . PHP_EOL . PHP_EOL . "<h3>", $changelog );
// $changelog .= PHP_EOL . "</ul>";

// // Ouput. Copy and paste this to your website.
// echo '<textarea name="changelog" cols="100" rows="30">' . $changelog . '</textarea><br />';
