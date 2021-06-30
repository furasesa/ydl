import logging
import youtube_dl


# def get_value(format_dict, key):
#     log = logging.getLogger('get_value')
#     if format_dict.get(key) is not None:
#         # log.debug('{}: {}'.format(key, format_dict.get(key)))
#         return format_dict.get(key)
#     else:
#         log.error('key: {} is not found'.format(key))


def get_video_specific(format_dict):
    # log = logging.getLogger('get_video_specific')
    # log.info('format_dict: {}'.format(type(format_dict)))
    height = format_dict.get('height')
    width = format_dict.get('width')
    fps = format_dict.get('fps')
    _filesize = format_dict.get('filesize')
    # vbr = self.get_value(format_dict, 'vbr')
    vcodec = format_dict.get('vcodec')
    filesize = 0

    # fixes
    """get pixel quality by extracting Height or width
    some video has different orientation
    try to get from dict 'resolution' if height or width is None
    """
    if int(width) > int(height):
        video_quality = '{}p'.format(height)
    else:
        video_quality = '{}p'.format(width)

    if width is not None and height is not None:
        resolution = '{}x{}'.format(width, height)
    else:
        resolution = vars(format_dict).get('resolution')

    if _filesize is not None:
        filesize = float(_filesize) / 1000000

    val = '{:<5}@{:<3}{:<6.4}{:10}{:>7.3f}{}'.format(video_quality, fps, vcodec, resolution, filesize, ' MB')
    # log.debug('value: {}'.format(val))
    return val


def get_audio_specific(format_dict):
    # log = logging.getLogger('get_audio_specific')
    # log.info('type of format_dict: {}'.format(type(format_dict)))
    acodec = format_dict.get('acodec')
    abr = format_dict.get('abr')
    asr = format_dict.get('asr')
    val = '{}@{:<6}{}'.format(abr, asr, acodec)
    # log.info(val)
    return val


