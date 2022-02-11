#!/bin/bash
# zip all folders into individual zip files
for i in */; do zip -r "${i%/}.zip" "$i"; done
