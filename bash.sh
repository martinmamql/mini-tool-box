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

# alias
alias ssh-matrix='ssh qianlim@matrix.ml.cmu.edu'

# get time
a=$(date +%s)

grep -r . -e "Dev Acc: 0.68"

grep -rl "'corr': 0.7" --include='*.csv' . | xargs grep -l 'mosi_sentiment'

# Ignore lines with patterns
grep -v "pattern" myfile.txt > tmpfile

# Loop until some string is present in stdout
# https://superuser.com/questions/375223/watch-the-output-of-a-command-until-a-particular-string-is-observed-and-then-e
until my_cmd | grep -q "String Im Looking For"; do : ; done
# Loop until some string is no longer present (e.g., failed)
until my_cmd | grep -q -L "String Im Looking For"; do : ; done
# Specific example
until gcloud compute tpus tpu-vm create v3-1 --zone europe-west4-a --accelerator-type v3-8 --version tpu-vm-v4-base | grep -q -L "ERROR"; do : ; sleep 30s; done

# Download from Google drive using wget; replace FILEID and FILENAME
# https://chemicloud.com/kb/article/download-google-drive-files-using-wget/
# Small file (<= 100 Mb):
wget --no-check-certificate 'https://docs.google.com/uc?export=download&id=FILEID' -O FILENAME

# Large file (> 100 Mb):
wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=FILEID' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=FILEID" -O FILENAME && rm -rf /tmp/cookies.txt

# Find files matching multiple KEYWORD within all /home/$user folders
cut -d: -f1 /etc/passwd $1 | while read x; do grep -rns /home/$x /work/$x /results/$x /projects/dataset_processed/$x -e "MOSEAS_STATUS" -e "MOSEAS_MTURK" -e "MOSEAS" -e "Multiligual_MOSEI" -e "Multling_MOSEI" >> ~/MOSEAS_find_all_users.txt 2>&1; done

# Show available GPUs
sinfo -o "%40N  %20c  %10m  %35f  %20G %T" -p russ_reserved
