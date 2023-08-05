from pdfminer.layout import LTRect, LTLine, LTTextBoxHorizontal, LTTextLineHorizontal, LTFigure

from .utils import BaseScrapeData, PdfDataContainer


class ScrapeInlineData(BaseScrapeData):
    scrapping_structure_name = 'inline_data_structure'

    def replace_duplicates(self, value, dict_data):
        if value not in dict_data:
            return value

        number = 2
        while f"{value} {number}" in dict_data:
            number += 1

        return f"{value} {number}"

    def scrape(self, page):

        self.logger.log(10, 'Scrape inline data...')
        inline_result = {}

        for attr in self.scrapping_structure:
            data = self.pdf.pq(
                'LTPage[pageid="{}"] :contains("{}")'.format(page, attr)
            )[0]

            data_bbox = list(data.layout.bbox)
            data_bbox[3] = data_bbox[1]
            data_bbox[0] -= self.border
            data_bbox[2] += self.border

            labels = []
            closing_rect = None
            while closing_rect is None and data_bbox[1] > self.border:
                data_bbox[1] -= self.border
                data_bbox_d = self.items_by_page_bbox(page, data_bbox)

                for d in data_bbox_d:
                    if isinstance(d.layout, LTRect):
                        closing_rect = d
                        break
            if closing_rect is not None:
                data_bbox[1] = float(closing_rect.attrib.get('y1'))

            for d in self.items_by_page_bbox(page, data_bbox):
                if isinstance(d.layout, LTTextBoxHorizontal):
                    if d not in labels and float(d.attrib.get('x0')) <= data_bbox[0] + self.border * 1.5:
                        labels.append(d)

            labels = sorted(
                labels,
                key=lambda v: float(v.attrib.get('y0')),
                reverse=True
            )

            result = {}
            for i, l in enumerate(labels):
                if i + 1 >= len(labels):
                    end_y = data_bbox[1]
                    if end_y <= self.border:
                        end_y = 54
                else:
                    end_y = float(labels[i + 1].attrib.get('y1'))

                value = self.scrape_line_data(page, l, end_y)

                result[self.replace_duplicates(l.layout.get_text().strip(), result)] = value

            inline_result[self.replace_duplicates(attr, inline_result)] = result

        return inline_result

    def scrape_line_data(self, page, element, end_y) -> str or None:
        str_result_data = ''
        bbox = list(element.layout.bbox)

        bbox[0] = bbox[2] + self.border
        bbox[1] = end_y - self.border
        bbox[2] = PdfDataContainer.width
        bbox[3] += self.border

        bbox_d = self.items_by_page_bbox(page, bbox)

        for b in bbox_d:
            if isinstance(b.layout, LTFigure):
                str_result_data = not b.layout.is_empty()
                break
            try:
                tempo_value = b.layout.get_text().strip()
                if tempo_value not in str_result_data and tempo_value is not ':':
                    str_result_data += tempo_value
            except AttributeError:
                continue

        try:
            if str_result_data:
                if str_result_data[0] == ':':
                    str_result_data = str_result_data[1:].strip()
        except TypeError:
            pass

        return str_result_data


