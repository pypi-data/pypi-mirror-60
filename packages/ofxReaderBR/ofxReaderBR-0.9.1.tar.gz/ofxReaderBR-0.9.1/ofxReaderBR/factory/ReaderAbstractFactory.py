import abc

from ofxReaderBR.reader.readercashflow import IReaderCashFlow


class ReaderAbstractFactory(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def createReaderBankStatement(self, file, factory, data, options=None):
        pass

    @abc.abstractmethod
    def createReaderCashFlow(self) -> IReaderCashFlow:
        pass
