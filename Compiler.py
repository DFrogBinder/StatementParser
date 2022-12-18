import os 
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import PyPDF2 as pd2
import sqlite3
import logging
from sqlite3 import Error 

def Add_Values(conn, Val):
    """
    Create a new project into the projects table
    :param conn:
    :param project:
    :return: project id
    """
    sql = ''' 
    INSERT INTO RawFinData('Date','Previous_Account_Balance','Closed_Position_PnL','Deposit_Withdrawals','Other_Transactions','Account_Balance')
              VALUES(?,?,?,?,?,?) 
    '''

    cur = conn.cursor()
    for i in range(len(Val)):
        cur.execute(sql, Val[i])
        conn.commit()
    return cur.lastrowid

def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        logging.info("SQLite version is :",sqlite3.version)
    except Error as e:
        logging.error(e)
    return conn

def Create_Table(Connector):
    
    sql = '''CREATE TABLE RawFinData (
	Date REAL PRIMARY KEY,
    Previous_Account_Balance REAL NOT NULL ,
	Closed_Position_PnL REAL NOT NULL,
	Deposit_Withdrawals REAL NOT NULL, 
    Other_Transactions REAL NOT NULL,
	Account_Balance REAL NOT NULL);
    '''

    Connector.execute(sql)
    return Connector


def get_data(VList,idx):
    data = VList[idx+1]
    return data

# Main function
def compile(ArchivePath):
    DataFrame = []
 
    # Read in data
    pdf = pd2.PdfFileReader(ArchivePath) 

    # Get the first page
    FirstPage = pdf.getPage(0)

    # Get text from first page
    RawText = FirstPage.extract_text()

    itrList = RawText.split('\n')
    for line,idx in zip(itrList,range(len(itrList))):
        if line == 'Account Balance':
            Valuation = get_data(itrList,idx)
            DataFrame.append(Valuation)
        elif line == 'Closed Position P/L':
            PL = get_data(itrList,idx)
            DataFrame.append(PL)
        elif line == 'Previous Account Balance':
            PrevValuation = get_data(itrList,idx)
            DataFrame.append(PrevValuation)
        elif line == 'Deposits  / Withdrawals':
            DW = get_data(itrList,idx)
            DataFrame.append(DW)
        elif line == 'Date':
            Date = get_data(itrList,idx)
            DataFrame.append(Date)
        elif line == 'Other Transactions':
            OtherTransactions = get_data(itrList,idx)
            DataFrame.append(OtherTransactions)
        else:
            continue
    return DataFrame

def main(ArchivePath):
    DB = []
    if not os.path.exists(ArchivePath):
        logging.error("Archive path does not exist")
        return

    ArchiveList = os.listdir(ArchivePath)
    for ent in ArchiveList:
        if not ent == '.DS_Store' and ent.split('.')[-1] == 'pdf':
            DB.append(compile(os.path.join(ArchivePath,ent)))

    # DB = pd.DataFrame(DB)

    Connector = create_connection(':memory:') # ':memory:'
    Create_Table(Connector)
    Add_Values(Connector, DB)

    p2 = pd.read_sql('select * from RawFinData', Connector)

    Connector.close()
    print(p2)

main('/Users/boyanivanov/sandbox/StatementParser/Archive')