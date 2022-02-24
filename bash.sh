#!/bin/bash
# zip all folders into individual zip files
for i in */; do zip -r "${i%/}.zip" "$i"; done

# Download Google drive files
# https://medium.com/@acpanjan/download-google-drive-files-using-wget-3c2c025a8b99
# https://stackoverflow.com/questions/25010369/wget-curl-large-file-from-google-drive

# Replace strings in all files in a folder:
# https://linuxize.com/post/how-to-find-files-in-linux-using-the-command-line/
find . -type f -exec sed -i 's/\/work\/awilf/\/work\/qianlim\/mtag/g' {} +

# Remove cached items
du -sm ~/.cache/*
rm -rf ~/.cache/*
