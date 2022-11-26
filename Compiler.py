import os 
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import PyPDF2 as pd2


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
            DataFrame.append([line,Valuation])
        elif line == 'Closed Position P/L':
            PL = get_data(itrList,idx)
            DataFrame.append([line,PL])
        elif line == 'Previous Account Balance':
            PrevValuation = get_data(itrList,idx)
            DataFrame.append([line,PrevValuation])
        elif line == 'Deposits  / Withdrawals':
            DW = get_data(itrList,idx)
            DataFrame.append([line,DW])
        elif line == 'Date':
            Date = get_data(itrList,idx)
            DataFrame.append([line,Date])
        elif line == 'Other Transactions':
            OtherTransactions = get_data(itrList,idx)
            DataFrame.append([line,OtherTransactions])
        else:
            continue
    return DataFrame

def main(ArchivePath):
    DB = []
    if not os.path.exists(ArchivePath):
        print("Archive path does not exist")
        return

    ArchiveList = os.listdir(ArchivePath)
    for ent in ArchiveList:
        if not ent == '.DS_Store' and ent.split('.')[-1] == 'pdf':
            DB.append(compile(os.path.join(ArchivePath,ent)))

    DB = pd.DataFrame(DB)
    print(DB)

main('/Users/boyanivanov/sandbox/StatementParser/Archive')