class ContextManager:
    def __init__(self):
        # self.formats = None
        self.info_list = []
        self.all_formats = []
        self.video_formats = []
        self.audio_formats = []
        self.webm_video_list = ['243', '244', '245', '246', '247', '248', '301', '302', '303', '304', '305']
        self.mp4_video_list = ['134', '135', '136', '137', '297', '298', '299', '397', '398', '399']
        self.va_list = ['18', '22']

    def get_webm_video_list(self) -> [str]:
        return self.webm_video_list

    def get_mp4_video_list(self) -> [str]:
        return self.mp4_video_list

    def get_va_list(self) -> [str]:
        return self.va_list

    def get_all_formats(self):
        return self.all_formats

    def get_video_formats(self):
        return self.video_formats

    def get_audio_formats(self):
        return self.audio_formats

    # def print_info_list(self):
    #     for info in self.info_list:
    #         print('\n\n', info, '\n\n')

    def print_all_format(self):
        for info in self.all_formats:  # dict
            title = info['title']
            url = info['url']
            format_ids = info['format_selector']
            print('title: {}\nurl:{}\nid:'.format(title, url))
            for fid in format_ids:
                print(fid)

    def generate_info(self, url):
        """Get Json info youtube_dl.YoutubeDL({'forcejson': True}).extract_info(uri, download=False)
        push to self.all_formats_builder(title, webpage_url, formats)
        self.filtered_builder(title, webpage_url, formats)
        """
        log = logging.getLogger('generate_info')
        try:
            for uri in url:
                info_pack = {}
                json_info = youtube_dl.YoutubeDL({'forcejson': True}).extract_info(uri, download=False)
                # self.format_list.append((uri, info.get('formats', [info])))

                # [({'url': link}, {id: id}, {formats: fmt})]
                video_id = json_info.get('id')
                uploader = json_info.get('uploader')
                title = json_info.get('title')
                upload_date = json_info.get('uploade_date')
                description = json_info.get('description')
                categories = json_info.get('categories')
                duration = json_info.get('duration')
                webpage_url = json_info.get('webpage_url')
                if webpage_url is None:
                    webpage_url = uri
                view_count = json_info.get('view_count')
                average_rating = json_info.get('average_rating')
                formats = json_info.get('formats')  # list
                info_pack.update({
                    'video_id': video_id,
                    'uploader': uploader,
                    'title': title,
                    'upload_date': upload_date,
                    'description': description,
                    'categories': categories,
                    'duration': duration,
                    'webpage_url': webpage_url,
                    'view_count': view_count,
                    'average_rating': average_rating,
                    'formats': formats
                })
                # print('info pack\n', info_pack, '\n\n')
                log.debug('{}'.format(info_pack))
                self.info_list.append(info_pack)
                self.all_formats_builder(title, webpage_url, formats)
                self.filtered_builder(title, webpage_url, formats)

        except youtube_dl.DownloadError as e:
            log.error('{}', e)

    def all_formats_builder(self, title, url, formats):
        log = logging.getLogger('all_formats_builder')
        all_format_pack = {}
        format_selector = []

        def get_codec_type(format_dict):
            if format_dict.get('vcodec') == 'none':
                return 'audio_only'
            elif format_dict.get('acodec') == 'none':
                return 'video_only'
            else:
                return 'av'

        for fmt in formats:
            format_id = fmt['format_id']
            ext = fmt['ext']
            codec_type = get_codec_type(fmt)
            # log.info('codec type: {}'.format(codec_type))
            video_spec = None
            audio_spec = None
            if codec_type == 'av':
                video_spec = get_video_specific(fmt)
                audio_spec = get_audio_specific(fmt)
            elif codec_type == 'audio_only':
                audio_spec = get_audio_specific(fmt)
            elif codec_type == 'video_only':
                video_spec = get_video_specific(fmt)
            else:
                logging.error('unknown type')

            if video_spec is not None and audio_spec is not None:
                # av
                specific = '{} + {}'.format(video_spec, audio_spec)
            elif audio_spec is None:
                # video only
                specific = '{}'.format(video_spec)
            elif video_spec is None:
                # audio only
                specific = '{}'.format(audio_spec)
            else:
                # not supported
                specific = None

            format_selector.append((format_id, '{:6} {}'.format(ext, specific)))

        # title, url, format_selector = tuple
        all_format_pack.update({
            'url': url,
            'title': title,
            'format_selector': format_selector
        })

        self.all_formats.append(all_format_pack)
        log.debug(self.all_formats)

        # logging.info(self.all_result)

    def filtered_builder(self, title, url, formats):
        log = logging.getLogger('filtered_builder')
        webm_audio_spec = ''
        m4a_spec = ''
        audio_format_pack = {}
        video_format_pack = {}
        video_selector_list = []
        audio_selector_list = []

        for fmt in formats:
            format_id = fmt['format_id']
            ext = fmt['ext']
            # initialize audio id for mp4 video
            if format_id == '140':
                log.debug('found m4a audio format: {}'.format(format_id))
                m4a_spec = get_audio_specific(fmt)
                audio_selector_list.append((format_id, '{:6} {}'.format(ext, m4a_spec)))

            if format_id == '251':
                log.debug('found webm audio format: {}'.format(format_id))
                webm_audio_spec = get_audio_specific(fmt)
                audio_selector_list.append((format_id, '{:6} {}'.format(ext, webm_audio_spec)))

            # webm video
            if format_id in self.webm_video_list:
                log.debug('found webm video format: {}'.format(format_id))
                video_spec = get_video_specific(fmt)
                if webm_audio_spec is not None:
                    # audio_spec = webm_audio_spec  # ignored
                    video_selector_list.append(('%s+251' % format_id, '{:6}{}'.format(ext, video_spec)))

            # mp4 video
            if format_id in self.mp4_video_list:
                log.debug('found mp4 video format: {}'.format(format_id))
                video_spec = get_video_specific(fmt)
                if m4a_spec is not None:
                    # audio_spec = m4a_spec  # ignored
                    video_selector_list.append(('%s+140' % format_id, '{:6}{}'.format(ext, video_spec)))

            if format_id in self.va_list:
                log.debug('found va format: {}'.format(format_id))
                video_spec = get_video_specific(fmt)
                video_selector_list.append((format_id, '{:6.3}{}'.format(ext, video_spec)))

        audio_format_pack.update({
            'url': url,
            'title': title,
            'format_selector': audio_selector_list
        })
        video_format_pack.update({
            'url': url,
            'title': title,
            'format_selector': video_selector_list
        })
        log.info('push audio {}'.format(audio_format_pack))
        log.info('push video {}'.format(video_format_pack))
        self.audio_formats.append(audio_format_pack)
        self.video_formats.append(video_format_pack)
        # logging.info(self.result)

# formats = mdict.get('formats', [mdict])
# table = [
#     [ydl.YoutubeDL.format_resolution(f), f['format_id'], f['ext'], format_note(f)]
#     for f in formats
#     if f.get('preference') is None or f['preference'] >= -1000]
# # logging.debug(formats)
# for t in table:
#     print(t)
