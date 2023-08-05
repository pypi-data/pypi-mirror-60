from ofxReaderBR.reader.OFXReaderController import OFXReaderController
from ofxReaderBR.reader.readerbankstatement import IReaderBankStatement, OFXReaderBankStatement
from ofxReaderBR.reader.readercashflow import IReaderCashFlow, OFXReaderCashFlow
from .ReaderAbstractFactory import ReaderAbstractFactory


class OFXReaderFactory(ReaderAbstractFactory):
    def createReaderController(self):
        return OFXReaderController()

    def createReaderBankStatement(self) -> IReaderBankStatement:
        return OFXReaderBankStatement()
    
    def createReaderCashFlow(self) -> IReaderCashFlow:
        return OFXReaderCashFlow()