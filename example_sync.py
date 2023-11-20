import matplotlib.pylab as plt
import imagesource
from flashvideosynchronization import FlashVideoSynchronization
from moviepy.editor import VideoFileClip,concatenate_videoclips,clips_array
import json

dest_dir = "1_3"
cameras = [1, 2] #the name of the cameras (please change the video inside directory with the number ex: 1.mp4, 2.mp4)
output_filename = "my_concatenation.mp4"
filenames = {cam: dest_dir+"/"+'%d.mp4' % cam for cam in cameras}
# print(filenames)
sources = {cam: imagesource.TimedVideoSource(filenames[cam]) for cam in cameras}

for source in sources.values():
    source.extract_timestamps()

sync = FlashVideoSynchronization()
sync.detect_flash_events(filenames)

# manually set rough offset by matching an event
sync.show_events()
matching_events = {1: 0, 2: 0}
offsets = {cam: sync.events[cam][matching_events[cam]]['frame_time'] for cam in cameras}
sync.show_events(offsets)  # now the events should appear aligned

# synchronize cameras: find parameters transformations that map camera time to reference camera time
sync.synchronize(cameras, offsets, base_cam=1)
json_str = sync.to_json()
json_val = json.loads(json_str)
clip1 = VideoFileClip(filenames[1])
clip2 = VideoFileClip(filenames[2])
shifted_clip2 = clip2.set_start(round(json_val['model']["2"]["shift"]/1000,2))
shifted_clip2 = shifted_clip2.resize(height=clip1.h)
final_clip = clips_array([[clip1, shifted_clip2]])
final_clip.write_videofile(output_filename)