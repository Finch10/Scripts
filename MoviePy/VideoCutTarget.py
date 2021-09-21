'''This script adds the desired video inside another one at certain timestamps.'''

import request 
import datetime 
import os 
from os.path import join
from moviepy.editor import *


class Mixing():
  def __init__(self, author_path, my_video_path,saving_path,partition, start=0, end=0,
                mirror=False):
    '''
      The Lyrics constructor
        :param my_video_path: str
          My video path
        :param author_video: str
          Author's folder path with video
        :saving_path: str
          Path where final videos will be saved
        :partition: str
          string with timer mark's in video
        :param start: int
          The number where to start video
        :param end: int
          The number where video ends
        :mirror: boolean
          Flag if there is necesary mirror video
    '''

    #Setting up the parameters.
    self._folder_author_path = author_path
    self._folder_saving_path = saving_path
    self.my_video_path =  my_video_path
    self.start = start
    self.end = end
    self.partition = self.get_time_marks(partition)
    self.mirror = mirror
    self._filesdir = os.listdir(self._folder_author_path)
    self.count = 1

  def get_time_marks(self, lista):

    times = re.findall(r'^(?:(\d\d):)?(\d\d):(\d\d(?:\.\d*)?)', lista, re.M)
    # convert to integers and floats [(0, 0, 0.0), (0, 1, 26.0), ...]
    times = [(int(h or 0), int(m), float(s or 0)) for h, m, s in times]
    # convert to timedeltas [timedelta(0), timedelta(0, 86), ...]
    times = [datetime.timedelta(hours=h, minutes=m, seconds=s) for h, m, s in times]
    times =[str(i) for i in times]
    times = [self._transform_seconds(i) for i in times]
    return times

  def _transform_seconds(self,marker):
    date_time = datetime.datetime.strptime(marker, "%H:%M:%S")
    a_timedelta = date_time - datetime.datetime(1900, 1, 1)
    seconds = a_timedelta.total_seconds()
    return seconds



  def _get_final_video(self, video):
    stocked = []

    # Get metadata from initial video
    durata = video.duration - self.end - 1
    w = video.w
    h = video.h
    fps = video.fps

    # Initialize and apply caracteristics to my video
    my_video = VideoFileClip(self.my_video_path)
    my_video = video.resize(
        height = h, width = w
    ).set_fps(fps)
     # Mirroring video if it is required
    if self.mirror == True:
      video = video.fx(vfx.mirror_x)


    # Giving value where video should start    
    back = self.start
    for i in self.partition:
      # Get fragment of video
      clip = video.subclip(back, i)
      # Append list with this fragment
      stocked.append(clip)
      # Append list with my video
      stocked.append(my_video)
      back = i
    clip = video.subclip(self.partition[-1], durata)
    stocked.append(clip)
    final_video = concatenate_videoclips(stocked, method='compose')
    return final_video




  def work(self):
    if os.path.isdir(self._folder_saving_path) == False:
        os.mkdir(self._folder_saving_path) 
       
    #Iterating all videos in author's folder
    for video in self._filesdir:
        self._execution(video)


  def _execution(self, video):
    # Get path to the video
    path = join(self._folder_author_path, video)

    # Initialize video with moviepy
    proto_video = VideoFileClip(path)
    # Get processed video
    final_video =self._get_final_video(proto_video)
    # Create saving path
    saving_path = join(self._folder_saving_path, video)
    # Save video
    final_video.write_videofile(saving_path[:-3] + 'mp4')
    # Delete old video
    os.remove(path)



  def work_audio(self, path_to_audio):
    #Iterating all videos in author's folder
    for video in self._filesdir:
      # Get path to the video
      path_v = join(self._folder_author_path, video)
      # Get path to the audio
      path_a = join(path_to_audio, video[:-3] + 'mp3')
      # Get processed video
      proto_video = VideoFileClip(path_v)
      # Get processed audio
      proto_audio = AudioFileClip(path_a).subclip(0, proto_video.duration-1)
      # Set audio to video
      proto_video = proto_video.set_audio(proto_audio)
      # Get processed video
      final_video =self._get_final_video(proto_video)
      # Create saving path
      saving_path = join(self._folder_saving_path, video)
      # Save video
      final_video.write_videofile(saving_path[:-3] + 'mp4')
      # Delete old video and audio
      os.remove(path_v)
      os.remove(path_a)

def main():
    #Read timestamps from txt file
    with open("VideoCutTarget.txt") as partition:
        partition = partition.read()
        First = Mixing(author_path = '/content/drive/MyDrive/directory', 
                   my_video_path = '/content/drive/MyDrive/Copy of Pixel Restauration.mp4', 
                   saving_path ='/content/drive/MyDrive',
                   partition = partition)
        First.work()

if __name__ == "__main__":
    main()
