import PyPDF2
import pypandoc


class DocExtract:
    def pdf_to_string(self, path):
        # Open the PDF file in read-binary mode
        with open(path, "rb") as file:
            # Create a PDF object
            pdf = PyPDF2.PdfReader(file)

            # Extract the text from each page of the PDF
            text = ""
            for page in range(len(pdf.pages)):
                print(pdf.pages[page])
                text += pdf.pages[page].extract_text()
            print(text)
        return text

    def docx_to_string(self, path):
        pypandoc.download_pandoc()
        # Set the path to the Word document
        doc_path = "./Research Assignment.docx"

        # Use pypandoc to convert the Word document to a text file
        output = pypandoc.convert_file(doc_path, "plain", outputfile="./resume transcription/lecture.txt")



