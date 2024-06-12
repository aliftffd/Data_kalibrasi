import serial
import csv
import json
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
import numpy as np

class RadarGraph:
    def __init__(self, root):
        self.root = root
        self.root.title('Real-time I and Q Graph')

        # Create the figure and axis for the graph
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(12, 6))
        self.ax1.set_xlabel('Index')
        self.ax1.set_ylabel('I and Q Values')
        self.ax1.set_title('Real-time I and Q Graph')
        self.ax2.set_xlabel('Frequency')
        self.ax2.set_ylabel('Amplitude')
        self.ax2.set_title('Average FFT I/Q')

        # Create the canvas for the graph
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Create the start button
        self.start_button = tk.Button(self.root, text='Start', command=self.start_reading)
        self.start_button.pack(side=tk.BOTTOM)

        # Create the reset button
        self.reset_button = tk.Button(self.root, text='Reset', command=self.reset_graph)
        self.reset_button.pack(side=tk.BOTTOM)

        # Buffers for I and Q components
        self.I_buffer = []
        self.Q_buffer = []
        self.index = 0

        # Serial port settings
        self.serial_port = 'COM3'  # Replace with your serial port
        self.baud_rate = 115200      # Replace with your baud rate
        self.duration_seconds = 60  # Read data for 5 seconds

    def start_reading(self):
        # Disable the start button
        self.start_button.config(state='disabled')

        # Open the serial port
        self.ser = serial.Serial(self.serial_port, self.baud_rate, timeout=1)

        # Record the start time
        self.start_time = time.time()

        # Loop to read data for the specified duration
        while time.time() - self.start_time < self.duration_seconds:
            # Read a line from the serial port
            line = self.ser.readline().decode('utf-8').strip()

            if line:
                try:
                    # Parse the JSON data
                    data = json.loads(line)
                    if isinstance(data, dict):
                        if "I" in data:
                            self.I_buffer = data["I"]
                        if "Q" in data:
                            self.Q_buffer = data["Q"]

                    # Check if both buffers have data
                    if self.I_buffer and self.Q_buffer:
                        if len(self.I_buffer) == len(self.Q_buffer):
                            # Update the graph
                            self.ax1.clear()
                            self.ax1.plot(range(self.index, self.index + len(self.I_buffer)), self.I_buffer, label='I (In-phase)')
                            self.ax1.plot(range(self.index, self.index + len(self.Q_buffer)), self.Q_buffer, label='Q (Quadrature)')
                            self.ax1.legend()

                            # Compute the complex signal
                            s = np.array(self.I_buffer) + 1j * np.array(self.Q_buffer)

                            # Remove the mean to center the data
                            s = s - np.mean(s)

                            # Number of samples per chirp (you need to provide this value or calculate it)
                            num_chirps = 10  # Adjust this value as needed
                            num_samples_per_chirp = len(s) // num_chirps

                            # Reshape the complex signal into a 2D array
                            s = s[:num_chirps * num_samples_per_chirp]  # Ensure s can be reshaped correctly
                            s = s.reshape((num_chirps, num_samples_per_chirp))

                            # Apply a window function (e.g., Hanning window) to reduce spectral leakage
                            window = np.hanning(num_samples_per_chirp)
                            s_windowed = s * window

                            # Apply the FFT along the columns (for each chirp)
                            range_spectrum = np.fft.fft(s_windowed, axis=1)

                            # Plot the average FFT I/Q
                            freq = np.fft.fftshift(np.fft.fftfreq(num_samples_per_chirp))
                            avg_fft_IQ = np.fft.fftshift(np.abs(np.mean(range_spectrum, axis=0)))
                            self.ax2.clear()
                            self.ax2.plot(freq, avg_fft_IQ)
                            self.ax2.set_title('Average FFT I/Q')

                            self.canvas.draw()

                            print(f"Updated graph with {len(self.I_buffer)} pairs of I and Q values.")

                            # Increment the index
                            self.index += len(self.I_buffer)

                            #Clear the buffers after updating the graph
                            self.I_buffer.clear()
                            self.Q_buffer.clear()
                        else:
                            print(f"Mismatched lengths: I={len(self.I_buffer)}, Q={len(self.Q_buffer)}")
                except json.JSONDecodeError:
                    print(f"Invalid JSON data: {line}")
                except TypeError as e:
                    print(f"TypeError: {e} - Data: {line}")

            # Update the GUI
            self.root.update_idletasks()
            self.root.update()

            time.sleep(0.01)  # Sleep for a short time to avoid busy-waiting

        # Close the serial port
        self.ser.close()
        print(f"Data logging stopped after {self.duration_seconds} seconds.")

        # Enable the start button
        self.start_button.config(state='normal')

    def reset_graph(self):
        # Clear the graph
        self.ax1.clear()
        self.ax1.set_xlabel('Index')
        self.ax1.set_ylabel('I and Q Values')
        self.ax1.set_title('Real-time I and Q Graph')
        self.ax2.clear()
        self.ax2.set_xlabel('Frequency')
        self.ax2.set_ylabel('Amplitude')
        self.ax2.set_title('Average FFT I/Q')
        self.canvas.draw()

        # Reset the buffers and index
        self.I_buffer.clear()
        self.Q_buffer.clear()
        self.index = 0

        print("Graph reset.")

# Create the GUI window
root = tk.Tk()
radar_graph = RadarGraph(root)
root.mainloop()