import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import serial

# Set up the serial connection
ser = serial.Serial('COM3', 9600)  # Replace with your serial port and baudrate

# Create the Tkinter window
root = tk.Tk()
root.title("Real-time FFT Plot")

# Create the Matplotlib figure and axis
fig, ax = plt.subplots()
ax.set_xlabel("Frequency")
ax.set_ylabel("Amplitude")
ax.set_title("Real-time FFT Plot")

# Create the canvas to display the plot
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

def read_serial():
    line = ser.readline().decode().strip()
    if line.startswith("FFT:"):
        fft_data = line[5:-1].split(",")
        data = {"FFT": [int(x) for x in fft_data]}
        return data
    else:
        return None

def update_plot():
    data = read_serial()
    if data is not None:
        x_data = range(len(data["FFT"]))  # Assuming the length of the FFT data is the number of frequencies
        y_data = data["FFT"]
        ax.clear()
        ax.set_xlabel("Frequency")
        ax.set_ylabel("Amplitude")
        ax.set_title("Real-time FFT Plot")
        ax.plot(x_data, y_data)
        canvas.draw()
    root.after(100, update_plot)

# Start the plot update loop
update_plot()

# Run the Tkinter event loop
root.mainloop()