import json
import os
import re
import sys
from datetime import timedelta
from time import sleep

import openai
import pandas as pd
from pandas._libs.tslibs.offsets import MonthEnd
from tqdm import tqdm

from makeDB import makeDB
from printAssetView import printAssetView
from printAssetWeight import printAssetWeight

os.environ["OPENAI_API_KEY"] = 'OPEN_AI_API_KEY'
openai.api_key = os.getenv("OPENAI_API_KEY")

pdfPath = r'data/pdf_logs'
mDB = makeDB(pdfPath,
             embeddingMethod='HuggingFace',
             embeddingAi='BM-K/KoSimCSE-bert-multitask',
             )

datearr = pd.date_range(start='2012-01-01', end='2023-06-30', freq='Q').tolist()

pav = printAssetView()
paw = printAssetWeight()

#check if file already exist
if os.path.isfile("assetViewDict.json"):
    with open("assetViewDict.json", "r", encoding="UTF-8") as st_json:
        assetViewDict = json.load(st_json)
else:
    assetWeightDict = {}
    assetViewDict = {}

# define Universe
asset_dict = {
              'subasset1': ['국내주식', '미국주식', '이머징주식'],
              'subasset2': ['성장주', '가치주'],
              'subasset3': ['반도체','은행','자동차','화학','증권','운송','바이오','소비재'],
              }

if __name__ == '__main__':

    for date in datearr:
        s_date = date - MonthEnd(3) + timedelta(days=1)

        s_date_str = s_date.strftime('%Y-%m-%d')
        date_str = date.strftime('%Y-%m-%d')

        print('Processing: Period from {} to {}'.format(s_date_str, date_str))

        if os.path.isdir(f'./db/{date_str}'):
            db = mDB.readDB(dbPath=f'./db/{date_str}')
        else:
            pdfPath = mDB.filterPDF_byPeriod(s_date_str, date_str)
            subdocList = mDB.readPDF(pdfPath)
            db = mDB.makeDB(subdocList,
                            dbPath=f'./db/{date_str}')

        #['국내주식시장', '선진국주식시장', '이머징주식시장', '국내채권시장', '선진국채권시장', '이머징채권시장', '에너지원자재시장', '산업금속원자재시장', '귀금속원자재시장']
        for asset_categ in asset_dict:

            # continue from last saved progress
            if asset_categ+'_'+date_str in assetViewDict:
                continue

            assetTable = asset_dict[asset_categ]
            pav.define_universe(assetTable)

            #print asset views
            pav.set_baseDocument(db)

            #due to connection error, try 5 times with 3 min interval
            conclusion = None
            counter = 0
            while conclusion == None and counter < 5:
                try:
                    conclusion, assetView = pav.printAssetView()
                except:
                    counter += 1
                    sleep(180)

            #if conclusion is None, exit process
            if conclusion == None:
                sys.exit('Connection Error')

            #save as dict format
            assetViewDict[asset_categ+'_'+date_str] = assetView

            json.dump(assetViewDict,
                      open('assetViewDict.json', 'w', encoding='UTF-8'),
                      ensure_ascii=False)
