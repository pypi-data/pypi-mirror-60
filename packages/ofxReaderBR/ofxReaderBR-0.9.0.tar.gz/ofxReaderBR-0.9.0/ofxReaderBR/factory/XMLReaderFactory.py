from ofxReaderBR.reader.readerbankstatement import XMLReaderBankStatement
from ofxReaderBR.reader.readercashflow import IReaderCashFlow, XMLReaderCashFlow
from ofxReaderBR.reader.readercontroller import XMLReaderController
from .ReaderAbstractFactory import ReaderAbstractFactory


class XMLReaderFactory(ReaderAbstractFactory):
    def createReaderController(self):
        return XMLReaderController()

    def createReaderBankStatement(self, file, factory, data, options=None):
        return XMLReaderBankStatement(file, factory, data, options)

    def createReaderCashFlow(self) -> IReaderCashFlow:
        return XMLReaderCashFlow()
