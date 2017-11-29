#!/bin/sh

echo "Restarting apache2 service"
sudo service apache2 restart

# kill running flask
pid=$(ps -ax | grep /bin/flask | grep -v "grep" | cut -d ' ' -f1)

if [ -n "$pid" ]; then
    echo "Killing $pid"
    kill $pid
fi

~/fradio/server/run &
