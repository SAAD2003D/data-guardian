import os
from xhtml2pdf import pisa # import pisa function from xhtml2pdf
# No need for HTML or CSS from weasyprint, or FontConfiguration

class PDFReporter:
    def __init__(self, dataset_profile, html_reporter_instance=None):
        self.profile = dataset_profile
        if html_reporter_instance:
            self.html_reporter = html_reporter_instance
        else:
            from .html_reporter import HTMLReporter # Local import to avoid circular issues
            self.html_reporter = HTMLReporter(self.profile)

    def _convert_html_to_pdf(self, source_html_string, output_path):
        """
        Converts an HTML string to a PDF file using xhtml2pdf.
        """
        result_file = None
        try:
            result_file = open(output_path, "w+b") # Open file in write binary mode

            # pisa.CreatePDF() returns a pisaStatus object which is True on success
            pisa_status = pisa.CreatePDF(
                src=source_html_string,  # HTML string content
                dest=result_file         # File handle to write PDF
            )
            
            if pisa_status.err:
                print(f"xhtml2pdf error: {pisa_status.err}")
                return False
            return True
        except Exception as e:
            print(f"An error occurred during PDF conversion with xhtml2pdf: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            if result_file:
                result_file.close()


    def generate_pdf_report(self, output_path="data_quality_report.pdf"):
        """
        Generates an HTML report in memory and then converts it to PDF using xhtml2pdf.
        """
        print(f"Generating PDF report for {self.profile.name} using xhtml2pdf...")
        if self.profile.raw_data is None:
            print("Error: Dataset not loaded. Cannot generate PDF report.")
            return False

        try:
            # Generate HTML content string using our existing HTMLReporter
            html_content_string = self.html_reporter.generate_html()
            
            if "<p>Error:" in html_content_string: # Basic check for error in HTML generation
                print("Error during HTML generation step for PDF.")
                return False

            # Convert the HTML string to PDF
            if self._convert_html_to_pdf(html_content_string, output_path):
                print(f"PDF report successfully saved to: {output_path}")
                return True
            else:
                print(f"Failed to generate PDF report with xhtml2pdf.")
                return False
                
        except Exception as e:
            print(f"An unexpected error occurred while orchestrating PDF generation: {e}")
            import traceback
            traceback.print_exc()
            return False