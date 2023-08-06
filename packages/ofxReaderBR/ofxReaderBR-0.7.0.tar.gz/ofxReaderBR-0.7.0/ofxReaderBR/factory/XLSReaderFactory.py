from ofxReaderBR.reader.readerbankstatement import IReaderBankStatement, XLSReaderBankStatement
from ofxReaderBR.reader.readercashflow import IReaderCashFlow, XLSReaderCashFlow
from ofxReaderBR.reader.readercontroller import XLSReaderController
from .ReaderAbstractFactory import ReaderAbstractFactory


class XLSReaderFactory(ReaderAbstractFactory):
    def createReaderController(self):
        return XLSReaderController()

    def createReaderBankStatement(self) -> IReaderBankStatement:
        return XLSReaderBankStatement()
    
    def createReaderCashFlow(self) -> IReaderCashFlow:
        return XLSReaderCashFlow()