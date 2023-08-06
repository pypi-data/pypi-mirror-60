from ofxReaderBR.reader.readerbankstatement import PDFReaderBankStatement
from ofxReaderBR.reader.readercashflow import IReaderCashFlow, PDFReaderCashFlow
from ofxReaderBR.reader.readercontroller import PDFReaderController
from .ReaderAbstractFactory import ReaderAbstractFactory


class PDFReaderFactory(ReaderAbstractFactory):
    def createReaderController(self):
        return PDFReaderController()

    def createReaderBankStatement(self, file, factory, data, options=None):
        return PDFReaderBankStatement(file, factory, data, options)

    def createReaderCashFlow(self) -> IReaderCashFlow:
        return PDFReaderCashFlow()
