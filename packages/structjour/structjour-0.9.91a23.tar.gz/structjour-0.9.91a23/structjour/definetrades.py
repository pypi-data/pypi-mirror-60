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
Created on Sep 5, 2018

@author: Mike Petersen
'''
import logging
import sys
# import datetime
import pandas as pd

from structjour.colz.finreqcol import FinReqCol 
from structjour.dfutil import DataFrameUtil
from structjour.statements.ibstatementdb import StatementDB
from structjour.stock.utilities import isNumeric

# pylint: disable = C0103




class ReqCol(object):
    '''
    Intended as an adapter class for multiple input types. ReqCol are the columns for the original
    input file All of these are required.
    '''

    def __init__(self, source="DAS"):
        '''Set the required columns in the import file.'''

        if source != 'DAS':
            logging.error("Only DAS is currently supported")
            raise ValueError

        # rcvals are the actual column titles (to be abstracted when we add new input files)
        # rckeys are the abstracted names for use with all file types
        rckeys = ['time', 'ticker', 'side', 'price', 'shares', 'acct', 'PL', 'date']
        rcvals = ['Time', 'Symb', 'Side', 'Price', 'Qty', 'Account', 'PnL', 'Date']
        rc = dict(zip(rckeys, rcvals))

        # Suggested way to address the columns for the main input DataFrame.
        self.time = rc['time']
        self.ticker = rc['ticker']
        self.side = rc['side']
        self.price = rc['price']
        self.shares = rc['shares']
        self.acct = rc['acct']
        self.PL = rc['PL']
        self.date = rc['date']

        self.rc = rc
        self.columns = list(rc.values())


class DefineTrades(object):
    '''
    DefineTrades moves the data from DataFrame representing the input file transactions to a
    dataframe with added columns sorted into trades, showing trade start time, share balance for
    each trade, and the duration of each trade.
    '''

    def __init__(self, source='DAS'):
        '''
        Constructor
        '''
        self.source = source
        assert self.source in ['DAS', 'IB_HTML', 'IB_CSV', 'DB']

        self._frc = FinReqCol(source)

    def appendCols(self, rccols):
        '''
        HACK ALERT:  adding columns to the the 'final' list of cols. Not ready to add these cols
        to FinReqCol
        '''
        cols = ['id', 'DAS', 'IB', 'tsid']
        for c in cols:
            if c not in rccols:
                rccols.append(c)
        return rccols

    
    def processDBTrades(self, trades):
        '''
        Run the methods to create the new DataFrame and fill in the data for the new trade-
        centric DataFrame.
        '''
        rc = self._frc

        # Process the output file DataFrame
        trades = self.addFinReqCol(trades)
        rccolumns = rc.columns.copy()
        rccolumns = self.appendCols(rccolumns)
        
        newTrades = trades[rccolumns]
        newTrades.copy()
        nt = newTrades.sort_values([rc.ticker, rc.acct, rc.date])
        # nt = self.writeShareBalance(nt)
        nt = self.addStartTimeDB(nt)
        # nt.Date = pd.to_datetime(nt.Date)
        nt = nt.sort_values([rc.start, rc.ticker, rc.acct, rc.date, rc.time], ascending=True)
        nt = self.addTradeIndex(nt)
        nt = self.addTradePL(nt)
        nt = self.addTradeDurationDB(nt)
        nt = self.addTradeNameDB(nt)
        # ldf is a list of DataFrames, one per trade
        ldf = self.getTradeList(nt)
        ldf, nt = self.postProcessingDB(ldf)
        nt = DataFrameUtil.addRows(nt, 2)
        nt = self.addSummaryPL(nt)

        dframe = DataFrameUtil.addRows(nt, 2)
        return dframe, ldf

    def processOutputDframe(self, trades):
        '''
        Run the methods to create the new DataFrame and fill in the data for the new trade-
        centric DataFrame.
        '''
        c = self._frc

        # Process the output file DataFrame
        trades = self.addFinReqCol(trades)
        newTrades = trades[c.columns]
        newTrades.copy()
        nt = newTrades.sort_values([c.ticker, c.acct, c.time])
        nt = self.writeShareBalance(nt)
        nt = self.addStartTime(nt)
        nt.Date = pd.to_datetime(nt.Date)
        # nt = nt.sort_values([c.ticker, c.start, c.acct, c.date, c.time], ascending=True)
        nt = nt.sort_values([c.start, c.acct, c.date, c.time], ascending=True)
        nt.reset_index(drop=True, inplace=True)
        nt = self.addTradeIndex(nt)
        nt = self.addTradePL(nt)
        nt = self.addTradeDuration(nt)
        nt = self.addTradeName(nt)
        # ldf is a list of DataFrames, one per trade
        ldf = self.getTradeList(nt)
        ldf, nt = self.postProcessing(ldf)
        nt = DataFrameUtil.addRows(nt, 2)
        nt = self.addSummaryPL(nt)

        # Get the length of the original input file before adding rows for processing Workbook
        # later (?move this out a level)
        inputlen = len(nt)
        dframe = DataFrameUtil.addRows(nt, 2)
        return inputlen, dframe, ldf

    def writeShareBalance(self, dframe):
        '''
        Create the data for share balance for a ticker. Note that for overnight holds after, the
        amount entered here is incorrect. It is corrected in postProcessing(). (for before trades,
        the amount entered hereis correct)
        :params dframe: The DataFrame representing the initial input file plus a bit.
        :return: The same dframe with updated balance entries.
        '''
        prevBal = 0
        c = self._frc

        for i, row in dframe.iterrows():
            qty = (dframe.at[i, c.shares])

            # This sets the after holds to 0 and leaves the before holds to set the proper balance
            if row[c.side] == "HOLD-" or row[c.side] == "HOLD+":
                dframe.at[i, c.bal] = 0
                newBalance = 0
            else:
                newBalance = qty + prevBal

            dframe.at[i, c.bal] = newBalance
            prevBal = newBalance
        return dframe

    def addStartTimeDB(self, dframe):
        '''
        Add the start time to the new column labeled Start or frc.start. Each transaction in each
        trade will share a start time.
        :params dframe: The output df to place the data
        :return dframe: The same dframe but with the new start data.
        '''

        rc = self._frc

        newTrade = True
        oldsymb = ''
        oldaccnt = ''
        for i, row in dframe.iterrows():

            if row[rc.ticker] != oldsymb or row[rc.acct] != oldaccnt:
                newTrade = True
            oldsymb = row[rc.ticker]
            oldaccnt = row[rc.acct]

            if newTrade:
                newTrade = True if isNumeric(row[rc.bal]) and row[rc.bal] == 0 else False
                oldTime = dframe.at[i, rc.time]
                dframe.at[i, rc.start] = oldTime

            else:
                dframe.at[i, rc.start] = oldTime
            if row[rc.bal] == 0:
                newTrade = True
        return dframe

    def addStartTime(self, dframe):
        '''
        Add the start time to the new column labeled Start or frc.start. Each transaction in each
        trade will share a start time.
        :params dframe: The output df to place the data
        :return dframe: The same dframe but with the new start data.
        '''

        c = self._frc

        newTrade = True
        for i, row in dframe.iterrows():
            if newTrade:
                if row[c.side].startswith('HOLD') and i < len(dframe):
                    oldTime = dframe.at[i+1, c.time]
                    dframe.at[i, c.start] = oldTime

                else:
                    oldTime = dframe.at[i, c.time]
                    dframe.at[i, c.start] = oldTime

                newTrade = False
            else:
                dframe.at[i, c.start] = oldTime
            if row[c.bal] == 0:
                newTrade = True
        return dframe

    def addTradeIndex(self, dframe):
        '''
        Labels and numbers the trades by populating the TIndex column. 'Trade 1' for example includes the transactions 
        between the initial purchase or short of a stock and its subsequent 0 position. (If the stock is held overnight, 
        non-transaction rows have been inserted to account for todays' activities.)
        '''

        rc = self._frc

        TCount = 0
        prevEndTrade = True
        prevTicker = ''
        prevAccount = ''

        for i, row in dframe.iterrows():
            if len(row[rc.ticker]) < 1:
                break
            if prevEndTrade or prevTicker != row[rc.ticker] or prevAccount != row[rc.acct]:
                TCount += 1
            tradeIndex = "Trade " + str(TCount)
            dframe.at[i, rc.tix] = tradeIndex

            prevEndTrade = False
            prevTicker = row[rc.ticker]
            prevAccount = row[rc.acct]
            # tradeIndex = "Trade " + str(TCount)
            if row[rc.bal] == 0:
                prevEndTrade = True
        return dframe

    def addTradePL(self, dframe):
        '''
        Add a trade summary P/L. That is total the transaction P/L and write a summary P/L for the
        trade in the c.sum column '''
        rc = self._frc
        newtrade = pd.DataFrame()
        for tindex in dframe[rc.tix].unique():
            t = dframe[dframe[rc.tix] == tindex]
            ixs = t.index
            sum = t[rc.PL].sum()
            t.at[ixs[-1], rc.sum] = sum
            newtrade = newtrade.append(t)
        return newtrade

    def addTradePLold(self, dframe):
        ''' Add a trade summary P/L. That is total the transaction P/L and write a summary P/L for the trade in the c.sum column '''

        c = self._frc

        tradeTotal = 0.0
        for i, row in dframe.iterrows():
            if not isNumeric(row[c.bal]):
                raise ValueError('Programmers exception from addTradePL. Input from badTrade')
            pl = row[c.PL] if isNumeric(row[c.PL]) else 0
            if row[c.bal] != 0:
                tradeTotal = tradeTotal + pl
            else:
                sumtotal = tradeTotal + pl
                dframe.at[i, c.sum] = sumtotal
                tradeTotal = 0
        return dframe

    def addTradeDurationDB(self, dframe):
        '''
        Get a time delta beween the time of the first and last transaction. Place it in the
        c.dur column on the last transaction of the trade'''

        c = self._frc
        ldf = self.getTradeList(dframe)
        newdf = pd.DataFrame()
        for tdf in ldf:
            assert len(tdf[c.start].unique()==1)
            ixs = tdf.index
            timeEnd = pd.Timestamp(tdf.at[ixs[-1], c.time])
            timeStart = pd.Timestamp(tdf.at[ixs[-1], c.start])
            dur = timeEnd - timeStart
            tdf.at[ixs[-1], c.dur] = dur
            # dur = tdf.at[ixs[-1], c.time] - tdf.at[ixs[-1], c.start]
            newdf = newdf.append(tdf)

        return newdf

    def addTradeDuration(self, dframe):
        ''' Get a time delta beween the time of the first and last transaction. Place it in the c.dur column'''

        c = self._frc

        for i, row in dframe.iterrows():
            if row[c.bal] == 0:
                timeEnd = pd.Timestamp(row[c.time])
                timeStart = pd.Timestamp(row[c.start])
                assert timeEnd.date() == timeStart.date()
                diff = timeEnd - timeStart

                # end = timeEnd.split(":")
                # start = timeStart.split(":")
                # diff = datetime.datetime(1, 1, 1, int(end[0]), int(end[1]), int(
                #     end[2])) - datetime.datetime(1, 1, 1, int(start[0]), int(start[1]), int(start[2]))
                dframe.at[i, c.dur] = diff
        return dframe


    def addTradeNameDB(self, dframe):
        '''
        Create a name for this trade like 'AMD Short'. Place it in the c.name column. If this is
        not an overnight hold, then the last transaction is an exit so B indicates short. This
        could still be a flipped position. We need the initial transactions- which are processed
        later.
        '''

        rc = self._frc
        newtrade = pd.DataFrame()
        for tindex in dframe[rc.tix].unique():
            t = dframe[dframe[rc.tix] == tindex]
            ixs = t.index
            side = ''
            if (t.iloc[-1][rc.oc].find('O') >= 0 and t.iloc[-1][rc.shares] > 0) or (
                t.iloc[-1][rc.oc].find('C') >= 0 and t.iloc[-1][rc.shares] < 0):
                side = ' Long'
            else:
                side = ' Short'
            name = t[rc.ticker].unique()[0]
            name += side
            t.at[ixs[-1], rc.name] = name
            newtrade = newtrade.append(t)
        return newtrade


    def addTradeName(self, dframe):
        '''
        Create a name for this trade like 'AMD Short'. Place it in the c.name column. If this is
        not an overnight hold, then the last transaction is an exit so B indicates short. This
        could still be a flipped position. We need the initial transactions- which are processed
        later.
        '''

        c = self._frc

        for i, row in dframe.iterrows():

            longShort = " Long"
            if row[c.bal] == 0:
                # this is the last tx of the trade today. B or HOLD- are shorts
                if row[c.side] == 'B' or row[c.side].startswith('HOLD-'):
                    longShort = " Short"
                dframe.at[i, c.name] = row[c.ticker] + longShort
        return dframe

    def addSummaryPL(self, df):
        '''
        Create a summaries of live, sim and total P/L for the day and place it in new rows.
        Total and sim total go in the first blank row under PL and sum
        Live total in lower blank row under sum. Note that the accounts are identified 'IB' style
        and will break when new brokers are added.  Uxxxxxxxx is live, TRxxxxxx is sim. When new
        brokers are added do something else.
        :prerequisites: 2 blank rows added at the bottom of the df
        :raise ValueError: If blank lines are not in df.
        '''
        rc = self._frc
        df.reset_index(drop=True, inplace=True)
        df[rc.PL] = pd.to_numeric(df[rc.PL], errors='coerce')

        ixs = df[df[rc.ticker] == ''].index
        assert len(ixs) > 1
        total = df[rc.PL].sum()
        for acnt in df[rc.acct].unique():
            acnttotal = df[df[rc.acct] == acnt][rc.PL].sum()
            if acnt.startswith('U'):
                df.at[ixs[1], rc.sum] = acnttotal
            elif acnt.startswith('TR'):
                df.at[ixs[0], rc.sum] = acnttotal
                
        df.at[ixs[0], rc.PL] = total
        return df


    def addSummaryPLold(self, dframe):
        ''' 
        Create a summary of the P/L for the day, place it in new row. 
        Sum up the transactions in c.PL for Live and Sim Seperately.
        We rely on the account number starting with 'U' or 'TR' to determine
        live or SIM. These two columns should add to the same amount. '''
        # Note that .sum() should work on this but it failed when I tried it.
        # because the two extra rows had PL Strings as ''
        c = self._frc

        count = 0
        tot = 0.0
        tot2 = 0.0
        totLive = 0.0
        totSim = 0.0
        for i, row in dframe.iterrows():
            count = count+1
            if count < len(dframe)-1:
                tot = tot+row[c.PL]
                if row[c.bal] == 0:
                    tot2 = tot2 + row[c.sum]
                    if row[c.acct].startswith('TR'):
                        totSim = totSim + row[c.sum]
                    else:
                        assert(row[c.acct].startswith('U'))
                        totLive = totLive + row[c.sum]
                # if count == len(dframe) -2 :
                #     lastCol = row[c.PL]

            elif count == len(dframe) - 1:
                dframe.at[i, c.PL] = tot
                dframe.at[i, c.sum] = totSim
            else:
                assert (count == len(dframe))
                dframe.at[i, c.sum] = totLive

        return dframe



    def getTradeList(self, dframe):
        '''
        Creates a python list of DataFrames for each trade. It relies on addTradeIndex successfully creating the 
        trade index in the format Trade 1, Trade 2 etc.
        :param:dframe: A dataframe with the column Tindex filled in.
        '''
        # Now  we are going to add each trade and insert space to put in pictures with circles and
        # arrows and paragraph on the back of each one to be used as evidence against you in a court
        # of law (or court of bb opionion)
        # insertsize=25
        # dframe = nt
        c = self._frc
        try:
            if not dframe[c.tix].unique()[0].startswith('Trade'):
                raise(NameError(
                    "Cannot make a trade list. Call addTradeIndex() before."))
        except NameError as ex:
            logging.error(ex)
            sys.exit(-1)

        ldf = list()
        count = 1
        while True:
            tradeStr = "Trade " + str(count)
            count = count + 1
            tdf = dframe[dframe.Tindex == tradeStr]
            if len(tdf) > 0:
                ldf.append(tdf)
            else:
                break
        return ldf

    def fixTsid(self, tdf):
        if len(tdf['tsid'].unique()) > 1:
            therightone = list()

            for id in tdf['tsid'].unique():
                if isNumeric(id):
                    therightone.append(id)
            if len(therightone) > 1:
                # This could be a place for user input...There are confused ids here
                # The question is what trade do these transactions belong to.
                raise ValueError('Programmers exception: Something needs to be done here')
            elif len(therightone) == 1:
                ibdb = StatementDB()
                for i, row in tdf.iterrows():
                    tdf.at[i, 'tsid'] = therightone[0]
                    ibdb.updateTSID(row['id'], therightone[0])
                # If one of the vals was nan, the column became float
                tdf = tdf.astype({'tsid': int})
                # Update the db
        return tdf
                


    def postProcessingDB(self, ldf):
        '''
        A few items that need fixing up. Locate and name flipped positions and overnight holds and
        change the name appropriately. Look for trades that lack a tsid (foreign key) and fix
        :params ldf: A ist of DataFrames, each DataFrame represents a trade defined by the initial
                     purchase or short of a stock, and all transactions until the transaction which
                     returns the share balance to 0.
        :return (ldf, nt): The updated versions of the list of DataFrames, and the updated single
                      DataFrame.
        '''
        rc = self._frc
        dframe = pd.DataFrame()
        for tdf in ldf:
            x0 = tdf.index[0]
            xl = tdf.index[-1]
            if tdf.at[x0, rc.bal] != tdf.at[x0, rc.shares] or tdf.at[xl, rc.bal] != 0:
                tdf.at[xl, rc.name] = tdf.at[xl, rc.name] + " OVERNIGHT"
        
            if tdf.at[x0, rc.bal] != 0:
                firstrow = True
                for i, row in tdf.iterrows():
                    if firstrow:
                        side = True if row[rc.bal] > 0 else False
                        firstrow = False
                    elif row[rc.bal] != 0 and (row[rc.bal] >= 0) != side:
                        tdf.at[xl, rc.name] = tdf.at[xl, rc.name] + " FLIPPED"
                        break
            else:
                assert len(tdf) == 1
            if len(tdf['tsid'].unique()) > 1 or not isNumeric(tdf['tsid'].unique()[0]):
                tdf = self.fixTsid(tdf)
                    
            dframe = dframe.append(tdf)
        return ldf, dframe


    def postProcessing(self, ldf):
        '''
        A few items that need fixing up in names and initial HOLD entries. This method is called
        after the creation of the DataFrameList (ldf). We locate flipped positions and overnight
        holds and change the name appropriately. Also update initial HOLD prices, and balance with
        the calculated average price of pre owned shares and initial shares respectively.
        :params ldf: A ist of DataFrames, each DataFrame represents a trade defined by the initial
                     purchase or short of a stock, and all transactions until the transaction which
                     returns the share balance to 0. Last entry may be a HOLD indicating shares
                     were held overnight in the amount of the previous transaction share balance.
                     After HOLDs are nontransactions. shares are listed as 0 indicating the
                     number of shares owned is in the previous transaction. Before HOLDs attempt to
                     show the current status of previous transctions not given explicity.
        :return (ldf, nt): The updated versions of the list of DataFrames, and the updated single
                      DataFrame.

        '''
        c = self._frc
        dframe = pd.DataFrame()
        for count, tdf in enumerate(ldf):
            tdf.copy()
            if tdf.iloc[-1][c.bal] == 0:
                x0 = tdf.index[0]
                xl = tdf.index[-1]
                if tdf.at[x0, c.side].startswith('HOLD') or tdf.at[xl, c.side].startswith('HOLD'):
                    tdf.at[xl, c.name] = tdf.at[xl, c.name] + " OVERNIGHT"
                    # Apparent double testing to cover trades with holds both before and after
                    if tdf.at[xl, c.side].startswith('HOLD'):
                        tdf.at[xl, c.bal] = 0
                    if tdf.at[x0, c.side].startswith('HOLD'):
                        sharelist = list()
                        pricelist = list()
                        for dummy, row in tdf.iterrows():
                            # Here we set initial entries' average price of shares previously held
                            # based on the P/L of the first exit. The math gets complicated if
                            # there are more than 2 entrances before # the first exit. This
                            # currently only works without extra opens before the first close.
                            # TODO Send in some SIM trades to model it.
                            sharelist.append(row[c.shares])
                            pricelist.append(row[c.price])
                            if row[c.PL] != 0:
                                # TODO This does not cover the possibilities-- still have no models
                                originalPrice = row[c.price] + (row[c.PL] / row[c.shares])
                                tdf.at[x0, c.price] = originalPrice
                                break
                elif tdf.at[x0, c.side].startswith('B') and tdf.at[xl, c.side].startswith('B'):
                    # Still not sure how IB deals with flipped trades. I think they break down the
                    # shares to figure, for ex, PL from shares sold closed to 0 balance, and avg
                    # price change from Shares sold Open to bal
                    # TODO: Get a an IB Statement with a flipped position
                    tdf.at[xl, c.name] = tdf.at[xl, c.name] + " FLIPPED"

                    msg = '\nFound a flipper long to short.\n'
                    msg = msg + "Use this file for devel and testing if this is an IB statement\n"
                elif not tdf.at[x0, c.side].startswith('B') and not tdf.at[xl, c.side].startswith('B'):
                    # tdf.iloc[-1][c.name] = tdf.iloc[-1][c.name] + " FLIPPED"
                    tdf.at[xl, c.name] = tdf.iloc[-1][c.name] + " FLIPPED"
                    msg = '\nFound a flipper short to long.\n'
                    msg = msg + "Use this file for devel and testing if this is an IB statement\n"
            else:
                msg = ('This should never run. What happned in postProcessing?',
                      'It means we have a non 0 balance at the end of a trade.(!?!)',
                      str(tdf.iloc[-1][c.bal], tdf.iloc[-1][c.name]))
                logging.error(msg)
            if count == 0:
                dframe = tdf
            else:
                dframe = dframe.append(tdf)
        return ldf, dframe

    def addFinReqCol(self, dframe):
        '''
        Add the columns from FinReqCol that are not already in dframe.
        :params dframe: The original DataFrame with the columns of the input file and including at
                         least all of the columns in ReqCol.columns
        :return dframe: A DataFrame that includes at least all of the columns in FinReqCol.columns
        '''
        c = self._frc
        for l in c.columns:
            if l not in dframe.columns:
                dframe[l] = ''
        return dframe
