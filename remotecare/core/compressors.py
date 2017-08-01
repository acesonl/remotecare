# -*- coding: utf-8 -*-
import cssmin
from pipeline.compressors import CompressorBase


class CSSMinCompressor(CompressorBase):
    """
    Compress CSS wrapper for cssmin
    """
    def compress_css(self, css):
        """
        Return compressed CSS
        """
        return cssmin.cssmin(css)
