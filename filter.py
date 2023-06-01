import cv2
import numpy
from alive_progress import alive_bar
import sys

# Get terminal args
args = sys.argv

# Determines if each frame of the recording is shown to user
show_recording = False if len(sys.argv) == 2 else sys.argv[2]


# Finds the template image in the source image with cropping
def find_in_image(source, template, cropping):
    if cropping:
        left, right, top, bott = cropping
        source = source[left:right, top:bott]
    template = cv2.imread(template)
    width, height = template.shape[:-1]
    return (cv2.matchTemplate(source, template, cv2.TM_CCOEFF_NORMED), width, height)

# Applies a filter to the image
def filter_image(image):
    image[:,:,1] = numpy.zeros([image.shape[0], image.shape[1]])
    return image

# Grab the recording and name the output file
recording_fn = sys.argv[1]
output_fn = "Formatted_recordings/" + recording_fn + "_f.mp4"
recording = cv2.VideoCapture("Recordings/"+recording_fn + '.mp4')

# Choose which frame to start on
if len(sys.argv)>3 and sys.argv[3]:
    recording.set(cv2.CAP_PROP_POS_FRAMES, int(sys.argv[3])-1)

# Read first frame of recording and get # of frames and length
success, frame = recording.read()
fps = recording.get(cv2.CAP_PROP_FPS)
frame_count = int(recording.get(cv2.CAP_PROP_FRAME_COUNT))
recording_duration = round(frame_count / recording.get(cv2.CAP_PROP_FPS))

# Create the edited video
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
output = cv2.VideoWriter(output_fn, fourcc, fps, (480, 480))
output_frame_count = 0

with alive_bar(frame_count, bar='classic2', spinner=None) as bar:
    if len(sys.argv)>3 and sys.argv[3]:
        bar(int(sys.argv[3]))
    for f in range(frame_count):
        # Read next frame
        success, frame = recording.read()

        if success:
            # List all the images we will check fqor including bounding boxes for performance
            checks = [['A',(300,480,300,480)]]
            found = False
            for check in checks:
                # Find template in source
                result, w, h = find_in_image(frame, 'Templates/' + check[0] + ".png", check[1])
                location = numpy.where(result >= 0.5)
                # Put a box around that location
                # x, xx, y, yy = check[1]
                # start_point = (x, y)
                # end_point = (xx, yy)
                # cv2.rectangle(frame, start_point, end_point, (0, 255, 0), 2)
                if len(location[::-1][0]) > 0:
                    found = True
                    if check[0] == 'A':
                        frame = filter_image(frame)
                        output.write(frame)
                        output_frame_count += 1
                    for pt in zip(*location[::-1]):
                        x, y = pt
                        x += check[1][0]
                        y += check[1][2]
                        cv2.rectangle(frame, (x, y), (x + h, y + w), (255, 255, 255), 2)

            # Show the recorded frame after editing
            if show_recording:
                cv2.imshow('Recording', frame)

        # Update the progress bar
        bar()

        if cv2.waitKey(1) == ord('q') and show_recording:
            break

# Release the Video writer
print("Saving Video...\n")
output.release()
print('Frames In: ' + str(frame_count) + '\tFrames Out: ' + str(output_frame_count))
print('Duration In: ' + str(frame_count * 60) + '\tDuration Out: ' + str(output_frame_count * 60))
print('Compression: %' + str(100-(output_frame_count/frame_count)*100))
# Destroy all windows
cv2.destroyAllWindows()
