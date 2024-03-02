
    Server sent a very new message with ID 7340026765897351173, ignoring (see FAQ for details)


Use this command to fix the above error

     sudo date -s "$(wget -qSO- --max-redirect=0 google.com 2>&1 | grep Date: | cut -d' ' -f5-8)Z"