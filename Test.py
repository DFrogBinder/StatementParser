import os
import numpy as np
import pandas as pd
import PyPDF2 as pd2
import sqlite3
import logging
import streamlit as st
import plotly.express as px

from AppKit import NSScreen
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
        # logging.info("SQLite version is :",sqlite3.version)
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

def get_display_dimensions():
    main_monitor = NSScreen.mainScreen().frame()
    return (int(main_monitor.size.width), int(main_monitor.size.height))

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

# Create a scatter plot
def scatter_plot(x,y,Title):
    df = pd.concat([x,y],axis=1)
    col1, col2 = df.columns
    fig = px.scatter(df, x=col1, y=col2)
    st.plotly_chart(fig)

    fig.update_layout(
    title={
        'text': Title,
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})

def bar_plots(x,y,Title):
    df = pd.concat([x,y],axis=1)
    col1, col2 = df.columns
    fig = px.bar(df,x=col1, y=col2,barmode='group')
    st.plotly_chart(fig)

    fig.update_layout(
    title={
        'text': Title,
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})

def PlotGraphs(Data):
   
    AccBal = Data['Account_Balance']
    PnL = Data['Closed_Position_PnL']
    Time = Data['Date']
    PAccBall = Data['Previous_Account_Balance']
    Other = Data['Other_Transactions']
    DW = Data['Deposit_Withdrawals']

    scatter_plot(Time,AccBal,"Account Balance")
    bar_plots(Time,PnL,"Closed Positions")
    bar_plots(Time,DW,"Deposits / Withdrawals")

    return 1

# Main function
def main_page():
    st.title('My Streamlit Dashboard')
    ArchivePath='/Users/boyanivanov/sandbox/StatementParser/Archive'
    
    DB = []
    if not os.path.exists(ArchivePath):
        logging.error("Archive path does not exist")
        return

    ArchiveList = os.listdir(ArchivePath)
    for ent in ArchiveList:
        if not ent == '.DS_Store' and ent.split('.')[-1] == 'pdf':
            DB.append(compile(os.path.join(ArchivePath,ent)))

    Connector = create_connection(':memory:') # ':memory:'
    Create_Table(Connector)
    Add_Values(Connector, DB)

    p2 = pd.read_sql('select * from RawFinData', Connector)
    # Sorts by Date  
    p2["Date"] = pd.to_datetime(p2["Date"], format='%d %b %Y')
    p2 = p2.sort_values(by="Date")

    Connector.close()
    err = PlotGraphs(p2)
    if err:
        logging.info("Plotting Graphs Completed!")
    else:
        logging.error("Plotting Graphs Failed!")

# Pages
def home():
    st.header('Home')
    st.write('This is the home page.')

def about():
    st.header('About')
    st.write('This is the about page.')

def contact():
    st.header('Contact')
    st.write('This is the contact page.')

# Dictionary of pages
pages = {
    'Home': home,
    'About': about,
    'Contact': contact,
    'Main': main_page
}

# Main app
def main():
    # Render the SelectBox for the navigation
    page = st.sidebar.selectbox("Navigation", list(pages.keys()))

    # Run the app corresponding to the selected page
    pages[page]()

if __name__ == "__main__":
    main()
