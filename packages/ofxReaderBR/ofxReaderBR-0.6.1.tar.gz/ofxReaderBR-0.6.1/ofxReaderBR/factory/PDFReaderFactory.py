from ofxReaderBR.reader.readerbankstatement import IReaderBankStatement, PDFReaderBankStatement
from ofxReaderBR.reader.readercashflow import IReaderCashFlow, PDFReaderCashFlow
from ofxReaderBR.reader.readercontroller import PDFReaderController
from .ReaderAbstractFactory import ReaderAbstractFactory


class PDFReaderFactory(ReaderAbstractFactory):
    def createReaderController(self):
        return PDFReaderController()

    def createReaderBankStatement(self) -> IReaderBankStatement:
        return PDFReaderBankStatement()
    
    def createReaderCashFlow(self) -> IReaderCashFlow:
        return PDFReaderCashFlow()