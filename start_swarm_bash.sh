#For start_sitl
#-----------------------

#!/usr/bin/env bash

args=$(getopt -l "drones:" -o "s:h" == "$@")

eval set -- "$args"

while true ; do
    case "$1" in
        -d|--drones)
            case "$2" in
                "") numDrones=3 ; shift 2;;
                *)numDrones=$2; shift 2;;
            esac ;;
        --) shift; break;;
    esac
done

for (( i=1; i<=$numDrones; i++))
do    
    xterm -hold -title "sim-$i" -e "dronekit-sitl copter --instance $i" &
done

for start_swarm
--------------------------

#!/usr/bin/env bash

args=$(getopt -l "slaves:" -o "s:h" == "$@")

eval set -- "$args"

while true ; do
    case "$1" in
        -s|--slaves)
            case "$2" in
                "") numDrones=3 ; shift 2;;
                *)numDrones=$2; shift 2;;
            esac ;;
        --) shift; break;;
    esac
done

xterm -hold -title "server" -e "python server.py" &
xterm -hold -title "master" -e "python master.py" &

for (( i=1; i<=$numDrones; i++))
do
    xterm -hold -title "slave $i" -e "python slave$i.py" &
done
