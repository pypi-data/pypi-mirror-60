from .scrappers import ScrapeInlineData, ScrapeTableData, ScrapeHeadData
from .utils import PdfReader, PdfDataContainer


class PdfScrapper:
    pdf_reader = PdfReader()
    pdf_scrapper_inline_data = ScrapeInlineData()
    pdf_scrapper_table_data = ScrapeTableData()
    pdf_scrapper_head_data = ScrapeHeadData()

    def set_data(self, path: str) -> None:
        PdfDataContainer.pdf_path = path

        pdf_query_data = self.pdf_reader.read_pdf(path)

        if pdf_query_data:
            PdfDataContainer.pdfquery = pdf_query_data.get('pdf')
            PdfDataContainer.width = pdf_query_data.get('width')
            PdfDataContainer.height = pdf_query_data.get('height')
            PdfDataContainer.pages_count = self.pdf_reader.pages_count(PdfDataContainer.pdfquery)

    def set_inline_data(self, data: list) -> None:
        PdfDataContainer.inline_data_structure = data

    def set_table_data(self, data: list):
        PdfDataContainer.table_data_structure = data

    def set_invalid_fields_data(self, data: list):
        PdfDataContainer.invalid_fields = data

    def set_mail_data(self, email_to, email_from, password, port, host):
        PdfDataContainer.email_to = email_to
        PdfDataContainer.email_from = email_from
        PdfDataContainer.email_from_password = password
        PdfDataContainer.email_host = host
        PdfDataContainer.email_port = port

    def scrape_inline_data(self, page, schema):
        if PdfDataContainer.pdfquery is None:
            return

        self.set_inline_data(schema)
        return self.pdf_scrapper_inline_data.scrape(page)

    def scrape_table_data(self, page, schema):
        if PdfDataContainer.pdfquery is None:
            return

        self.set_table_data(schema)
        return self.pdf_scrapper_table_data.scrape(page)

    def set_logger(self, logger):
        PdfDataContainer.logger = logger

    def _validate_dict(self, data: dict):
        structure = {}
        for k, v in data.items():
            errors_line = ''
            for ivl_field in PdfDataContainer.invalid_fields:
                if ivl_field in v:
                    errors_line += f"contains {ivl_field}; "
            if errors_line:
                structure[k] = errors_line
        return structure

    def validate_scrapping_data(self, scrapping_data):
        errors = []

        for s in scrapping_data:
            data = scrapping_data[s]

            structure = {}
            if isinstance(data, dict):
                validation_res = self._validate_dict(data)
                if validation_res:
                    structure[s] = validation_res
            else:
                list_errors = []
                for d in data:
                    validation_res = self._validate_dict(d)
                    if validation_res:
                        list_errors.append(validation_res)
                if list_errors:
                    structure[s] = list_errors

            if structure:
                errors.append(structure)

        return errors

    def scrape_all_data(self, page=None) -> dict or None:
        if PdfDataContainer.pdfquery is None:
            return

        results = self.pdf_scrapper_head_data.scrape(page)

        scrapping_data = {}
        for res in results:
            scrapping_data.update(self.scrape_inline_data(
                page=res.get('page'),
                schema=res.get('inline')
            ))
            scrapping_data.update(self.scrape_table_data(
                page=res.get('page'),
                schema=res.get('table')
            ))

        PdfDataContainer.logger.log(10, {'Errors': self.validate_scrapping_data(scrapping_data)})

        return scrapping_data
