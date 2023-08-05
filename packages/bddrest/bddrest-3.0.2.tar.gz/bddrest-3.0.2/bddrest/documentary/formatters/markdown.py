from .base import Formatter


class MarkdownFormatter(Formatter):
    def _writeline(self, text=''):
        self.write(f'{text}\n')

    def write_header(self, text, level=1):
        self._writeline(f'{"#" * level} {text}\n')

    def write_paragraph(self, text):
        self._writeline(text)
        self._writeline()

    def _write_table_row(self, row):
        self._writeline(' | '.join(str(i) for i in row))

    def write_table(self, array2d, headers=None):
        if not isinstance(array2d, list):
            array2d = list(array2d)

        columns = len(array2d[0])
        if headers:
            self._write_table_row(headers)
        self._writeline(' | '.join(['---'] * columns))
        for row in array2d:
            self._write_table_row(row)

        self._writeline()

    def write_list(self, listkind):
        for l in listkind:
            self._writeline(f'* {l}')
        self._writeline()

