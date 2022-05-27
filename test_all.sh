file_list=("./Broadcasting/testbroadcasting.py" "./Clocks/testlogicalclock.py" "./Election/testElectionEchoExtinction.py"  "./Election/testElectionSpira.py" )

for py_file in "${file_list[@]}"
do
    echo  'Running' ${py_file}
    python3 ${py_file}
done