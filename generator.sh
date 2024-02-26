#!/bin/bash

int_to_hex() {
    local int=$1
    local hex=$(printf "%016x" "$int")
    eval "$2='$hex'"
}

sleep_wait=2
temp_min=-50
temp_max=2550
temp_value=-50
temp_average=800
temp_min_fluct=0
temp_max_fluct=50

climbing=1
refilling=0

load_min=0
load_max=800

fuel_min=0
fuel_max=3000
fuel_value=0
fuel_min_fluct=0
fuel_max_fluct=30



# at first, the tank is filled up randomly
fuel_value=$((fuel_max / 2 + $RANDOM % (fuel_max - fuel_max / 2 + 1)))

while true
    do
    sleep $sleep_wait
    
    #TEMP
    if [ "$climbing" -eq 1 ]; then
        temp=$(( temp_min_fluct + $RANDOM % (temp_max_fluct - temp_min_fluct + 1) )) # this is good
        ((temp_value+=temp))
        if [ "$temp_value" -gt "$temp_average" ]; then
            climbing=0
        fi
    else
        temp_value=$((temp_average + temp_min_fluct + $RANDOM % (temp_max_fluct - temp_min_fluct + 1))) # ASK do I need to go below the average? 
    fi
    
     # LOAD
    load_value=$((load_min + $RANDOM % (load_max - load_min + 1)))
    
    
     # FUEL
    if [ "$refilling" -eq 1 ]; then
        fuel_value=$((fuel_value + $RANDOM % (fuel_max - fuel_value + 1)))
        refilling=0
    else
        consumed=$((fuel_min_fluct + $RANDOM % (fuel_max_fluct - fuel_min_fluct + 1)))
        ((fuel_value-=consumed))
        if [ "$fuel_value" -lt 0 -o "$fuel_value" -eq 0 ]; then
            fuel_value=0
            refilling=1
        fi
    fi
    
    # load_value=$(awk -v min=$load_min -v max=$load_max 'BEGIN{srand(); printf "%.2f", min + rand() * (max - min)}')
    # fuel_value=$(awk -v min=$fuel_min -v max=$fuel_max 'BEGIN{srand(); printf "%.2f", min + rand() * (max - min)}')
    echo "$temp_value"
    echo "$load_value"
    echo "$fuel_value"
    
    temp_hex=""
    load_hex=""
    fuel_hex=""
    
    int_to_hex $temp_value temp_hex
    int_to_hex $load_value load_hex
    int_to_hex $fuel_value fuel_hex
    
    #check if the command accepts strings?
    #echo Temp: $temp_hex
    #echo Load: $load_hex
    #echo Fuel: $fuel_hex
    echo _________________
    
    #cansend can0 123#"$temp_hex" -z 7
    #cansend can0 124#"$load_hex"-z 7
    #cansend can0 125#"$fuel_hex" -z 7