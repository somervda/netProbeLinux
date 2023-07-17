#!/bin/bash

# make and/or copy configui.json file

# Make an empty hosts file is one doesn't exist
if [ ! -f /data/hosts.json ]
then
    echo '[]' > /data/hosts.json
    echo "Empty /data/hosts.json file created."
fi

# Make an logger folder is one doesn't exist
if [ ! -d /data/logger ]
then
    mkdir /data/logger
    echo "New /data/logger directory created."
fi

# Start the scheduler process
python scheduler.py  > /dev/null &
scheduler_pid=$!
# Start the webServices process
python webServices.py > /dev/null &
webServices_pid=$!
echo "****"
echo "scheduler_pid: $scheduler_pid   webServices_pid: $webServices_pid "

# Clean up netProbe if either process stops 
while true
do
    if ! ps -p $scheduler_pid > /dev/null
    then
        echo "scheduler not running , killing webServices."
        kill -9 $webServices_pid
        break
    fi
    if ! ps -p $webServices_pid > /dev/null
    then
        echo "webServices not running , killing scheduler."
        kill -9 $scheduler_pid
        break
    fi
    echo "Sleeping..."
    sleep 15
done

echo "** netprobe_runner exiting **"
echo ""
