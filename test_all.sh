file_list=(
"./Broadcasting/testbroadcasting.py" 
"./Clocks/testlogicalclock.py" 
"./Election/testElectionEchoExtinction.py"  
"./Election/testElectionSpira.py"  
#"./General/test_mp_composition.py"
"./General/test.py"
"./General/test_undirectional_channels.py"
"./General/test_directional_channels.py"
"./General/testcomposition.py"
)

for py_file in "${file_list[@]}"
do
    echo  'Running' ${py_file}
    python3 ${py_file}
done