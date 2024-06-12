import serial

# Open serial port (COM4 in this example)
ser = serial.Serial('COM3', 195200)

while True:
    # Read a line from the serial port
    line = ser.readline().decode('utf-8').strip()

    # Split the line into components
    components = line.split(',')

    # Parse the Q and I values
    if len(components) == 2 and components[0].startswith('Q') and components[1].startswith('I'):
        Q = int(components[0][2:])
        I = int(components[1][2:])
        print(f'Q: {Q}, I: {I}')
