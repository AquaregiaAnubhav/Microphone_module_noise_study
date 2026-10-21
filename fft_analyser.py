import serial
import numpy as np
from scipy.fft import rfft, rfftfreq
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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

# Capture the exact number of samples needed
while len(audio_data) < SAMPLES_PER_FRAME:
    try:
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

# Filter out 0 Hz for log plot to avoid math domain errors
valid_idx = xf > 0
xf_clean = xf[valid_idx]
magnitude_clean = magnitude[valid_idx]

# Build the interactive Plotly subplots
fig = make_subplots(
    rows=2, cols=1,
    subplot_titles=("Time Domain (Raw Acoustic Amplitude)",
                    "Frequency Domain (FFT Spectral Analysis - Log/Log Scale)"),
    vertical_spacing=0.15
)

# Top Graph: The raw audio waveform
time_x = np.linspace(0, DURATION, SAMPLES_PER_FRAME)
fig.add_trace(
    go.Scatter(x=time_x, y=y, mode='lines', line=dict(color='blue'), name="Amplitude"),
    row=1, col=1
)
fig.update_xaxes(title_text="Time (seconds)", row=1, col=1)
fig.update_yaxes(title_text="Amplitude", row=1, col=1)

# Bottom Graph: The Frequency Spectrum (Log-Log)
fig.add_trace(
    go.Scatter(x=xf_clean, y=magnitude_clean, mode='lines', line=dict(color='red'), name="Magnitude"),
    row=2, col=1
)

fig.update_xaxes(
    type="linear",
    title_text="Frequency (Hz)",
    range=[1, 1000],
    row=2, col=1
)
fig.update_yaxes(
    type="linear",
    title_text="Magnitude (Loudness)",
    row=2, col=1
)

# Final layout adjustments
fig.update_layout(
    height=800,
    title_text="Interactive Acoustic Analysis",
    showlegend=False,
    hovermode="x unified"
)

# Opens the interactive graph in your default web browser
fig.show()