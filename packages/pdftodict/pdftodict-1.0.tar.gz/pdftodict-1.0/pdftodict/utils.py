import abc
import pdfquery
import smtplib

from pdfminer.layout import LTRect


class BaseScrapeData(abc.ABC):
    border = 10
    scrapping_structure_name = ''

    @property
    def pdf(self):
        return PdfDataContainer.pdfquery

    @property
    def width(self):
        return PdfDataContainer.width

    @property
    def height(self):
        return PdfDataContainer.height

    @property
    def scrapping_structure(self):
        return getattr(PdfDataContainer, self.scrapping_structure_name)

    @property
    def logger(self):
        return PdfDataContainer.logger

    def items_by_page_bbox(self, page, bbox):
        return self.pdf.pq(
            'LTPage[pageid="{}"] :in_bbox("{}, {}, {}, {}")'.format(page, *bbox)
        )

    @abc.abstractmethod
    def scrape(self, page):
        pass


class PdfReader:
    def _pdf_valid_structure(self, pdf, width, height) -> bool:
        bbox = [0, 0, width, height]
        page = 1

        main_bbox = pdf.pq(
            'LTPage[pageid="{}"] :in_bbox("{}, {}, {}, {}")'.format(page, *bbox)
        )

        datas = []
        max_length = 0
        for m in main_bbox:
            if isinstance(m.layout, LTRect):
                if float(m.attrib.get('width')) > max_length:
                    datas = [m]
                    max_length = float(m.attrib.get('width'))
                elif float(m.attrib.get('width')) == max_length:
                    datas.append(m)
        return len(datas) > 0 and max_length > width * 0.7

    def _send_info_mail(self, path):
        if PdfDataContainer.email_from is '':
            return

        PdfDataContainer.logger.log(10, f'Sending mail to {PdfDataContainer.email_to}...')

        server = smtplib.SMTP_SSL(PdfDataContainer.email_host, PdfDataContainer.email_port)
        server.login(PdfDataContainer.email_from, PdfDataContainer.email_from_password)

        msg = f"PDF {path} is invalid!"

        server.sendmail(PdfDataContainer.email_from, PdfDataContainer.email_to, msg)

    def read_pdf(self, path: str) -> dict or None:
        pdf = self.get_pdfquery(path)
        if pdf is None:
            return

        width = self.get_width_from_pdfquery(pdf)
        height = self.get_height_from_pdfquery(pdf)

        if not self._pdf_valid_structure(pdf, width, height):
            PdfDataContainer.logger.log(30, f'Structure for {path} is invalid!')
            self._send_info_mail(path)
            return

        return {
            'pdf': pdf,
            'width': width,
            'height': height
        }

    def pages_count(self, pdf):
        return pdf.doc.catalog['Pages'].resolve()['Count']

    def get_width_by_pdf_path(self, path: str):
        pdf = self.get_pdfquery(path)

        return self.get_width_from_pdfquery(pdf)

    def get_height_by_pdf_path(self, path: str):
        pdf = self.get_pdfquery(path)

        return self.get_height_from_pdfquery(pdf)

    def _get_first_page_from_pdquery(self, pdf):
        return pdf.pq('LTPage[pageid="1"]')

    def get_width_from_pdfquery(self, pdfquery):
        first_page = self._get_first_page_from_pdquery(pdfquery)

        return float(first_page.attr('width'))

    def get_height_from_pdfquery(self, pdfquery):
        first_page = self._get_first_page_from_pdquery(pdfquery)

        return float(first_page.attr('height'))

    def get_pdfquery(self, path):
        PdfDataContainer.logger.log(level=10, msg='Reading pdf...')
        try:
            pdf = pdfquery.PDFQuery(path)
            pdf.load()

            return pdf
        except FileNotFoundError:
            PdfDataContainer.logger.log(level=10, msg='File was not found!')
            return


class PdfDataContainer:
    pdfquery = None
    width = None
    height = None
    pdf_path = ''
    pages_count = 1

    inline_data_structure = []
    table_data_structure = []

    invalid_fields = []

    email_to = ''
    email_from = ''
    email_port = 587
    email_from_password = ''
    email_host = ''

    logger = type('obj', (object, ), {'log': lambda level, msg: print(msg)})
