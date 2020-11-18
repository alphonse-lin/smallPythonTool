import pandas as pd
import json
from pandas import Series, DataFrame

if __name__ == '__main__':
    filePath = r'E:\114_temp\008_代码集\001_python\smallPythonTool\Excel2XML\data\造价表.xlsx'
    first_outputPath = r'E:\114_temp\008_代码集\001_python\smallPythonTool\Excel2XML\data\造价表.json'
    data = pd.read_excel(filePath, sheet_name='Sheet1', header=0, index_col=0)
    nameList=[]
    for name in data.index:
        nameList.append(name.strip('\n'))
    data.index=Series(nameList)
    data = data.replace('\n', ' ', regex=True)
    print(data.iloc[0])

    data.to_json(first_outputPath, orient='columns')
