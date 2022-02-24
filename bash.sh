#!/bin/bash
# zip all folders into individual zip files
for i in */; do zip -r "${i%/}.zip" "$i"; done

# Download Google drive files
# https://medium.com/@acpanjan/download-google-drive-files-using-wget-3c2c025a8b99
# https://stackoverflow.com/questions/25010369/wget-curl-large-file-from-google-drive
