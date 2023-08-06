from abc import abstractmethod, ABC

from ofxReaderBR.reader.OFXReaderController import OFXReaderController
from ofxReaderBR.reader.readerbankstatement import (PDFReaderBankStatement,
                                                    XLSReaderBankStatement,
                                                    XMLReaderBankStatement,
                                                    OFXReaderBankStatement)
from ofxReaderBR.reader.readercashflow import (PDFReaderCashFlow,
                                               XLSReaderCashFlow,
                                               XMLReaderCashFlow,
                                               OFXReaderCashFlow)
from ofxReaderBR.reader.readercontroller import PDFReaderController, XLSReaderController, XMLReaderController


class AbstractReaderFactory(ABC):

    @abstractmethod
    def create_reader_controller(self):
        pass

    @abstractmethod
    def create_reader_bank_statement(self, file, factory, data, options=None):
        pass

    @abstractmethod
    def create_reader_cash_flow(self):
        pass


class OFXReaderFactory(AbstractReaderFactory):

    def create_reader_controller(self):
        return OFXReaderController()

    def create_reader_bank_statement(self, file, factory, data, options=None):
        return OFXReaderBankStatement(file, factory, data, options)

    def create_reader_cash_flow(self):
        return OFXReaderCashFlow()

    @staticmethod
    def create_xml_factory():
        return XMLReaderFactory()


class PDFReaderFactory(AbstractReaderFactory):

    def create_reader_controller(self):
        return PDFReaderController()

    def create_reader_bank_statement(self, file, factory, data, options=None):
        return PDFReaderBankStatement(file, factory, data, options)

    def create_reader_cash_flow(self):
        return PDFReaderCashFlow()


class XLSReaderFactory(AbstractReaderFactory):

    def create_reader_controller(self):
        return XLSReaderController()

    def create_reader_bank_statement(self, file, factory, data, options=None):
        return XLSReaderBankStatement(file, factory, data, options)

    def create_reader_cash_flow(self):
        return XLSReaderCashFlow()


class XMLReaderFactory(AbstractReaderFactory):

    def create_reader_controller(self):
        return XMLReaderController()

    def create_reader_bank_statement(self, file, factory, data, options=None):
        return XMLReaderBankStatement(file, factory, data, options)

    def create_reader_cash_flow(self):
        return XMLReaderCashFlow()
