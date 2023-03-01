# Check mother board
# https://linuxconfig.net/manuals/howto/how-to-find-motherboard-model-in-linux.html
cat /sys/devices/virtual/dmi/id/board_{vendor,name,version}
