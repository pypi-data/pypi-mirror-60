from typing import List

from .cashflow import CashFlow


class BankStatement(object):
    def __init__(self):
        self.inflows: List[CashFlow] = []
        self.outflows: List[CashFlow] = []

    def __repr__(self):
        bs = 'BankStatement:'
            
        bs += '\n\n\t = Inflows: = \n\t'
        for cs in self.inflows:
            bs += '\n' + str(cs)
        bs += '\n\n\t = Outflows: =\n\t'
        for cs in self.outflows:
            bs += '\n' + str(cs)
        return bs

    def __del__(self):
        self.inflows = None
        self.outflows = None

    def cashflows(self):
        return self.inflows + self.outflows

    def merge(self, other):
        self.inflows.append(other.inflows)
        self.outflows.append(other.outflows)


class BankStatementAdder:

    def add(self, bankStatement_1, bankStatement_2) -> BankStatement:
        bnk_stmt = BankStatement()

        bnk_stmts = []
        if isinstance(bankStatement_1, list):
            bnk_stmts.extend(bankStatement_1)
        else:
            bnk_stmts.append(bankStatement_1)

        if isinstance(bankStatement_2, list):
            bnk_stmts.extend(bankStatement_2)
        else:
            bnk_stmts.append(bankStatement_2)

        for bs in bnk_stmts:
            bnk_stmt.inflows.extend(bs.inflows)
            bnk_stmt.outflows.extend(bs.outflows)

        return bnk_stmt
