from time import sleep
from datetime import datetime
import pyvisa
import csv
import os
import argparse

fieldnames = [
    'Date of measurement', 
    'Volts DC', 
    'Volts AC', 
    'Volts Diode', 
    'Ampers DC', 
    'Ampers AC', 
    'Ohms 2-wire', 
    'Ohms 4-wire', 
    'Ohms continuity', 
    'Hz',
    'Farads'
]

#### LIST OF COMMANDS TO MEASURE ##### MORE COMMANDS : https://www.batronix.com/pdf/Rigol/ProgrammingGuide/DM3058_ProgrammingGuide_EN.pdf

measurement_commands = {
    'Volts DC': ':MEASure:VOLTage:DC?',
    'Volts AC': ':MEASure:VOLTage:AC?',
    'Volts Diode': ':MEASure:DIODe?',
    'Ampers DC': ':MEASure:CURRent:DC?',
    'Ampers AC': ':MEASure:CURRent:AC?',
    'Ohms 2-wire': ':MEASure:RESistance?',
    'Ohms 4-wire': ':MEASure:FRESistance?',
    'Ohms continuity': ':MEASure:CONTinuity?',
    'Hz': ':MEASure:FREQuency?',
    'Farads': ':MEASure:CAPacitance?'
}

csv_file = 'RIGOLDM3068Measure.csv'
csv_file2 = 'RIGOLDM3058EMeasure.csv'

def setup_file(filename):
    """Set up the CSV file for writing or appending."""
    write_headers = not os.path.exists(filename)
    file_mode = 'a' if os.path.exists(filename) else 'w'
    return open(filename, mode=file_mode, newline='', encoding='utf-8'), write_headers

def write_header_if_needed(writer, write_headers):
    """Write the CSV header if needed."""
    if write_headers:
        writer.writeheader()

def get_parameter_name(parameter_value):
    """Return the key (parameter name) from the command dictionary."""
    return next(key for key, value in measurement_commands.items() if value == parameter_value)

def create_data_row(date, instrument_name, key, value):
    """Create a data row with the measurement value or zero for other fields."""
    data_row = {'Instrument': instrument_name, 'Date of measurement': date}
    for field in fieldnames[1:]:
        data_row[field] = value if field == key else 0
    return data_row

def log_measurement(date, value1, value2):
    """Print the measurement data in a formatted way."""
    print(f"{date} | {value1} | {value2}")

def measure_and_write(writer1, writer2, instrument1, instrument2, param1, param2, key1, key2):
    """Perform the measurement, log, and write the results to CSV files."""
    now = datetime.now()
    date = now.strftime("%d/%m/%Y %H:%M:%S")
    
    raw1 = float(instrument1.query(param1))
    raw2 = float(instrument2.query(param2))
    
    data_row1 = create_data_row(date, 'Instrument 1', key1, raw1)
    data_row2 = create_data_row(date, 'Instrument 2', key2, raw2)
    
    writer1.writerow(data_row1)
    writer2.writerow(data_row2)
    
    log_measurement(date, raw1, raw2)

# Initialize instruments and files
def init_instruments_and_files():
    rm = pyvisa.ResourceManager()
    print(f'Connected VISA resources: {rm.list_resources()}')

    instrument1 = rm.open_resource('USB0::0x1AB1::0x0C94::DM3O183800786::INSTR')
    instrument2 = rm.open_resource('USB0::0x1AB1::0x0588::DM3R161650215::INSTR')

    print('Instrument 1 ID =', instrument1.query('*IDN?'))
    print('Instrument 2 ID =', instrument2.query('*IDN?'))

    file1, write_headers1 = setup_file(csv_file)
    writer1 = csv.DictWriter(file1, fieldnames=fieldnames)
    write_header_if_needed(writer1, write_headers1)

    file2, write_headers2 = setup_file(csv_file2)
    writer2 = csv.DictWriter(file2, fieldnames=fieldnames)
    write_header_if_needed(writer2, write_headers2)

    return instrument1, instrument2, writer1, writer2, file1, file2

# Main measurement functions
def measure_one_thing(instrument1, instrument2, writer1, writer2, param1, param2, key1, key2, samples=5):
    """Measure one parameter multiple times and log results."""
    print(f"                       DM3068     |    DM3058E ")
    print(f"  Date of Measure   |    {key1}     |     {key2}")
    print("----------------------------------------------------------------------------------")

    for _ in range(samples):
        measure_and_write(writer1, writer2, instrument1, instrument2, param1, param2, key1, key2)
        sleep(0.5)

def measure_all_at_once(instrument1, instrument2, writer1, writer2, samples=1):
    """Measure all parameters in sequence and log results."""
    print(f"                       DM3068     |    DM3058E ")
    print(f"  Date of Measure | {' | '.join(fieldnames[1:])}")
    print("----------------------------------------------------------------------------------")

    for _ in range(samples):
        for key, command in measurement_commands.items():
            measure_and_write(writer1, writer2, instrument1, instrument2, command, command, key, key)
            sleep(0.5)

def measure_till_stop(instrument1, instrument2, writer1, writer2, param1, param2, key1, key2):
    """Measure continuously until stopped by user."""
    print("Use Ctrl + C to stop the loop\n")
    print(f"                       DM3068     |    DM3058E ")
    print(f"  Date of Measure   |    {key1}     |     {key2}")
    print("----------------------------------------------------------------------------------")

    try:
        while True:
            measure_and_write(writer1, writer2, instrument1, instrument2, param1, param2, key1, key2)
            sleep(0.5)
    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Stopping the loop.\n")

# Setup and Execution with argparse for terminal options
if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Run measurement script.")
    parser.add_argument("mode", choices=["one", "all", "loop"], help="Choose mode to run: 'one' for one-thing, 'all' for all-at-once, or 'loop' to measure till stop.")
    args = parser.parse_args()

    instrument1, instrument2, writer1, writer2, file1, file2 = init_instruments_and_files()

    # Select parameters by changing indices
    param1 = list(measurement_commands.values())[7]  
    param2 = list(measurement_commands.values())[9]  
    key1 = get_parameter_name(param1)  # Get parameter name for DM3068
    key2 = get_parameter_name(param2)  # Get parameter name for DM3058E

    # Run based on user input from command-line
    if args.mode == "one":
        measure_one_thing(instrument1, instrument2, writer1, writer2, param1, param2, key1, key2)
    elif args.mode == "all":
        measure_all_at_once(instrument1, instrument2, writer1, writer2)
    elif args.mode == "loop":
        measure_till_stop(instrument1, instrument2, writer1, writer2, param1, param2, key1, key2)

    file1.close()
    file2.close()