"""
Python wrapper for ffprobe command line tool. ffprobe must exist in the path.
"""
import functools
import operator
import os
import pipes
import platform
import subprocess
import json

from ffprobe3.exceptions import FFProbeError


class FFProbe:
    """
    FFProbe wraps the ffprobe command and pulls the data into an object form::
        metadata=FFProbe('multimedia-file.mov')
    """

    def __init__(self, path_to_video):
        self.path_to_video = path_to_video

        try:
            with open(os.devnull, 'w') as tempf:
                subprocess.check_call(["ffprobe", "-h"], stdout=tempf, stderr=tempf)
        except FileNotFoundError:
            raise IOError('ffprobe not found.')

        if os.path.isfile(self.path_to_video):
            if platform.system() == 'Windows':
                cmd = ["ffprobe", "-v quiet -print_format json -show_format -show_streams", self.path_to_video]
            else:
                cmd = ["ffprobe -v quiet -print_format json -show_format -show_streams " + pipes.quote(self.path_to_video)]

            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

            self.streams = []
            self.video = []
            self.audio = []
            self.subtitle = []
            self.attachment = []

            jstdout = ""

            for line in iter(p.stdout.readline, b''):
                line = line.decode('UTF-8').strip()
                jstdout += line

            p.stdout.close()
            p.stderr.close()

            # read the streams
            jstreams = json.loads(jstdout)

            if 'streams' in jstreams:
                for dstream in jstreams['streams']:
                    self.streams.append(FFStream(dstream))

                for stream in self.streams:
                    if stream.is_audio():
                        self.audio.append(stream)
                    elif stream.is_video():
                        self.video.append(stream)
                    elif stream.is_subtitle():
                        self.subtitle.append(stream)
                    elif stream.is_attachment():
                        self.attachment.append(stream)
            else:
                raise FFProbeError('Unrecognized media file ' + self.path_to_video)

        else:
            raise IOError('No such media file ' + self.path_to_video)

    def __repr__(self):
        return "<FFprobe: {video}, {audio}, {subtitle}, {attachment}>".format(**vars(self))

    def file_name(self):
        return self.path_to_video

class FFStream:
    """
    An object representation of an individual stream in a multimedia file.
    """
    def __init__(self, dstream):
        self.dstream = dstream

        try:

            self.dstream['framerate'] = None
            array_framerate = self.dstream.get('avg_frame_rate', '').split('/')

            if 2 == len(array_framerate) and array_framerate[1] > 0:
                self.dstream['framerate'] = round(functools.reduce(operator.truediv, map(int, array_framerate)))

        except:
            self.dstream['framerate'] = None

    def __repr__(self):
        if self.is_video():
            template = "<Stream: #{index} [{codec_type}] {codec_long_name}, {framerate}, ({width}x{height})>"

        elif self.is_audio():
            template = "<Stream: #{index} [{codec_type}] {codec_long_name}, channels: {channels} ({channel_layout}), " \
                       "{sample_rate}Hz> "

        elif self.is_subtitle() or self.is_attachment():
            template = "<Stream: #{index} [{codec_type}] {codec_long_name}>"

        else:
            template = ''

        return template.format(**self.dstream)

    def is_audio(self):
        """
        Is this stream labelled as an audio stream?
        """
        return self.dstream.get('codec_type', None) == 'audio'

    def is_video(self):
        """
        Is the stream labelled as a video stream.
        """
        return self.dstream.get('codec_type', None) == 'video'

    def is_subtitle(self):
        """
        Is the stream labelled as a subtitle stream.
        """
        return self.dstream.get('codec_type', None) == 'subtitle'

    def is_attachment(self):
        """
        Is the stream labelled as a attachment stream.
        """
        return self.dstream.get('codec_type', None) == 'attachment'

    def frame_size(self):
        """
        Returns the pixel frame size as an integer tuple (width,height) if the stream is a video stream.
        Returns None if it is not a video stream.
        """
        size = None
        if self.is_video():
            width = self.dstream['width']
            height = self.dstream['height']

            if width and height:
                try:
                    size = (int(width), int(height))
                except ValueError:
                    raise FFProbeError("None integer size {}:{}".format(width, height))
        else:
            return None

        return size

    def width(self):
        """
        If this is a video stream, return the width
        """
        try:
            width = self.dstream.get('width', '')
            return int(width) if width else None
        except ValueError:
            raise FFProbeError('None integer width')

    def height(self):
        """
        If this is a video stream, return the height
        """
        try:
            height = self.dstream.get('height', '')
            return int(height) if height else None
        except ValueError:
            raise FFProbeError('None integer height')

    def aspect_ratio(self):
        """
        Compute the aspect ratio as a decimal. Return the value None if this is not a video stream.
        """
        if self.is_video():

            # attempt to parse the aspect ratio used for display
            str_disp_aspect_ratio = self.dstream['display_aspect_ratio'] if 'display_aspect_ratio' in self.dstream else None

            if str_disp_aspect_ratio and 2 == len(str_disp_aspect_ratio.split(':')):
                aspect_ratios = str_disp_aspect_ratio.split(':')

                width = int(aspect_ratios[0])
                height = int(aspect_ratios[1])

                if width and height:
                    return width / height

            # if display aspect is undefined then assume the raw video height/width
            str_width = self.dstream['width']
            str_height = self.dstream['height']

            if str_width and str_height:
                try:
                    width = int(str_width) if str_width else None
                    height = int(str_height) if str_height else None

                    if width and height:
                        return width / height

                except ValueError:
                    raise FFProbeError("None integer size {}:{}".format(str_width, str_height))
        return None

    def pixel_format(self):
        """
        Returns a string representing the pixel format of the video stream. e.g. yuv420p.
        Returns none is it is not a video stream.
        """
        return self.dstream.get('pix_fmt', None)

    def frames(self):
        """
        Returns the length of a video stream in frames. Returns 0 if not a video stream.
        """
        if self.is_video() or self.is_audio():
            try:
                frame_count = int(self.dstream.get('nb_frames', ''))
            except ValueError:
                raise FFProbeError('None integer frame count')
        else:
            frame_count = 0

        return frame_count

    def duration_seconds(self):
        """
        Returns the runtime duration of the video stream as a floating point number of seconds.
        Returns 0.0 if not a video stream.
        """
        if self.is_video() or self.is_audio():
            try:
                duration = float(self.dstream.get('duration', ''))
            except ValueError:
                raise FFProbeError('None numeric duration')
        else:
            duration = 0.0

        return duration

    def language(self):
        """
        Returns language tag of stream. e.g. eng
        """
        return self.dstream.get('TAG:language', None)

    def codec(self):
        """
        Returns a string representation of the stream codec.
        """
        return self.dstream.get('codec_name', None)

    def codec_description(self):
        """
        Returns a long representation of the stream codec.
        """
        return self.dstream.get('codec_long_name', None)

    def codec_tag(self):
        """
        Returns a short representative tag of the stream codec.
        """
        return self.dstream.get('codec_tag_string', None)

    def channels(self):
        """
        Returns number of channels for an audio stream
        """
        try:
            channels = self.dstream.get('channels', '')
            return int(channels) if channels else None
        except ValueError:
            raise FFProbeError('None integer channels')

    def bit_rate(self):
        """
        Returns bit_rate as an integer in bps
        """
        try:
            bit_rate = self.dstream.get('bit_rate', '')
            return int(bit_rate) if bit_rate else None
        except ValueError:
            raise FFProbeError('None integer bit_rate')
