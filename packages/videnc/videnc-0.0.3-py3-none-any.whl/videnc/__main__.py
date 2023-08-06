import argparse
import os
import sys

from python_find.tree_search import TreeSearch
from typing import List

from .video import Video

def output_path_handler(output_path: str) -> None:
    """ Create non-existent output path """

    if not os.path.isdir(output_path):
            if output_path == DEFAULT_OUTPUT_PATH:
                os.mkdir(output_path)

            else:
                invalid_input = True

                while invalid_input:
                    response = input('{0} does not exist. Should it be created (y/n)? '.format(output_path))

                    if response.lower() == 'y':
                        invalid_input = False

                        os.mkdir(output_path)
    
                    elif response.lower() == 'n':
                        invalid_input = False

                        print('{0} won\'t be created.'.format(output_path))
                        print('Exiting.')
                        exit()
    
                    if invalid_input:
                        print('Invalid input. Type "y" for yes or "n" for no.')


def main(cl_args: List[str]) -> int:
    DEFAULT_OUTPUT_PATH = os.path.expanduser('~/videnc')
    DEFAULT_PROGRESSIVE_VIDEO = False
    parser = argparse.ArgumentParser(
        prog='videnc',
        description='A python script for video processing and information.')

    # TODO Video container type option. The MKV container is hardcoded right now.

    # TODO use nargs='*' to take multiple paths
    parser.add_argument('path',
        help='path to video or directory containing video files')
    
    parser.add_argument('-c', '--compress', type=bool, default=True,
        help='enable video compression to output directory')
        
    parser.add_argument('-vp', '--progressive', default=DEFAULT_PROGRESSIVE_VIDEO,
        choices=['yadif'], help='apply deinterlacing filter to video')
    parser.add_argument('-o', '--output-path', default=DEFAULT_OUTPUT_PATH,
        help='directory to place output file(s)')
    parser.add_argument('-d', '--delete-source', type=bool, default=False,
        help='delete source files after successful encode')
    parser.add_argument('-q', '--quality', type=int, default=25,
        choices=range(52),
        help='quality of output video, see FFmpeg x265 CRF for more')
    parser.add_argument('-p', '--preset', default='medium',
        choices=['ultrafast', 'superfast', 'veryfast', 'faster', 'fast',
            'medium', 'slow', 'slower', 'veryslow'],
        help='used to achieve certain encoding speed to compression ratio.')
    parser.add_argument('-a', '--audio-streams', default=None,
        help='comma separated list of audio streams to select for output')
        
    video_scaling_args = parser.add_argument_group('Video scaling')    
    video_scaling_args.add_argument('-vh', '--video-height', default=None,
        help='Set height when scaling the video. Must also set video width')
    video_scaling_args.add_argument('-vw', '--video-width', default=None,
        help='Set width when scaling the video. Must also set video height')

    args = parser.parse_args(cl_args)
    
    input_path = os.path.expanduser(args.path)
    output_path = os.path.expanduser(args.output_path)
    video_width = args.video_width
    video_height = args.video_height
    selected_audio_streams = args.audio_streams

    try:
        # get audio streams to include
        if selected_audio_streams:
            selected_audio_streams = selected_audio_streams.split(',')

        output_path_handler(output_path)

        if os.path.isdir(input_path):
            search = TreeSearch(root=input_path, name='*.mkv')
            for video in search.generate_found_files():
                path_basename = os.path.basename(video)
                video_output_path = os.path.join(output_path, path_basename)
                Video(path=video, output_path=video_output_path,
                    audio_streams=selected_audio_streams,
                    compress=args.compress, preset=args.preset,
                    quality=args.quality, video_height=video_height,
                    video_width=video_width)

                if args.delete_source:
                    os.remove(video)

        else:
            # TODO check if file is specified video container (hardcoded MKV currently)
            path_basename = os.path.basename(input_path)
            video_output_path = os.path.join(output_path, path_basename)
            Video(path=input_path, output_path=video_output_path,
                audio_streams=selected_audio_streams,
                compress=args.compress, preset=args.preset,
                quality=args.quality, video_height=video_height,
                video_width=video_width)

            if args.delete_source:
                os.remove(input_path)

        exit(0)

    except KeyboardInterrupt:
        # TODO cleanup file currently being compressed before exiting
        print('User canceled operation.')        
        print('Exiting.')

    #finally:

if __name__ == '__main__':
    main(sys.argv[1:])

