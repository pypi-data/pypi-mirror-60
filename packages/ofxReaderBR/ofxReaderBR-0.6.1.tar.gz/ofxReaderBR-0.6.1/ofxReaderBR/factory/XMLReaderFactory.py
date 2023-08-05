from ofxReaderBR.reader.readerbankstatement import IReaderBankStatement, XMLReaderBankStatement
from ofxReaderBR.reader.readercashflow import IReaderCashFlow, XMLReaderCashFlow
from ofxReaderBR.reader.readercontroller import XMLReaderController
from .ReaderAbstractFactory import ReaderAbstractFactory


class XMLReaderFactory(ReaderAbstractFactory):
    def createReaderController(self):
        return XMLReaderController()

    def createReaderBankStatement(self) -> IReaderBankStatement:
        return XMLReaderBankStatement()
    
    def createReaderCashFlow(self) -> IReaderCashFlow:
        return XMLReaderCashFlow()