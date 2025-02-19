#!/bin/bash

# Activates python virtualenv
source /home/squintas/.pyenv/versions/nemo/bin/activate
#
# # Moves to client directory
# #cd /home/squintas/git_teddy/standalone/
#
# # The execution line was added on /etc/rc.local file to launch 
# # the teddy-client script in the background when the system is 
# # booted
#
# Launches Teddy-client python script
python /home/squintas/git_teddy/standalone/teddy_standalone.py 

