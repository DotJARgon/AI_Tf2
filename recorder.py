import time
from screeninfo import get_monitors
import cv2
import numpy
from mss import mss
import os
from alive_progress import alive_bar

# Get the primary monitor
# Check if the screen is 1920x1080, if not, compensate
for monitor in get_monitors():
    if monitor.is_primary:
        bounding_box = {'top': 0, 'left': 0, 'width': abs(monitor.width), 'height': abs(monitor.height)}
    if monitor.width > 1920:
        bounding_box['width'] = 1920
        bounding_box['left'] = 0
    if monitor.height > 1080:
        bounding_box['height'] = 1080
        bounding_box['top'] = int((abs(monitor.height) - 1080) / 2)

# Sets the resolution of the output
scale = 0.5
# resolution = (int(1920*scale), int(1080*scale))
resolution = (480, 480)

# Specify name of Output file
file_count = 0
for path in os.listdir("Recordings"):
    file_count += 1
filename = "Recordings/rec_"+str(file_count+1)+".mp4"
print(filename)

# Count frames for fps fix
frames = 0

# Specify frames rate. We can choose
# any value and experiment with it
fps = 60.0

# Number of frames to collect before we calc real fps
cfps = 60

fourcc = cv2.VideoWriter_fourcc(*'mp4v')

# Creating a VideoWriter object
out = cv2.VideoWriter(filename, fourcc, fps, resolution)

sct = mss()
print("Checking Framerate...")

# Get start time of recording
start_time = time.time()
with alive_bar(cfps, bar='classic2', spinner=None) as bar:
    for i in range(cfps):
        sct_img = sct.grab(bounding_box)
        frame = numpy.array(sct_img)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2RGB)
        frame = cv2.resize(frame, resolution, interpolation=cv2.INTER_CUBIC)
        # Write it to the output file
        out.write(frame)
        frames += 1
        bar()
# Get end time / elapsed time
# Get true fps from this
end_time = time.time()
elapsed_time = end_time - start_time
real_fps = round(frames / elapsed_time)
print("Frames Gathered: " + str(frames))
print("FPS: " + str(real_fps))
# Creating a VideoWriter object with correct fps
out = cv2.VideoWriter(filename, fourcc, real_fps, resolution)

print("Recording...")
while True:
    sct_img = sct.grab(bounding_box)
    frame = numpy.array(sct_img)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2RGB)
    frame = cv2.resize(frame, resolution, interpolation=cv2.INTER_CUBIC)
    # Write it to the output file
    out.write(frame)

    # Optional: Display the recording screen
    cv2.imshow('Live', frame)
    frames += 1

    # Stop recording when we press 'q'
    if cv2.waitKey(1) == ord('q'):
        break

# Release the Video writer
print("Saving Video...")
end_time = time.time()
elapsed_time = end_time - start_time
print("Time Elapsed: " + str(round(elapsed_time)) + "s")
out.release()

# Destroy all windows
cv2.destroyAllWindows()