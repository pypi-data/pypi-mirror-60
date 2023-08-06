from ofxReaderBR.reader.OFXReaderController import OFXReaderController
from ofxReaderBR.reader.readerbankstatement import OFXReaderBankStatement
from ofxReaderBR.reader.readercashflow import IReaderCashFlow, OFXReaderCashFlow
from .ReaderAbstractFactory import ReaderAbstractFactory


class OFXReaderFactory(ReaderAbstractFactory):
    def createReaderController(self):
        return OFXReaderController()

    def createReaderBankStatement(self, file, factory, data, options=None):
        return OFXReaderBankStatement(file, factory, data, options)

    def createReaderCashFlow(self) -> IReaderCashFlow:
        return OFXReaderCashFlow()
