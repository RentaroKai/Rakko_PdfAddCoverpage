from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
import io
import math

class PDFHandler:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.reader = PdfReader(pdf_path)
        self.writer = PdfWriter()
    
    def get_max_page_size(self):
        max_width = 0
        max_height = 0
        for page in self.reader.pages:
            width = page.mediabox.width
            height = page.mediabox.height
            max_width = max(max_width, width)
            max_height = max(max_height, height)
        return math.ceil(float(max_width)), math.ceil(float(max_height))
    
    def add_covers(self, front_image, back_image):
        # Convert images to PDF pages
        front_pdf = self.image_to_pdf(front_image)
        back_pdf = self.image_to_pdf(back_image)
        
        # Add front cover
        self.writer.add_page(PdfReader(front_pdf).pages[0])
        
        # Add original PDF pages
        for page in self.reader.pages:
            self.writer.add_page(page)
        
        # Add back cover
        self.writer.add_page(PdfReader(back_pdf).pages[0])
        
        return self.writer
    
    def image_to_pdf(self, image):
        pdf_bytes = io.BytesIO()
        image.save(pdf_bytes, format="PDF")
        pdf_bytes.seek(0)
        return pdf_bytes

    def save(self, output_path):
        with open(output_path, 'wb') as output_file:
            self.writer.write(output_file)