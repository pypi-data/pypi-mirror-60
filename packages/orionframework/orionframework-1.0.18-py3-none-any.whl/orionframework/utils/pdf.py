import PyPDF2
import textract
from django.core.files import File


def get_text(file_path):
    """
    Extract text for all pages of the given PDF document
    """
    if isinstance(file_path, File):
        f = file_path.open('rb')
        file_path = f.name
    elif isinstance(file_path, str, ):
        f = open(file_path, 'rb')
    else:
        f = file_path

    pdf = PyPDF2.PdfFileReader(f)

    num_pages = pdf.numPages
    count = 0
    text = ""

    while count < num_pages:
        page = pdf.getPage(count)
        count += 1
        text += page.extractText()

    if text == "":
        text = textract.process(file_path, method='tesseract', language='eng').decode("UTF-8")

    return text
