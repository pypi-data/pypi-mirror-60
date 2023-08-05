# coding: utf-8
# -----------------------------------------------------------------------------------
# <copyright company="Aspose" file="GifSaveOptionsData.py">
#   Copyright (c) 2019 Aspose.Words for Cloud
# </copyright>
# <summary>
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
# </summary>
# -----------------------------------------------------------------------------------
import pprint
import re  # noqa: F401

import six


class GifSaveOptionsData(object):
    """Container class for gif save options.
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'save_format': 'str',
        'file_name': 'str',
        'dml_rendering_mode': 'str',
        'dml_effects_rendering_mode': 'str',
        'zip_output': 'bool',
        'update_last_saved_time_property': 'bool',
        'update_sdt_content': 'bool',
        'update_fields': 'bool',
        'color_mode': 'str',
        'jpeg_quality': 'int',
        'metafile_rendering_options': 'MetafileRenderingOptionsData',
        'numeral_format': 'str',
        'optimize_output': 'bool',
        'page_count': 'int',
        'page_index': 'int',
        'graphics_quality_options': 'GraphicsQualityOptionsData',
        'horizontal_resolution': 'float',
        'image_brightness': 'float',
        'image_color_mode': 'str',
        'image_contrast': 'float',
        'paper_color': 'str',
        'pixel_format': 'str',
        'resolution': 'float',
        'scale': 'float',
        'use_anti_aliasing': 'bool',
        'use_gdi_emf_renderer': 'bool',
        'use_high_quality_rendering': 'bool',
        'vertical_resolution': 'float'
    }

    attribute_map = {
        'save_format': 'SaveFormat',
        'file_name': 'FileName',
        'dml_rendering_mode': 'DmlRenderingMode',
        'dml_effects_rendering_mode': 'DmlEffectsRenderingMode',
        'zip_output': 'ZipOutput',
        'update_last_saved_time_property': 'UpdateLastSavedTimeProperty',
        'update_sdt_content': 'UpdateSdtContent',
        'update_fields': 'UpdateFields',
        'color_mode': 'ColorMode',
        'jpeg_quality': 'JpegQuality',
        'metafile_rendering_options': 'MetafileRenderingOptions',
        'numeral_format': 'NumeralFormat',
        'optimize_output': 'OptimizeOutput',
        'page_count': 'PageCount',
        'page_index': 'PageIndex',
        'graphics_quality_options': 'GraphicsQualityOptions',
        'horizontal_resolution': 'HorizontalResolution',
        'image_brightness': 'ImageBrightness',
        'image_color_mode': 'ImageColorMode',
        'image_contrast': 'ImageContrast',
        'paper_color': 'PaperColor',
        'pixel_format': 'PixelFormat',
        'resolution': 'Resolution',
        'scale': 'Scale',
        'use_anti_aliasing': 'UseAntiAliasing',
        'use_gdi_emf_renderer': 'UseGdiEmfRenderer',
        'use_high_quality_rendering': 'UseHighQualityRendering',
        'vertical_resolution': 'VerticalResolution'
    }

    def __init__(self, save_format=None, file_name=None, dml_rendering_mode=None, dml_effects_rendering_mode=None, zip_output=None, update_last_saved_time_property=None, update_sdt_content=None, update_fields=None, color_mode=None, jpeg_quality=None, metafile_rendering_options=None, numeral_format=None, optimize_output=None, page_count=None, page_index=None, graphics_quality_options=None, horizontal_resolution=None, image_brightness=None, image_color_mode=None, image_contrast=None, paper_color=None, pixel_format=None, resolution=None, scale=None, use_anti_aliasing=None, use_gdi_emf_renderer=None, use_high_quality_rendering=None, vertical_resolution=None):  # noqa: E501
        """GifSaveOptionsData - a model defined in Swagger"""  # noqa: E501

        self._save_format = None
        self._file_name = None
        self._dml_rendering_mode = None
        self._dml_effects_rendering_mode = None
        self._zip_output = None
        self._update_last_saved_time_property = None
        self._update_sdt_content = None
        self._update_fields = None
        self._color_mode = None
        self._jpeg_quality = None
        self._metafile_rendering_options = None
        self._numeral_format = None
        self._optimize_output = None
        self._page_count = None
        self._page_index = None
        self._graphics_quality_options = None
        self._horizontal_resolution = None
        self._image_brightness = None
        self._image_color_mode = None
        self._image_contrast = None
        self._paper_color = None
        self._pixel_format = None
        self._resolution = None
        self._scale = None
        self._use_anti_aliasing = None
        self._use_gdi_emf_renderer = None
        self._use_high_quality_rendering = None
        self._vertical_resolution = None
        self.discriminator = None

        if save_format is not None:
            self.save_format = save_format
        if file_name is not None:
            self.file_name = file_name
        if dml_rendering_mode is not None:
            self.dml_rendering_mode = dml_rendering_mode
        if dml_effects_rendering_mode is not None:
            self.dml_effects_rendering_mode = dml_effects_rendering_mode
        if zip_output is not None:
            self.zip_output = zip_output
        if update_last_saved_time_property is not None:
            self.update_last_saved_time_property = update_last_saved_time_property
        if update_sdt_content is not None:
            self.update_sdt_content = update_sdt_content
        if update_fields is not None:
            self.update_fields = update_fields
        if color_mode is not None:
            self.color_mode = color_mode
        if jpeg_quality is not None:
            self.jpeg_quality = jpeg_quality
        if metafile_rendering_options is not None:
            self.metafile_rendering_options = metafile_rendering_options
        if numeral_format is not None:
            self.numeral_format = numeral_format
        if optimize_output is not None:
            self.optimize_output = optimize_output
        if page_count is not None:
            self.page_count = page_count
        if page_index is not None:
            self.page_index = page_index
        if graphics_quality_options is not None:
            self.graphics_quality_options = graphics_quality_options
        if horizontal_resolution is not None:
            self.horizontal_resolution = horizontal_resolution
        if image_brightness is not None:
            self.image_brightness = image_brightness
        if image_color_mode is not None:
            self.image_color_mode = image_color_mode
        if image_contrast is not None:
            self.image_contrast = image_contrast
        if paper_color is not None:
            self.paper_color = paper_color
        if pixel_format is not None:
            self.pixel_format = pixel_format
        if resolution is not None:
            self.resolution = resolution
        if scale is not None:
            self.scale = scale
        if use_anti_aliasing is not None:
            self.use_anti_aliasing = use_anti_aliasing
        if use_gdi_emf_renderer is not None:
            self.use_gdi_emf_renderer = use_gdi_emf_renderer
        if use_high_quality_rendering is not None:
            self.use_high_quality_rendering = use_high_quality_rendering
        if vertical_resolution is not None:
            self.vertical_resolution = vertical_resolution

    @property
    def save_format(self):
        """Gets the save_format of this GifSaveOptionsData.  # noqa: E501

        Gets or sets format of save.  # noqa: E501

        :return: The save_format of this GifSaveOptionsData.  # noqa: E501
        :rtype: str
        """
        return self._save_format

    @save_format.setter
    def save_format(self, save_format):
        """Sets the save_format of this GifSaveOptionsData.

        Gets or sets format of save.  # noqa: E501

        :param save_format: The save_format of this GifSaveOptionsData.  # noqa: E501
        :type: str
        """
        self._save_format = save_format
    @property
    def file_name(self):
        """Gets the file_name of this GifSaveOptionsData.  # noqa: E501

        Gets or sets name of destination file.  # noqa: E501

        :return: The file_name of this GifSaveOptionsData.  # noqa: E501
        :rtype: str
        """
        return self._file_name

    @file_name.setter
    def file_name(self, file_name):
        """Sets the file_name of this GifSaveOptionsData.

        Gets or sets name of destination file.  # noqa: E501

        :param file_name: The file_name of this GifSaveOptionsData.  # noqa: E501
        :type: str
        """
        self._file_name = file_name
    @property
    def dml_rendering_mode(self):
        """Gets the dml_rendering_mode of this GifSaveOptionsData.  # noqa: E501

        Gets or sets a value determining how DrawingML shapes are rendered. { Fallback | DrawingML }.  # noqa: E501

        :return: The dml_rendering_mode of this GifSaveOptionsData.  # noqa: E501
        :rtype: str
        """
        return self._dml_rendering_mode

    @dml_rendering_mode.setter
    def dml_rendering_mode(self, dml_rendering_mode):
        """Sets the dml_rendering_mode of this GifSaveOptionsData.

        Gets or sets a value determining how DrawingML shapes are rendered. { Fallback | DrawingML }.  # noqa: E501

        :param dml_rendering_mode: The dml_rendering_mode of this GifSaveOptionsData.  # noqa: E501
        :type: str
        """
        self._dml_rendering_mode = dml_rendering_mode
    @property
    def dml_effects_rendering_mode(self):
        """Gets the dml_effects_rendering_mode of this GifSaveOptionsData.  # noqa: E501

        Gets or sets a value determining how DrawingML effects are rendered. { Simplified | None | Fine }.  # noqa: E501

        :return: The dml_effects_rendering_mode of this GifSaveOptionsData.  # noqa: E501
        :rtype: str
        """
        return self._dml_effects_rendering_mode

    @dml_effects_rendering_mode.setter
    def dml_effects_rendering_mode(self, dml_effects_rendering_mode):
        """Sets the dml_effects_rendering_mode of this GifSaveOptionsData.

        Gets or sets a value determining how DrawingML effects are rendered. { Simplified | None | Fine }.  # noqa: E501

        :param dml_effects_rendering_mode: The dml_effects_rendering_mode of this GifSaveOptionsData.  # noqa: E501
        :type: str
        """
        self._dml_effects_rendering_mode = dml_effects_rendering_mode
    @property
    def zip_output(self):
        """Gets the zip_output of this GifSaveOptionsData.  # noqa: E501

        Gets or sets controls zip output or not. Default value is false.  # noqa: E501

        :return: The zip_output of this GifSaveOptionsData.  # noqa: E501
        :rtype: bool
        """
        return self._zip_output

    @zip_output.setter
    def zip_output(self, zip_output):
        """Sets the zip_output of this GifSaveOptionsData.

        Gets or sets controls zip output or not. Default value is false.  # noqa: E501

        :param zip_output: The zip_output of this GifSaveOptionsData.  # noqa: E501
        :type: bool
        """
        self._zip_output = zip_output
    @property
    def update_last_saved_time_property(self):
        """Gets the update_last_saved_time_property of this GifSaveOptionsData.  # noqa: E501

        Gets or sets a value determining whether the Aspose.Words.Properties.BuiltInDocumentProperties.LastSavedTime property is updated before saving.  # noqa: E501

        :return: The update_last_saved_time_property of this GifSaveOptionsData.  # noqa: E501
        :rtype: bool
        """
        return self._update_last_saved_time_property

    @update_last_saved_time_property.setter
    def update_last_saved_time_property(self, update_last_saved_time_property):
        """Sets the update_last_saved_time_property of this GifSaveOptionsData.

        Gets or sets a value determining whether the Aspose.Words.Properties.BuiltInDocumentProperties.LastSavedTime property is updated before saving.  # noqa: E501

        :param update_last_saved_time_property: The update_last_saved_time_property of this GifSaveOptionsData.  # noqa: E501
        :type: bool
        """
        self._update_last_saved_time_property = update_last_saved_time_property
    @property
    def update_sdt_content(self):
        """Gets the update_sdt_content of this GifSaveOptionsData.  # noqa: E501

        Gets or sets value determining whether content of  is updated before saving.  # noqa: E501

        :return: The update_sdt_content of this GifSaveOptionsData.  # noqa: E501
        :rtype: bool
        """
        return self._update_sdt_content

    @update_sdt_content.setter
    def update_sdt_content(self, update_sdt_content):
        """Sets the update_sdt_content of this GifSaveOptionsData.

        Gets or sets value determining whether content of  is updated before saving.  # noqa: E501

        :param update_sdt_content: The update_sdt_content of this GifSaveOptionsData.  # noqa: E501
        :type: bool
        """
        self._update_sdt_content = update_sdt_content
    @property
    def update_fields(self):
        """Gets the update_fields of this GifSaveOptionsData.  # noqa: E501

        Gets or sets a value determining if fields should be updated before saving the document to a fixed page format. Default value for this property is. true  # noqa: E501

        :return: The update_fields of this GifSaveOptionsData.  # noqa: E501
        :rtype: bool
        """
        return self._update_fields

    @update_fields.setter
    def update_fields(self, update_fields):
        """Sets the update_fields of this GifSaveOptionsData.

        Gets or sets a value determining if fields should be updated before saving the document to a fixed page format. Default value for this property is. true  # noqa: E501

        :param update_fields: The update_fields of this GifSaveOptionsData.  # noqa: E501
        :type: bool
        """
        self._update_fields = update_fields
    @property
    def color_mode(self):
        """Gets the color_mode of this GifSaveOptionsData.  # noqa: E501

        Gets or sets a value determining how colors are rendered. { Normal | Grayscale}.  # noqa: E501

        :return: The color_mode of this GifSaveOptionsData.  # noqa: E501
        :rtype: str
        """
        return self._color_mode

    @color_mode.setter
    def color_mode(self, color_mode):
        """Sets the color_mode of this GifSaveOptionsData.

        Gets or sets a value determining how colors are rendered. { Normal | Grayscale}.  # noqa: E501

        :param color_mode: The color_mode of this GifSaveOptionsData.  # noqa: E501
        :type: str
        """
        self._color_mode = color_mode
    @property
    def jpeg_quality(self):
        """Gets the jpeg_quality of this GifSaveOptionsData.  # noqa: E501

        Gets or sets determines the quality of the JPEG images inside PDF document.  # noqa: E501

        :return: The jpeg_quality of this GifSaveOptionsData.  # noqa: E501
        :rtype: int
        """
        return self._jpeg_quality

    @jpeg_quality.setter
    def jpeg_quality(self, jpeg_quality):
        """Sets the jpeg_quality of this GifSaveOptionsData.

        Gets or sets determines the quality of the JPEG images inside PDF document.  # noqa: E501

        :param jpeg_quality: The jpeg_quality of this GifSaveOptionsData.  # noqa: E501
        :type: int
        """
        self._jpeg_quality = jpeg_quality
    @property
    def metafile_rendering_options(self):
        """Gets the metafile_rendering_options of this GifSaveOptionsData.  # noqa: E501

        Gets or sets allows to specify metafile rendering options.  # noqa: E501

        :return: The metafile_rendering_options of this GifSaveOptionsData.  # noqa: E501
        :rtype: MetafileRenderingOptionsData
        """
        return self._metafile_rendering_options

    @metafile_rendering_options.setter
    def metafile_rendering_options(self, metafile_rendering_options):
        """Sets the metafile_rendering_options of this GifSaveOptionsData.

        Gets or sets allows to specify metafile rendering options.  # noqa: E501

        :param metafile_rendering_options: The metafile_rendering_options of this GifSaveOptionsData.  # noqa: E501
        :type: MetafileRenderingOptionsData
        """
        self._metafile_rendering_options = metafile_rendering_options
    @property
    def numeral_format(self):
        """Gets the numeral_format of this GifSaveOptionsData.  # noqa: E501

        Gets or sets indicates the symbol set that is used to represent numbers while rendering to fixed page formats.  # noqa: E501

        :return: The numeral_format of this GifSaveOptionsData.  # noqa: E501
        :rtype: str
        """
        return self._numeral_format

    @numeral_format.setter
    def numeral_format(self, numeral_format):
        """Sets the numeral_format of this GifSaveOptionsData.

        Gets or sets indicates the symbol set that is used to represent numbers while rendering to fixed page formats.  # noqa: E501

        :param numeral_format: The numeral_format of this GifSaveOptionsData.  # noqa: E501
        :type: str
        """
        self._numeral_format = numeral_format
    @property
    def optimize_output(self):
        """Gets the optimize_output of this GifSaveOptionsData.  # noqa: E501

        Gets or sets flag indicates whether it is required to optimize output of XPS. If this flag is set redundant nested canvases and empty canvases are removed, also neighbor glyphs with the same formatting are concatenated. Note: The accuracy of the content display may be affected if this property is set to true.  Default is false.  # noqa: E501

        :return: The optimize_output of this GifSaveOptionsData.  # noqa: E501
        :rtype: bool
        """
        return self._optimize_output

    @optimize_output.setter
    def optimize_output(self, optimize_output):
        """Sets the optimize_output of this GifSaveOptionsData.

        Gets or sets flag indicates whether it is required to optimize output of XPS. If this flag is set redundant nested canvases and empty canvases are removed, also neighbor glyphs with the same formatting are concatenated. Note: The accuracy of the content display may be affected if this property is set to true.  Default is false.  # noqa: E501

        :param optimize_output: The optimize_output of this GifSaveOptionsData.  # noqa: E501
        :type: bool
        """
        self._optimize_output = optimize_output
    @property
    def page_count(self):
        """Gets the page_count of this GifSaveOptionsData.  # noqa: E501

        Gets or sets determines number of pages to render.  # noqa: E501

        :return: The page_count of this GifSaveOptionsData.  # noqa: E501
        :rtype: int
        """
        return self._page_count

    @page_count.setter
    def page_count(self, page_count):
        """Sets the page_count of this GifSaveOptionsData.

        Gets or sets determines number of pages to render.  # noqa: E501

        :param page_count: The page_count of this GifSaveOptionsData.  # noqa: E501
        :type: int
        """
        self._page_count = page_count
    @property
    def page_index(self):
        """Gets the page_index of this GifSaveOptionsData.  # noqa: E501

        Gets or sets determines 0-based index of the first page to render.  # noqa: E501

        :return: The page_index of this GifSaveOptionsData.  # noqa: E501
        :rtype: int
        """
        return self._page_index

    @page_index.setter
    def page_index(self, page_index):
        """Sets the page_index of this GifSaveOptionsData.

        Gets or sets determines 0-based index of the first page to render.  # noqa: E501

        :param page_index: The page_index of this GifSaveOptionsData.  # noqa: E501
        :type: int
        """
        self._page_index = page_index
    @property
    def graphics_quality_options(self):
        """Gets the graphics_quality_options of this GifSaveOptionsData.  # noqa: E501

        Gets or sets allows to specify additional System.Drawing.Graphics quality options.  # noqa: E501

        :return: The graphics_quality_options of this GifSaveOptionsData.  # noqa: E501
        :rtype: GraphicsQualityOptionsData
        """
        return self._graphics_quality_options

    @graphics_quality_options.setter
    def graphics_quality_options(self, graphics_quality_options):
        """Sets the graphics_quality_options of this GifSaveOptionsData.

        Gets or sets allows to specify additional System.Drawing.Graphics quality options.  # noqa: E501

        :param graphics_quality_options: The graphics_quality_options of this GifSaveOptionsData.  # noqa: E501
        :type: GraphicsQualityOptionsData
        """
        self._graphics_quality_options = graphics_quality_options
    @property
    def horizontal_resolution(self):
        """Gets the horizontal_resolution of this GifSaveOptionsData.  # noqa: E501

        Gets or sets the horizontal resolution for the generated images, in dots per inch.  This property has effect only when saving to raster image formats. The default value is 96.  # noqa: E501

        :return: The horizontal_resolution of this GifSaveOptionsData.  # noqa: E501
        :rtype: float
        """
        return self._horizontal_resolution

    @horizontal_resolution.setter
    def horizontal_resolution(self, horizontal_resolution):
        """Sets the horizontal_resolution of this GifSaveOptionsData.

        Gets or sets the horizontal resolution for the generated images, in dots per inch.  This property has effect only when saving to raster image formats. The default value is 96.  # noqa: E501

        :param horizontal_resolution: The horizontal_resolution of this GifSaveOptionsData.  # noqa: E501
        :type: float
        """
        self._horizontal_resolution = horizontal_resolution
    @property
    def image_brightness(self):
        """Gets the image_brightness of this GifSaveOptionsData.  # noqa: E501

        Gets or sets brightness of image.  # noqa: E501

        :return: The image_brightness of this GifSaveOptionsData.  # noqa: E501
        :rtype: float
        """
        return self._image_brightness

    @image_brightness.setter
    def image_brightness(self, image_brightness):
        """Sets the image_brightness of this GifSaveOptionsData.

        Gets or sets brightness of image.  # noqa: E501

        :param image_brightness: The image_brightness of this GifSaveOptionsData.  # noqa: E501
        :type: float
        """
        self._image_brightness = image_brightness
    @property
    def image_color_mode(self):
        """Gets the image_color_mode of this GifSaveOptionsData.  # noqa: E501

        Gets or sets color mode of image.  # noqa: E501

        :return: The image_color_mode of this GifSaveOptionsData.  # noqa: E501
        :rtype: str
        """
        return self._image_color_mode

    @image_color_mode.setter
    def image_color_mode(self, image_color_mode):
        """Sets the image_color_mode of this GifSaveOptionsData.

        Gets or sets color mode of image.  # noqa: E501

        :param image_color_mode: The image_color_mode of this GifSaveOptionsData.  # noqa: E501
        :type: str
        """
        self._image_color_mode = image_color_mode
    @property
    def image_contrast(self):
        """Gets the image_contrast of this GifSaveOptionsData.  # noqa: E501

        Gets or sets contrast of image.  # noqa: E501

        :return: The image_contrast of this GifSaveOptionsData.  # noqa: E501
        :rtype: float
        """
        return self._image_contrast

    @image_contrast.setter
    def image_contrast(self, image_contrast):
        """Sets the image_contrast of this GifSaveOptionsData.

        Gets or sets contrast of image.  # noqa: E501

        :param image_contrast: The image_contrast of this GifSaveOptionsData.  # noqa: E501
        :type: float
        """
        self._image_contrast = image_contrast
    @property
    def paper_color(self):
        """Gets the paper_color of this GifSaveOptionsData.  # noqa: E501

        Gets or sets background (paper) color of image.  # noqa: E501

        :return: The paper_color of this GifSaveOptionsData.  # noqa: E501
        :rtype: str
        """
        return self._paper_color

    @paper_color.setter
    def paper_color(self, paper_color):
        """Sets the paper_color of this GifSaveOptionsData.

        Gets or sets background (paper) color of image.  # noqa: E501

        :param paper_color: The paper_color of this GifSaveOptionsData.  # noqa: E501
        :type: str
        """
        self._paper_color = paper_color
    @property
    def pixel_format(self):
        """Gets the pixel_format of this GifSaveOptionsData.  # noqa: E501

        Gets or sets pixel format of image.  # noqa: E501

        :return: The pixel_format of this GifSaveOptionsData.  # noqa: E501
        :rtype: str
        """
        return self._pixel_format

    @pixel_format.setter
    def pixel_format(self, pixel_format):
        """Sets the pixel_format of this GifSaveOptionsData.

        Gets or sets pixel format of image.  # noqa: E501

        :param pixel_format: The pixel_format of this GifSaveOptionsData.  # noqa: E501
        :type: str
        """
        self._pixel_format = pixel_format
    @property
    def resolution(self):
        """Gets the resolution of this GifSaveOptionsData.  # noqa: E501

        Gets or sets both horizontal and vertical resolution for the generated images, in dots per inch.  This property has effect only when saving to raster image formats. The default value is 96.  # noqa: E501

        :return: The resolution of this GifSaveOptionsData.  # noqa: E501
        :rtype: float
        """
        return self._resolution

    @resolution.setter
    def resolution(self, resolution):
        """Sets the resolution of this GifSaveOptionsData.

        Gets or sets both horizontal and vertical resolution for the generated images, in dots per inch.  This property has effect only when saving to raster image formats. The default value is 96.  # noqa: E501

        :param resolution: The resolution of this GifSaveOptionsData.  # noqa: E501
        :type: float
        """
        self._resolution = resolution
    @property
    def scale(self):
        """Gets the scale of this GifSaveOptionsData.  # noqa: E501

        Gets or sets zoom factor of image.  # noqa: E501

        :return: The scale of this GifSaveOptionsData.  # noqa: E501
        :rtype: float
        """
        return self._scale

    @scale.setter
    def scale(self, scale):
        """Sets the scale of this GifSaveOptionsData.

        Gets or sets zoom factor of image.  # noqa: E501

        :param scale: The scale of this GifSaveOptionsData.  # noqa: E501
        :type: float
        """
        self._scale = scale
    @property
    def use_anti_aliasing(self):
        """Gets the use_anti_aliasing of this GifSaveOptionsData.  # noqa: E501

        Gets or sets determine whether or not to use anti-aliasing for rendering.  # noqa: E501

        :return: The use_anti_aliasing of this GifSaveOptionsData.  # noqa: E501
        :rtype: bool
        """
        return self._use_anti_aliasing

    @use_anti_aliasing.setter
    def use_anti_aliasing(self, use_anti_aliasing):
        """Sets the use_anti_aliasing of this GifSaveOptionsData.

        Gets or sets determine whether or not to use anti-aliasing for rendering.  # noqa: E501

        :param use_anti_aliasing: The use_anti_aliasing of this GifSaveOptionsData.  # noqa: E501
        :type: bool
        """
        self._use_anti_aliasing = use_anti_aliasing
    @property
    def use_gdi_emf_renderer(self):
        """Gets the use_gdi_emf_renderer of this GifSaveOptionsData.  # noqa: E501

        Gets or sets a value determining whether to use GDI+ or Aspose.Words metafile renderer when saving to EMF.  # noqa: E501

        :return: The use_gdi_emf_renderer of this GifSaveOptionsData.  # noqa: E501
        :rtype: bool
        """
        return self._use_gdi_emf_renderer

    @use_gdi_emf_renderer.setter
    def use_gdi_emf_renderer(self, use_gdi_emf_renderer):
        """Sets the use_gdi_emf_renderer of this GifSaveOptionsData.

        Gets or sets a value determining whether to use GDI+ or Aspose.Words metafile renderer when saving to EMF.  # noqa: E501

        :param use_gdi_emf_renderer: The use_gdi_emf_renderer of this GifSaveOptionsData.  # noqa: E501
        :type: bool
        """
        self._use_gdi_emf_renderer = use_gdi_emf_renderer
    @property
    def use_high_quality_rendering(self):
        """Gets the use_high_quality_rendering of this GifSaveOptionsData.  # noqa: E501

        Gets or sets determine whether or not to use high quality (i.e. slow) rendering algorithms.  # noqa: E501

        :return: The use_high_quality_rendering of this GifSaveOptionsData.  # noqa: E501
        :rtype: bool
        """
        return self._use_high_quality_rendering

    @use_high_quality_rendering.setter
    def use_high_quality_rendering(self, use_high_quality_rendering):
        """Sets the use_high_quality_rendering of this GifSaveOptionsData.

        Gets or sets determine whether or not to use high quality (i.e. slow) rendering algorithms.  # noqa: E501

        :param use_high_quality_rendering: The use_high_quality_rendering of this GifSaveOptionsData.  # noqa: E501
        :type: bool
        """
        self._use_high_quality_rendering = use_high_quality_rendering
    @property
    def vertical_resolution(self):
        """Gets the vertical_resolution of this GifSaveOptionsData.  # noqa: E501

        Gets or sets the vertical resolution for the generated images, in dots per inch.  This property has effect only when saving to raster image formats. The default value is 96.  # noqa: E501

        :return: The vertical_resolution of this GifSaveOptionsData.  # noqa: E501
        :rtype: float
        """
        return self._vertical_resolution

    @vertical_resolution.setter
    def vertical_resolution(self, vertical_resolution):
        """Sets the vertical_resolution of this GifSaveOptionsData.

        Gets or sets the vertical resolution for the generated images, in dots per inch.  This property has effect only when saving to raster image formats. The default value is 96.  # noqa: E501

        :param vertical_resolution: The vertical_resolution of this GifSaveOptionsData.  # noqa: E501
        :type: float
        """
        self._vertical_resolution = vertical_resolution
    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, GifSaveOptionsData):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
