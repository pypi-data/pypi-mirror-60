# Structjour -- a daily trade review helper
# Copyright (C) 2019 Zero Substance Trading
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

'''
@author: Mike Petersen

@creation_date: 2019-07-10

Test methods in the class ibstatementdb.StatementDB.  Need to yet devise tests for
processStatement and refigureAPL (Still sketchy).
'''

import os
import sqlite3
import unittest

import pandas as pd

from PyQt5.QtCore import QSettings

from structjour.colz.finreqcol import FinReqCol
from structjour.definetrades import DefineTrades
from structjour.dfutil import DataFrameUtil
from structjour.statements import findfiles as ff
from structjour.statements.ibstatementdb import StatementDB
from structjour.statements.ibstatement import IbStatement
from structjour.thetradeobject import runSummaries
from structjour.view.layoutforms import LayoutForms

from structjour.colz.finreqcol import FinReqCol
# pylint: disable = C0103

class Test_StatementDB(unittest.TestCase):
    '''
    Test functions and methods in the ibstatementdb module
    '''
    def __init__(self, *args, **kwargs):
        super(Test_StatementDB, self).__init__(*args, **kwargs)
        self.settings = QSettings('zero_substance', 'structjour')

        
        self.db = "testdb.db"
        jdir = self.settings.value('journal')

        self.fulldb = os.path.join(jdir, self.db)

    def setUp(self):
        
        ddiirr = os.path.dirname(__file__)
        os.chdir(os.path.realpath(ddiirr))
        os.chdir(os.path.realpath('../'))

    def test_addTradeSummaries(self):
        '''
        Tests addTradeSummaries
        ''' 
        ibdb = StatementDB(self.db)
        self.clearTables()
        ibs, x = self.openStuff()
        # ibdb.getUncoveredDays
        covered = ibdb.getCoveredDays()
    
        rc = FinReqCol()
        for count, day in enumerate(covered):
            df = ibdb.getStatement(day)
            if not df.empty:
                tu = DefineTrades("DB")
                dframe, ldf = tu.processDBTrades(df)
                tradeSummaries, ts, entries, initialImageNames = runSummaries(ldf)
                ibdb.addTradeSummaries(tradeSummaries, ldf)
                summaries = ibdb.findTradeSummariesByDay(day)
                for summary in summaries:
                    summary = ibdb.makeTradeSumDict(summary)
                    entryTrades = ibdb.getEntryTrades(summary['id'])
                    self.assertGreater(len(entryTrades), 0)


                break

        # getNumTicketsforDay
                

    def test_findTrade(self):
        rc = FinReqCol()
        
        ibdb = StatementDB(self.db)
        row = {
            rc.ticker:  'SNRK',
            "DateTime": '20191212;093145',
            rc.shares: 3000,
            rc.price: 150.23,
            rc.comm: None,
            rc.oc: 'O',
            rc.acct: "U2229999",
            rc.bal: 3000,
            rc.avg: 150.23,
            rc.PL: None,
            "DAS": 'DAS',
            "IB": None}
        data = list(row.values())
        columns = list(row.keys())
        x = pd.DataFrame(data=[data], columns=columns)
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        ibdb.insertTrade(x.iloc[0], cur)
        conn.commit()
        foundit = ibdb.findTrade(x.iloc[0]['DateTime'], x.iloc[0][rc.ticker], x.iloc[0][rc.shares], x.iloc[0][rc.acct])
        self.assertTrue(foundit)

    def test_find_Trade(self):
        pass
    
    def test_insertPositions(self):
        pass
    
    def test_getNumTicketsForDay(self):
        pass

    def test_StatementDB(self):
        '''Test table creation'''
        StatementDB(self.fulldb)
        conn = sqlite3.connect(self.fulldb)
        cur = conn.cursor()
        x = cur.execute('''SELECT name FROM sqlite_master WHERE type='table'; ''')
        x = x.fetchall()
        tabnames = ['chart', 'holidays', 'ib_covered', 'ib_trades', 'ib_positions', 'trade_sum']
        self.assertTrue(set(tabnames).issubset(set([y[0] for y in x])))

    def clearTables(self):
        conn = sqlite3.connect(self.fulldb)
        cur = conn.cursor()
        cur.execute('''delete from chart''')
        # cur.execute('''delete from holidays''')
        cur.execute('''delete from ib_covered''')
        cur.execute('''delete from ib_trades''')
        cur.execute('''delete from ib_positions''')
        cur.execute('''delete from trade_sum''')
        conn.commit()


    def test_insertTrade(self):
        '''
        Test the method insertTrade. Verifys that it inserts a trade and then, with an
        identical trade, it does not insert the trade. The col DateTime requires fxn.
        '''
        rc = FinReqCol()
        row = dict()
        row[rc.ticker] = 'AAPL'
        row['DateTime'] = '20190101;123045'
        row[rc.shares] = 450
        row[rc.price] = 205.43
        row[rc.comm] = .75
        row[rc.oc] = 'O'
        row[rc.acct] = 'U1234567'
        row[rc.bal] = 450
        row[rc.avg] = 205.43
        row[rc.PL] = 0

        ibdb = StatementDB(self.db)

        self.clearTables()
        conn = sqlite3.connect(self.fulldb)
        cur = conn.cursor()
        ibdb.insertTrade(row, cur)
        conn.commit()

        x = cur.execute('''SELECT count() from ib_trades ''')
        x = x.fetchone()
        
        self.assertEqual(x[0], 1)
            
        ibdb.insertTrade(row, cur)
        conn.commit()
        x = cur.execute('''SELECT count() from ib_trades ''')
        x = x.fetchone()
        self.assertEqual(x[0], 1)
        self.clearTables()

    def openStuff(self, allofit=None):
        '''Site specific testing stuff-- open a multi  day statement'''
        # Site specific stuff here Open a monthly or yearly statemnet into the test db.
        # Currently set to search the journal root dir, so it will load an annual or two.
        bdir = ff.getBaseDir()
        fs = ff.findFilesInDir(bdir, 'U242.csv', True)
        ibs = IbStatement(db=self.db)
        for f in fs:

            x = ibs.openIBStatement(f)
            delt = ibs.endDate - ibs.beginDate
            assert delt.days > 20
            if not allofit:
                break
        return ibs, x

    def test_getUncoveredDays(self):
        '''Tests several methods in the covered process from''' 
        self.clearTables()
        ibdb = StatementDB(self.db)
        ibs, x = self.openStuff()
        delt = ibs.endDate - ibs.beginDate
        assert delt.days > 20

        begin = ibs.endDate - pd.Timedelta(days=15)
        end = ibs.endDate + pd.Timedelta(days=15)
        covered = ibdb.getUncoveredDays(ibs.account, begin, end)
        self.assertTrue(len(covered) > 0)
        for c in covered:
            self.assertTrue(c > ibs.endDate)
            self.assertTrue(c <= end)

    def test_getStatementDays(self):
        '''
        Test the method StatementDB.getStatementDays. Exercises getUncovered. Specifically test that
        when it returns data, it has the correct fields required in FinReqCol. And that the trades
        all occur within the specified dates (this tests on a single day). Noticd that openStuff
        exercises a bunch of stuff.
        '''
        frc = FinReqCol()
        ibs, x = self.openStuff()
        current = ibs.endDate
        ibdb = StatementDB(db=self.db)
        days = list(pd.date_range(start=current-pd.Timedelta(days=21), end=current))
        days.sort(reverse=True)
        for day in days:
            if day.weekday() > 4 or ibdb.isHoliday(current):
                continue
            s = ibdb.getStatementDays(ibs.account, beg=day)
            if not s.empty:
                cols = [frc.ticker, frc.date, frc.shares, frc.bal, frc.price,
                        frc.avg, frc.comm, frc.acct, frc.oc, frc.PL, 'id']
                self.assertTrue(set(cols) == set(list(s.columns)))
                for daDate  in s[frc.date].unique():
                    self.assertEqual(day.date(), pd.Timestamp(daDate).date())


def main():
    unittest.main()

def notmain():
    t = Test_StatementDB()
    # t.test_getUncoveredDays()
    # t.test_getStatementDays()
    # t.test_insertTrade()
    # t.test_addTradeSummaries()
    t.test_findTrade()


if __name__ == '__main__':
    notmain()
    # main()