# RIGOLSMeasure
This script is for measuring various parameters using two RIGOL devices by USB. RIGOLDM3068 and RIGOLDM3058E at the moment. 
Script can be easily changed to use one device or more by just changing functions that initialize instruments and 
functions that measure parameters.

We have 3 main functions to use :

```
measure_all_at_once(instrument1, instrument2, writer1, writer2)
measure_one_thing(instrument1, instrument2, writer1, writer2, param1, param2, key1, key2)
measure_till_stop(instrument1, instrument2, writer1, writer2, param1, param2, key1, key2)
```

## measure_all_at_once
This one measures all parameters given in measurment_commands in given order that many times the user wants. 
If you want to change how many times the parameters will be measured you need to do it here :

```
def measure_all_at_once(instrument1, instrument2, writer1, writer2, samples=1):
```
at the end of brackets there is samples variable, here u change it. (samples=1 means that all parameters will be measured once)

## measure_one_thing
This one measures one chosen parameter as many times as user wants. 
Changing it is same as in function before; changing samples variable in function brackets.

## measure_till_stop
This function measures one selected parameter continuously until the user stops the process, for example, by using CTRL + C

## Changing what parameter to measure
You can choose which parameter to measure in both devices here :

```
param1 = list(measurement_commands.values())[7]  
param2 = list(measurement_commands.values())[9] 
```

param1 is for DM3068, and param2 is for DM3058E as for now. 
You can select different parameters to measure at once in both devices as given in example.

# Usage
To run the script u need to type in terminal :

```
python RIGOLSMeasurea.py {function}
```

in 'function' place you need to type either 'one' 'all' or 'loop' depending on what function you want to use

# Environment

In bash you need to type : 

```
./setup.sh
```

to setup environemt and install required dependencies