class ScrapeTableData(BaseScrapeData):
    scrapping_structure_name = 'table_data_structure'

    def x0_from_element(self, element):
        return float(element[0].attrib.get('x0'))

    def group_headers_by_x0(self, headers):
        grouped_headers = []
        sorted_headers = sorted(
            headers,
            key=self.x0_from_element,
            reverse=False
        )

        group = []
        for h in sorted_headers:
            if group:
                if self.x0_from_element(h) == self.x0_from_element(group[0]):
                    group.append(h)
                else:
                    grouped_headers.append(group)
                    group = [h]
            else:
                group = [h]
        if group:
            grouped_headers.append(group)

        return grouped_headers

    def table_headers(self, page, attr_name):
        attr_main_bbox = self.pdf.pq(
            'LTPage[pageid="{}"] :contains("{}")'.format(page, attr_name)
        ).items()

        attr_main_bbox = [x for x in attr_main_bbox]
        attr_main_bbox = attr_main_bbox[0][0].layout.bbox
        table_name_len = attr_main_bbox[2] - attr_main_bbox[0]

        attr_main_bbox = list(attr_main_bbox)
        attr_main_bbox[3] = attr_main_bbox[1]
        attr_main_bbox[0] -= self.border
        attr_main_bbox[2] += self.border

        headers = []
        headers_collected = False
        while not headers_collected and attr_main_bbox[1] > self.border:
            attr_main_bbox[1] -= 10
            attrs_b = self.items_by_page_bbox(page, attr_main_bbox).items()
            attrs_b = [x[0] for x in attrs_b]

            headers = list(set(filter(lambda x: isinstance(x.layout, LTRect), attrs_b)))

            if attrs_b:
                headers_collected = isinstance(attrs_b[-1].layout, LTLine) and len(headers) > 0

            filtered_headers = []
            for h in headers:
                last_header_len = h.layout.bbox
                last_header_len = last_header_len[2] - last_header_len[0]

                if last_header_len > (table_name_len - self.border):
                    headers_collected = True
                    headers = filtered_headers
                else:
                    filtered_headers.append(h)

        return self.group_headers_by_x0(list(headers))

    def column_value_by_bbox_data(self, bbox_data):
        data = ''
        for d in bbox_data:
            try:
                if d.layout.get_text().strip() not in data:
                    data += d.layout.get_text().strip() + ' '
            except AttributeError:
                continue

        return data.strip()

    def column_value_by_bbox(self, page, column_bbox, last_line_pos, table_end_pos):
        column_bbox[3] = column_bbox[1] = last_line_pos

        column_data_founded = False
        column_value = ''

        while not column_data_founded and column_bbox[1] > table_end_pos and column_bbox[1] > self.border:
            column_bbox[1] -= self.border
            column_bbox_data = self.items_by_page_bbox(page, column_bbox)

            if len(column_bbox_data) > 0:
                if isinstance(column_bbox_data[0].layout, LTLine):
                    while isinstance(column_bbox_data[0].layout, LTLine):
                        if column_bbox[2] + self.border < PdfDataContainer.width:
                            column_bbox[2] += self.border

                        if column_bbox[0] - self.border > 0:
                            column_bbox[0] -= self.border

                        column_bbox_data = self.items_by_page_bbox(page, column_bbox)

                if isinstance(column_bbox_data[0].layout, LTTextBoxHorizontal):
                    column_value = self.column_value_by_bbox_data(column_bbox_data)
                    column_data_founded = True
                elif isinstance(column_bbox_data[0].layout, LTTextLineHorizontal):
                    if len(column_bbox_data.children()) > 0:
                        if isinstance(column_bbox_data.children()[0].layout, LTTextBoxHorizontal):
                            column_value = self.column_value_by_bbox_data(column_bbox_data)
                            column_data_founded = True

        return column_value

    def scrape(self, page):
        self.logger.log(10, 'Processing table datas...')
        scrape_result = {}

        for attr_name in self.scrapping_structure:
            headers = self.table_headers(page, attr_name)

            end_table_bbox = [
                float(headers[0][-1].attrib.get('x0')) - self.border,
                float(headers[0][-1].attrib.get('y0')) - self.border,
                float(headers[-1][-1].attrib.get('x1')) + self.border,
                float(headers[0][-1].attrib.get('y0')) - self.border,
            ]

            end_table_pos = 54

            while end_table_bbox[1] > self.border and end_table_pos == 54:
                end_table_bbox[1] -= self.border
                end_table_bbox_data = self.items_by_page_bbox(page, end_table_bbox)

                for d in end_table_bbox_data:
                    if isinstance(d.layout, LTRect) and d not in headers:
                        end_table_pos = float(d.attrib.get('y1'))
                        break
            data = []
            last_line_pos = headers[0][-1].layout.bbox[1]
            lowest_pos = last_line_pos

            while last_line_pos > end_table_pos + self.border / 2:
                data_dict = {}
                for header_group in headers:
                    tempo_last_line = last_line_pos
                    for sub_header in header_group:
                        header_name = sub_header[0].layout.get_text().strip()
                        column_bbox = list(sub_header.layout.bbox)
                        column_value = self.column_value_by_bbox(
                            page=page,
                            column_bbox=column_bbox,
                            last_line_pos=tempo_last_line,
                            table_end_pos=end_table_pos
                        )

                        data_dict[header_name] = column_value

                        if lowest_pos > column_bbox[1]:
                            lowest_pos = column_bbox[1]

                        tempo_last_line = column_bbox[1]

                last_line_pos = lowest_pos + self.border

                empty_length = 0
                for k, v in data_dict.items():
                    if not v:
                        empty_length += 1

                len_headers = 0
                for h in headers:
                    len_headers += len(h)

                if empty_length == len_headers or last_line_pos <= self.border:
                    break

                data.append(data_dict)

            scrape_result[attr_name] = data

        return scrape_result


class ScrapeHeadData(BaseScrapeData):
    def check_rect_down(self, page, element) -> bool:
        bbox = list(element.layout.bbox)
        bbox[0] -= self.border
        bbox[2] += self.border
        bbox[3] = bbox[1]

        while bbox[1] > self.border:

            bbox[1] -= self.border
            bbox_data = self.items_by_page_bbox(page, bbox)
            for d in bbox_data:
                if isinstance(d.layout, LTRect):
                    if float(d.attrib.get('width')) >= float(element.attrib.get('width')) - self.border:
                        return False
                    else:
                        return True
        return False

    def scrape(self, page=None):
        if page:
            pages = [page]
        else:
            pages = range(PdfDataContainer.pages_count)

        results = []

        for p in pages:
            table_datas = []
            inline_datas = []
            bbox = [0, 0, PdfDataContainer.width, PdfDataContainer.height]
            main_bbox = self.items_by_page_bbox(p, bbox)

            datas = []
            max_length = 0
            for m in main_bbox:
                if isinstance(m.layout, LTRect):
                    if float(m.attrib.get('width')) > max_length:
                        datas = [m]
                        max_length = float(m.attrib.get('width'))
                    elif float(m.attrib.get('width')) == max_length:
                        datas.append(m)

            for d in datas:
                if self.check_rect_down(p, d):
                    table_datas.append(d)
                else:
                    inline_datas.append(d)

            results.append(
                {
                    'page': p,
                    'inline': [x[0].layout.get_text().strip() for x in inline_datas],
                    'table': [x[0].layout.get_text().strip() for x in table_datas]
                }
            )

        return results
