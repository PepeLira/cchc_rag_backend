import logging
from pathlib import Path
from io import BytesIO
from typing import TYPE_CHECKING, Iterable, List, Optional, Union

from docling_core.types.doc import ImageRefMode
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.backend.docling_parse_v2_backend import DoclingParseV2DocumentBackend

if TYPE_CHECKING:
    from docling.datamodel.document import InputDocument

_log = logging.getLogger(__name__)

IMAGE_RESOLUTION_SCALE = 2.0


class DoclingIntegration:

    def __init__(self, images_scale=IMAGE_RESOLUTION_SCALE, generate_picture_images=True):
        self.images_scale = images_scale
        self.generate_picture_images = generate_picture_images
        self.doc_converter = self._initialize_converter()

    def _initialize_converter(self) -> DocumentConverter:
        # Set up any pipeline options
        pipeline_options = PdfPipelineOptions()
        pipeline_options.images_scale = self.images_scale
        pipeline_options.generate_picture_images = self.generate_picture_images

        format_options = {
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
        return DocumentConverter(format_options=format_options)

    def parse_pdf(self, input_pdf_path: Path, output_dir: Path) -> Path:
        conv_res = self.doc_converter.convert(input_pdf_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        doc_filename = conv_res.input.file.stem
        html_filename = output_dir / f"{doc_filename}.html"

        # Save HTML with externally referenced pictures
        conv_res.document.save_as_html(html_filename, image_mode=ImageRefMode.REFERENCED)

        return conv_res, html_filename
    
    def get_page_count(self, path_or_stream: Union[BytesIO, Path]) -> int:
        doc_backend = DoclingParseV2DocumentBackend(in_doc=None, path_or_stream=path_or_stream)
        return doc_backend.get_page_count()

