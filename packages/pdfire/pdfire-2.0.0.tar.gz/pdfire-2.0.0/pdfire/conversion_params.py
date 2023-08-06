import json

paper_formats = [
    'letter',
    'legal',
    'tabloid',
    'ledger',
    'a0',
    'a1',
    'a2',
    'a3',
    'a4',
    'a5',
    'a6',
]

medias = [
    'screen',
    'print',
]

class ConversionParams:
    def __init__(
        self,
        html: str = None,
        url: str = None,
        cdn: bool = None,
        storage = None,
        landscape: bool = None,
        print_background: bool = None,
        scale: float = None,
        format: str = None,
        paper_width = None,
        paper_height = None,
        margin = None,
        margin_top = None,
        margin_right = None,
        margin_bottom = None,
        margin_left = None,
        page_ranges: list = None,
        header_template: str = None,
        footer_template: str = None,
        prefer_css_page_size: bool = None,
        viewport_width: int = None,
        viewport_height: int = None,
        block_ads: bool = None,
        selector: str = None,
        wait_for_selector: str = None,
        wait_for_selector_timeout: int = None,
        wait_until: str = None,
        wait_until_timeout: int = None,
        delay: int = None,
        timeout: int = None,
        headers: dict = None,
        emulate_media: str = None,
        owner_password: str = None,
        user_password: str = None,
        allowErrorPage: bool = None,
        optimize: bool = None
    ):
        self.html = html
        self.url = url
        self.cdn = cdn
        self.storage = storage
        self.landscape = landscape
        self.print_background = print_background
        self.scale = scale
        self._format = None
        self.format = format
        self._paper_width = None
        self.paper_width = paper_width
        self._paper_height = None
        self.paper_height = paper_height
        self._margin = None
        self.margin = margin
        self._margin_top = None
        self.margin_top = margin_top
        self._margin_right = None
        self.margin_right = margin_right
        self._margin_bottom = None
        self.margin_bottom = margin_bottom
        self._margin_left = None
        self.margin_left = margin_left
        self.page_ranges = page_ranges
        self.header_template = header_template
        self.footer_template = footer_template
        self.prefer_css_page_size = prefer_css_page_size
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self.block_ads = block_ads
        self.selector = selector
        self.wait_for_selector = wait_for_selector
        self.wait_for_selector_timeout = wait_for_selector_timeout
        self.wait_until = wait_until
        self.wait_until_timeout = wait_until_timeout
        self.delay = delay
        self.timeout = timeout
        self.headers = headers
        self._emulate_media = None
        self.emulate_media = emulate_media
        self.owner_password = owner_password
        self.user_password = user_password
        self.allowErrorPage = allowErrorPage
        self.optimize = optimize

    @property
    def format(self):
        return self._format
    
    @format.setter
    def format(self, format: str):
        if not format in [None, *paper_formats]:
            raise TypeError("Invalid paper format '" + format + "'.")
        
        self._format = format
    
    @property
    def paper_width(self):
        return self._paper_width
    
    @paper_width.setter
    def paper_width(self, width):
        if not (width is None or type(width) in [None, int, str]):
            raise TypeError("Invalid paper width: '" + str(width) + "'.")
        
        self._paper_width = width

    @property
    def paper_height(self):
        return self._paper_height
    
    @paper_height.setter
    def paper_height(self, height):
        if not (height is None or type(height) in [None, int, str]):
            raise TypeError("Invalid paper height: '" + str(height) + "'.")
        
        self._paper_height = height
    
    @property
    def margin(self):
        return self._margin
    
    @margin.setter
    def margin(self, margin):
        if not (margin is None or type(margin) in [None, int, str]):
            raise TypeError("Invalid PDF margin: '" + str(margin) + "'.")
        
        self._margin = margin
    
    @property
    def margin_top(self):
        return self._margin_top
    
    @margin_top.setter
    def margin_top(self, margin):
        if not (margin is None or type(margin) in [None, int, str]):
            raise TypeError("Invalid PDF top margin: '" + str(margin) + "'.")
        
        self._margin_top = margin
    
    @property
    def margin_right(self):
        return self._margin_right
    
    @margin_right.setter
    def margin_right(self, margin):
        if not (margin is None or type(margin) in [None, int, str]):
            raise TypeError("Invalid PDF right margin: '" + str(margin) + "'.")
        
        self._margin_right = margin
    
    @property
    def margin_bottom(self):
        return self._margin_bottom
    
    @margin_bottom.setter
    def margin_bottom(self, margin):
        if not (margin is None or type(margin) in [None, int, str]):
            raise TypeError("Invalid PDF bottom margin: '" + str(margin) + "'.")
        
        self._margin_bottom = margin
    
    @property
    def margin_left(self):
        return self._margin_left
    
    @margin_left.setter
    def margin_left(self, margin):
        if not (margin is None or type(margin) in [int, str]):
            raise TypeError("Invalid PDF left margin: '" + str(margin) + "'.")
        
        self._margin_left = margin
    
    @property
    def emulate_media(self):
        return self._emulate_media
    
    @emulate_media.setter
    def emulate_media(self, media: str):
        if not media in [None, *medias]:
            raise TypeError("Invalid CSS media: '" + str(media) + "'.")
        
        self._emulate_media = media

    def to_dict(self):
        page_ranges = None
        
        if not self.page_ranges is None:
            page_ranges = map(lambda r: str(r).strip(), self.page_ranges)
            page_ranges = filter(lambda r: r != "", page_ranges)

        values = {
            'html': self.html,
            'url': self.url,
            'cdn': self.cdn,
            'storage': self.storage,
            'landscape': self.landscape,
            'printBackground': self.print_background,
            'scale': self.scale,
            'format': self.format,
            'paperWidth': self.paper_width,
            'paperHeight': self.paper_height,
            'margin': self.margin,
            'marginTop': self.margin_top,
            'marginRight': self.margin_right,
            'marginBottom': self.margin_bottom,
            'marginLeft': self.margin_left,
            'pageRanges': ",".join(page_ranges) if not page_ranges is None else None,
            'headerTemplate': self.header_template,
            'footerTemplate': self.footer_template,
            'preferCSSPageSize': self.prefer_css_page_size,
            'viewportWidth': self.viewport_width,
            'viewportHeight': self.viewport_height,
            'blockAds': self.block_ads,
            'selector': self.selector,
            'waitForSelector': self.wait_for_selector,
            'waitForSelectorTimeout': self.wait_for_selector_timeout,
            'waitUntil': self.wait_until,
            'waitUntilTimeout': self.wait_until_timeout,
            'delay': self.delay,
            'timeout': self.timeout,
            'headers': self.headers,
            'emulateMedia': self.emulate_media,
            'ownerPassword': self.owner_password,
            'userPassword': self.user_password,
            'allowErrorPage': self.allowErrorPage,
            'optimize': self.optimize
        }

        return {k: v for k, v in values.items() if v is not None}
