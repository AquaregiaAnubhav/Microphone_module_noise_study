import serial
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import rfft, rfftfreq

# Configuration
PORT = 'COM6'  # Matches your ESP32's upload port
BAUD_RATE = 921600
SAMPLE_RATE = 48000
DURATION = 1  # Seconds of audio to capture per analysis frame
SAMPLES_PER_FRAME = SAMPLE_RATE * DURATION

print(f"Connecting to {PORT}...")
try:
    ser = serial.Serial(PORT, BAUD_RATE, timeout=2)
except serial.SerialException:
    print(f"Error: Could not open {PORT}. Ensure Arduino Serial Plotter is closed.")
    exit()

print(f"Recording {DURATION} second(s) of environmental noise...")
audio_data = []

# Flush any partial or garbage serial lines from the buffer
ser.reset_input_buffer()
for _ in range(10):
    ser.readline()

3
while len(audio_data) < SAMPLES_PER_FRAME:
    try:
        # Read a line, decode it, and strip the \r\n
        line = ser.readline().decode('utf-8').strip()
        if line:
            audio_data.append(int(line))
    except ValueError:
        pass  # Ignore any malformed text lines during transmission

ser.close()
print("Capture complete. Computing FFT...")

# Convert list to a high-speed numpy array
y = np.array(audio_data)

# Compute the Fast Fourier Transform
yf = rfft(y)
xf = rfftfreq(SAMPLES_PER_FRAME, 1 / SAMPLE_RATE)
magnitude = np.abs(yf)

# Build the spectral analysis plots
plt.figure(figsize=(12, 8))

# Top Graph: The raw audio waveform
plt.subplot(2, 1, 1)
plt.plot(np.linspace(0, DURATION, SAMPLES_PER_FRAME), y, color='blue')
plt.title('Time Domain (Raw Acoustic Amplitude)')
plt.xlabel('Time (seconds)')
plt.ylabel('Amplitude')
plt.grid(True, alpha=0.3)

# Bottom Graph: The Frequency Spectrum (Log-Log)
plt.subplot(2, 1, 2)
plt.plot(xf, magnitude, color='red')  # Changed to loglog
plt.title('Frequency Domain (FFT Spectral Analysis - Log/Log Scale)')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Magnitude (Loudness)')

# Start at 20Hz (log(0) is undefined) and go up to Nyquist limit (24kHz)
plt.xlim(0.1, 20)

# Enable gridlines for both major and minor log ticks
plt.grid(True, which="both", ls="-", alpha=0.3)

plt.tight_layout()
plt.show()