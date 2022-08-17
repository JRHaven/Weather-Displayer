#!/bin/bash

# This file is part of Weather-Displayer.

# Weather-Displayer is free software: you can redistribute it and/or modify 
# it under the terms of the GNU General Public License as published by the Free 
# Software Foundation, either version 3 of the License, or (at your option) any 
# later version.

# Weather-Displayer is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or 
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more 
# details.

# You should have received a copy of the GNU General Public License along with 
# Weather-Displayer. If not, see <https://www.gnu.org/licenses/>. 


if [[ $1 == "-q" ]]; then
    if [[ $(pgrep main.py) == "" ]]; then
        echo "The program isn't running! No need to quit!"
        exit
    fi

    echo "$(date): ----- QUIT COMMAND RECIEVED -----" >> log
    echo "Quitting..."
    echo "don" > passthru
    echo "$(date): ----- QUIT COMMAND SENT TO GETTER -----" >> log
    sleep 1
    echo "$(date): ----- TERMINATING MAIN -----" >> log
    echo "" > passthru
    killall main.py
    echo "...done"
    exit
fi

echo "" >> log
echo "$(date): ------ SESSION START ------" >> log
echo "" >> log

./getter.py &
./main.py