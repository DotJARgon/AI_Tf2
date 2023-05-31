import time
from screeninfo import get_monitors
import cv2
import numpy
from mss import mss
import os

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

# Specify frames rate. We can choose
# any value and experiment with it
fps = 60.0

fourcc = cv2.VideoWriter_fourcc(*'mp4v')

# Creating a VideoWriter object
out = cv2.VideoWriter(filename, fourcc, fps, resolution)

sct = mss()
t = time.time()
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

    # Stop recording when we press 'q'
    if cv2.waitKey(1) == ord('q'):
        break

# Release the Video writer
print("Saving Video...")
out.release()

# Destroy all windows
cv2.destroyAllWindows()