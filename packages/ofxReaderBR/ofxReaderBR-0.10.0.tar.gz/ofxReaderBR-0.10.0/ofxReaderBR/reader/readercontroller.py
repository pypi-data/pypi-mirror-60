import abc
import logging
from typing import List

from lxml import etree
from openpyxl import load_workbook

from ofxReaderBR.model import BankStatement
from ofxReaderBR.reader.pdf.PDFParserSantander import PDFParserSantander
from ofxReaderBR.reader.pdf.pdfParser import PDFParser

logger = logging.getLogger(__name__)


class BaseReaderController(abc.ABC):
    @abc.abstractmethod
    def _get_result(self, file, options):
        pass

    def _read(self, factory, files):
        logger.debug(files)

        bank_stmts = []
        for file in files:
            options = {}

            data = self._get_result(file, options)
            bs_reader = factory.create_reader_bank_statement(
                file, factory, data, options)

            try:
                bs = bs_reader.read()
            except (RuntimeError, ValueError) as err:
                bs = BankStatement(file)
                bs.read_status = BankStatement.ERROR
                logger.error(f'Error reading file {file}: {err}')

            bank_stmts.append(bs)

        return bank_stmts


class PDFReaderController(BaseReaderController):
    def read(self, factory, files=()) -> List[BankStatement]:
        return self._read(factory, files)

    def _get_result(self, file, options):
        try:
            parser = PDFParserSantander(file)
            result = parser.run()
            options['has_header'] = False
        except ValueError as err:
            logger.debug(err)
            parser = PDFParser()
            result = parser.run(file)
        return result


class XLSReaderController(BaseReaderController):
    def read(self, factory, files=()) -> List[BankStatement]:
        return self._read(factory, files)

    def _get_result(self, file, options):
        wb = load_workbook(file)
        return wb.active


class XMLReaderController(BaseReaderController):
    def read(self, factory, files=()):
        return self._read(factory, files)

    def _get_result(self, file, options):
        data = file.read().decode("latin-1")
        data = data[data.find('<OFX>'):]

        parser = etree.XMLParser(recover=True)
        tree = etree.fromstring(data, parser=parser)

        if tree.findall("CREDITCARDMSGSRSV1"):
            options['creditcard'] = True
        else:
            options['creditcard'] = False

        return tree
