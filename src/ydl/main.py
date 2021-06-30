import logging
from .downloader import Downloader
from prompt_toolkit.shortcuts import checkboxlist_dialog
from .context import ContextManager


class VidDownloader:
    def __init__(self, url):
        self.ydl = Downloader()
        self.ctm = ContextManager()
        self.ctm.generate_info(url)
        # get known format_id
        self.webm_video_list = self.ctm.get_webm_video_list()
        self.mp4_video_list = self.ctm.get_mp4_video_list()
        self.va_list = self.ctm.get_va_list()
        self.queue_downloads = []

    def use_external_downloader(self, downloader):
        self.ydl.set_config('external_downloader', downloader)

    def termux_tmpl(self):
        self.ydl.set_config('outtmpl', '~/storage/downloads/youtube-dl/%(title)s.%(ext)s')

    def output_tmpl(self, out_tmpl):
        self.ydl.set_config('outtmpl', out_tmpl)

    def print_available_formats(self):
        self.ctm.print_all_format()

    def all_format_wizard(self):
        for fmts in self.ctm.get_all_formats():
            url = fmts.get('url')
            title = fmts.get('title')
            formats = fmts.get('format_selector')

            selected_list = checkboxlist_dialog(
                title=title+"140+mp4 or 251+webm(video)",
                text="link {}".format(url),
                values=formats
            ).run()

            if '140' in selected_list:
                format_choose = ['140+' + v for v in self.mp4_video_list if v in selected_list]
            elif '251' in selected_list:
                format_choose = ['251+' + v for v in self.webm_video_list if v in selected_list]
            else:
                format_choose = None

            self.queue_downloads.append({'url': url, 'formats': format_choose})

    def video_download_wizard(self, extension=None, selected_format=None):
        # default mode
        # print('\nvideo formats\n',video_formats)
        if extension is not None:
            self.ydl.set_postprocessors({
                'key': 'FFmpegVideoConvertor',
                'preferedformat': extension,
            })
        for fmts in self.ctm.get_video_formats():
            url = fmts.get('url')
            title = fmts.get('title')
            formats = fmts.get('format_selector')

            if selected_format is not None:
                format_choose = selected_format
            else:
                selected_list = checkboxlist_dialog(
                    title=title,
                    text="link {}".format(url),
                    values=formats
                ).run()
                format_choose = selected_list
            logging.debug('format choose: {}'.format(format_choose))
            self.queue_downloads.append({'url': url, 'formats': format_choose})

    def audio_only_downloads(self, acodec='mp3', quality=1):
        self.ydl.set_postprocessors(
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': acodec,
                'preferredquality': quality,
            },
        )
        self.ydl.set_postprocessors({'key': 'FFmpegMetadata'},)
        for fmts in self.ctm.get_audio_formats():
            url = fmts.get('url')
            # title = fmts.get('title')
            format_choose = ['251/140']
            self.queue_downloads.append({'url': url, 'formats': format_choose})

    def run(self, simulate=False):
        for downloads in self.queue_downloads:
            url = downloads.get('url')
            formats = downloads.get('formats')
            for f in formats:
                self.ydl.set_url(url)
                self.ydl.set_config('format', f)
                if simulate:
                    self.ydl.test()
                else:
                    self.ydl.run()

