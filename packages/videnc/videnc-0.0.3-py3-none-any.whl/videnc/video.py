import av
import os
import subprocess

from typing import List

from av import AVError
import ffpb

class Video:
    def __init__(self, path: str, audio_streams: List[int] = None,
            output_path: str = None, compress: bool = False, 
            preset: str = 'medium',  quality: int = 25,
            video_width: int = None, video_height: int = None,
            deint: bool = False, deint_filter: str = 'yadif'):
        self.video_container = av.open(path)
        self.audio_layouts = self._get_audio_layouts()

        # TODO if not compressing video print video info?

        if compress and output_path:
            ffmpeg_cl = self._get_ffmpeg_cl(path, output_path, audio_streams,
                preset, quality, video_width, video_height, deint, deint_filter)
            print(ffmpeg_cl)
            ffpb.main(ffmpeg_cl)

    def _get_ffmpeg_cl(self, path: str, output_path: str,
            audio_streams: List[int] = None, preset: str = 'medium',
            quality: int = 25, video_width: int = None,
            video_height: int = None,deint: bool = False,
            deint_filter: str = 'yadif') -> List[str]:
        video_name, video_ext = os.path.splitext(os.path.basename(path))
        metadata_notitle = ['-metadata:s:v:0', 'title=' + video_name,
            '-metadata', 'title=' + video_name]

        # don't change ffmpeg cl method order without checking dependencies
        return ['-i', path] \
            + ['-map', '0:v:0'] \
            + self._get_ffmpeg_audio_stream_options(audio_streams) \
            + self._get_ffmpeg_audio_filter_options() \
            + self._get_ffmpeg_audio_bitrate_options() \
            + self._get_ffmpeg_video_options(preset, quality, video_width,
                video_height) \
            + self._get_ffmpeg_color_depth_options() \
            + self._get_ffmpeg_subtitle_options() \
            + metadata_notitle \
            + [output_path]

    def _get_ffmpeg_audio_filter_options(self) -> List[str]:
        """ needs _get_ffmpeg_audio_stream_options run before running this!
        """
        audio_filters = []

        if len(self.selected_audio_streams) > 1:
            for stream in self.selected_audio_streams:
                layout = self.audio_layouts[stream]
                if 'mono' in layout:
                    audio_filters += [f'-filter:a:{stream}',
                        'aformat=channel_layouts=mono']
    
                elif 'stereo' in layout:
                    audio_filters += [f'-filter:a:{stream}',
                        'aformat=channel_layouts=stereo']
    
                elif '5.1' in layout:
                    audio_filters += [f'-filter:a:{stream}',
                        'aformat=channel_layouts=5.1']
    
                elif '7.1' in layout:
                    audio_filters += [f'-filter:a:{stream}',
                        'aformat=channel_layouts=7.1']

        else:
            layout = self.audio_layouts[self.selected_audio_streams[0]]
            if 'mono' in layout:
                audio_filters += ['-filter:a:0', 'aformat=channel_layouts=mono']
        
            elif 'stereo' in layout:
                audio_filters += ['-filter:a:0', 'aformat=channel_layouts=stereo']

            elif '5.1' in layout:
                audio_filters += ['-filter:a:0', 'aformat=channel_layouts=5.1']

            elif '7.1' in layout:
                audio_filters += ['-filter:a:0', 'aformat=channel_layouts=7.1']
        
        return audio_filters

    def _get_ffmpeg_audio_stream_options(self,
            streams: List[int] = None) -> List[int]:
        """ Get audio stream mappings for ffmpeg command line. """
        self.selected_audio_streams = []
        audio_stream_options = []

        # select all audio streams
        if not streams:
            for s in range(self.audio_streams):
                self.selected_audio_streams.append(int(s))
                audio_stream_options += ['-map', f'0:a:{s}']

            return audio_stream_options

        # only get selected audio streams
        else:
            for s in streams:
                self.selected_audio_streams.append(int(s))
                audio_stream_options += ['-map', f'0:a:{s}']

            return audio_stream_options

    def _get_ffmpeg_subtitle_options(self, copy: bool = True,
            disabled: bool = False) -> List[str]:
        if disabled and not copy:
            return ['-sn']

        elif copy and not disabled:
            return ['-map', '0:s?', '-c:s', 'copy']

        else:
            raise ValueError('Only one subtitle option can be enabled.')

    def _get_ffmpeg_color_depth_options(self, b8: bool = False, b10: bool = False,
            b12: bool = True) -> List[str]:
        if b8 and not b10 and not b12:
            return ['-pix_fmt', 'yuv420p']

        if b10 and not b8 and not b12:
            return ['-pix_fmt', 'yuv420p10le']

        if b12 and not b8 and not b10:
            return ['-pix_fmt', 'yuv420p12le']

        else:
            raise ValueError('Only one color depth option can be enabled.')

    def _get_ffmpeg_audio_bitrate_options(self) -> List[str]:
        stream = 0
        codec = ['-c:a', 'libopus']
        bitrate_1ch = [f'-b:a:{stream}', '12k']
        bitrate_2ch = [f'-b:a:{stream}', '64k']
        bitrate_6ch = [f'-b:a:{stream}', '192k']
        bitrate_8ch = [f'-b:a:{stream}', '256k']
    
        if len(self.selected_audio_streams) > 1:
            encode_option_list = codec
            for stream in self.selected_audio_streams:
                bitrate_1ch = [f'-b:a:{stream}', '12k']
                bitrate_2ch = [f'-b:a:{stream}', '64k']
                bitrate_6ch = [f'-b:a:{stream}', '192k']
                bitrate_8ch = [f'-b:a:{stream}', '256k']
                layout = self.audio_layouts[stream]

                if '7.1' in layout:
                    encode_option_list += bitrate_8ch
    
                elif '5.1' in layout:
                    encode_option_list += bitrate_6ch
    
                elif 'stereo' in layout:
                    encode_option_list += bitrate_2ch
    
                elif 'mono' in layout:
                    encode_option_list += bitrate_1ch
    
            return encode_option_list
    
        else:
            layout = self.audio_layouts[self.selected_audio_streams[0]]
            if '7.1' in layout:
                return codec + bitrate_8ch
    
            elif '5.1' in layout:
                return codec + bitrate_6ch
    
            elif 'stereo' in layout:
                return codec + bitrate_2ch
    
            elif 'mono' in layout:
                return codec + bitrate_1ch


    def _get_ffmpeg_video_options(self, preset: str, quality: int,
            video_width: int = None, video_height: int = None,
            deint: bool = False, deint_filter: str = 'yadif') -> List[str]:
        """ Return ffmpeg video encoding options """

        video_options = ['-preset', preset, '-crf', str(quality), '-c:v', 'libx265']

        if video_width and video_height:
            video_options += ['-vf', 'scale={}:{}'.format(video_width, video_height)]

        if deint:
            video_options += ['-vf', deint_filter]

        return video_options
    
    def _get_audio_channels(self, stream: int) -> str:
        for frame in self.video_container.decode(audio=stream):
            return frame.layout.name

    def _get_audio_layouts(self) -> List[str]:
        """ Get the number of audio channels of each audio stream

        Returns
            A list of strings representing the audio channel layout of each
            audio stream.
        """
        audio_layouts = []
        self.audio_streams = 0
        while True:
            try:
                audio_layouts.append(self._get_audio_channels(self.audio_streams))
                self.audio_streams += 1

            except IndexError:
                return audio_layouts

