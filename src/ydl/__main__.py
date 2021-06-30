"""
usage:
ydl [-V]
ydl [-v --ph  -o=<output> -d=<downloader> --ext=<extension> -f=<format_id>...] URL...
ydl [-va --all -q=<quality> --ph -o=<output> -d=<downloader> --ext=<extension>] URL...
ydl [-vVFTa --all -q=<quality> --ph  -o=<output> -d=<downloader> --ext=<extension> -f=<format_id>... ] URL...

options:
-h --help           Print help
-v --verbose        Enable verbose
-F                  Print Format list
-T --test           Simulate output command. for test only
-a                  Download Audio Only. default selected format is 251
--all               Get all available format. use wizard instead of '-f'
-q=<quality>        Set audio quality. 0 is best. 160k is set for bitrates
-f=<format_id>      Download specified format id. is list format. For example:
                    '-f 137+140 -f 247+251' to download mp4 and webm videos
-o=<output>         doc: https://github.com/ytdl-org/youtube-dl/blob/master/README.md#output-template
                    id (string): Video identifier
                    title (string): Video title
                    url (string): Video URL
                    ext (string): Video filename extension
                    alt_title (string): A secondary title of the video
                    uploader (string): Full name of the video uploader
                    creator (string): The creator of the video
                    release_date (string): The date (YYYYMMDD) when the video was released
                    timestamp (numeric): UNIX timestamp of the moment the video became available
                    upload_date (string): Video upload date (YYYYMMDD)
                    channel (string): Full name of the channel the video is uploaded on
                    location (string): Physical location where the video was filmed
                    duration (numeric): Length of the video in seconds
                    view_count (numeric): How many users have watched the video on the platform
                    like_count (numeric): Number of positive ratings of the video
                    dislike_count (numeric): Number of negative ratings of the video
                    format (string): A human-readable description of the format
                    format_id (string): Format code specified by --format
                    example:
                    '-o %(title)s-%(id)s.%(ext)s'
-d=<downloader>     External downloader [default: aria2c]
--ph                Phone output template. useful for termux
                    output template will be like this
                    '~/storage/downloads/youtube-dl/%(title)s.%(ext)s'
--ext=<extension>   Defined output extension
                    Send FFMPEG post-processors to convert specified extension

"""


from docopt import docopt
import logging.config

from .logging_config import LOG_CONFIG
from .main import VidDownloader


def main():
    arguments = docopt(__doc__, version='ydl 0.0.2')
    # ydl[-vVFTa --all -q=<quality> --ph -o=<output> -d=<downloader> --ext=<extension> -f=<format_id> ...] URL...
    print(arguments)

    # Get Arguments data
    is_verbose = arguments.get('--verbose')
    # V is print version
    get_list_format = arguments.get('-F')
    simulate = arguments.get('--test')
    is_audio_only = arguments.get('-a')
    quality = arguments.get('-q')

    is_all_format = arguments.get('--all')
    phone_tmpl = arguments.get('--ph')
    out_tmpl = arguments.get('-o')
    ext_downloader = arguments.get('-d')
    extension = arguments.get('--ext')

    selected_format = arguments.get('-f')

    url_list = arguments.get('URL')

    verbosity_level = logging.DEBUG if is_verbose else logging.ERROR
    LOG_CONFIG.update({'root': {'handlers': ['console', 'filewritter'], 'level': verbosity_level}})
    # insert config
    logging.config.dictConfig(LOG_CONFIG)
    # test logging
    logging.debug('test file writer debug')
    logging.info('test info console')

    ydl = VidDownloader(url_list)

    if is_all_format:
        ydl.all_format_wizard()
    elif is_audio_only:
        ydl.audio_only_downloads(acodec=extension, quality=quality)
    else:
        ydl.video_download_wizard(extension=extension, selected_format=selected_format)

    ydl.run(simulate=simulate)


if __name__ == '__main__':
    main()

