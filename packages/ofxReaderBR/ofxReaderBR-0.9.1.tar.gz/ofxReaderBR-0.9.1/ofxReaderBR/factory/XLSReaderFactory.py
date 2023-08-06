from ofxReaderBR.reader.readerbankstatement import XLSReaderBankStatement
from ofxReaderBR.reader.readercashflow import IReaderCashFlow, XLSReaderCashFlow
from ofxReaderBR.reader.readercontroller import XLSReaderController
from .ReaderAbstractFactory import ReaderAbstractFactory


class XLSReaderFactory(ReaderAbstractFactory):
    def createReaderController(self):
        return XLSReaderController()

    def createReaderBankStatement(self, file, factory, data, options=None):
        return XLSReaderBankStatement(file, factory, data, options)

    def createReaderCashFlow(self) -> IReaderCashFlow:
        return XLSReaderCashFlow()
