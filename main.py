import configparser
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
from printAssetViewV2 import printAssetView
from printAssetWeight import printAssetWeight

import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

config = configparser.ConfigParser()
config.read('./src/config.ini')
OPENAI_API_KEY = config.get('section', 'OPENAI_API_KEY')
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
openai.api_key = os.getenv("OPENAI_API_KEY")

pdfPath = r'data/pdf_logs'
mDB = makeDB(pdfPath,
             embeddingMethod='HuggingFace',#'HuggingFace', OpenAi
             embeddingAi='snunlp/KR-SBERT-V40K-klueNLI-augSTS',#'BM-K/KoSimCSE-bert-multitask', text-embedding-ada-002
             )

datearr = pd.date_range(start='2023-12-31', end='2023-12-31', freq='Q').tolist()

pav = printAssetView(API_KEY=OPENAI_API_KEY, llmAiEngine='gpt-3.5-turbo-1106', numberOfReason=15)
paw = printAssetWeight(llmAiEngine='gpt-3.5-turbo-1106')

# define Universe
asset_dict = {
              'subasset1': ['국내 주식', '미국 주식', '유럽 주식', '일본 주식', '중국 주식', '이머징 주식'],
              'subasset4': ['성장스타일', '가치스타일', '퀄리티스타일', '모멘텀스타일', '배당스타일'],
              'subasset7': ['반도체', '소프트웨어', '2차전지', 'IT하드웨어', '통신서비스', '철강', '에너지', '유틸리티'
                            , '자동차', '건강관리', '화학', '필수소비재', '운송', '보험', '은행', '조선', '우주항공, 국방'
                            , '유통', '기계', '미디어, 엔터테인먼트', '화장품, 의류', '건설건축', '디스플레이'],
              }

if __name__ == '__main__':

    for date in datearr:
        s_date = date - MonthEnd(3) + timedelta(days=1)

        s_date_str = s_date.strftime('%Y-%m-%d')
        date_str = date.strftime('%Y-%m-%d')

        print('Processing: Period from {} to {}'.format(s_date_str, date_str))

        for provider in ['']: #['', 'NH투자증권']

            # check if file already exist
            if os.path.isfile(f"assetViewDict{provider}.json"):
                with open(f"assetViewDict{provider}.json", "r", encoding="UTF-8") as st_json:
                    assetViewDict = json.load(st_json)
            else:
                assetViewDict = {}

            if provider == 'NH':
                provider_fullname = 'NH투자증권'
            else:
                provider_fullname = ''

            if os.path.isdir(f'C:/Users/NHWM/PycharmProjects/AllocateGPT/db/{date_str}{provider}'):
                db = mDB.readDB(dbPath=f'C:/Users/NHWM/PycharmProjects/AllocateGPT/db/{date_str}{provider}')
            else:
                pdfPath = mDB.filterPDF(provider=provider_fullname,
                                        start=s_date_str,
                                        end=date_str)
                subdocList = mDB.readPDF(pdfPath)
                db = mDB.makeDB(subdocList,
                                dbPath=f'C:/Users/NHWM/PycharmProjects/AllocateGPT/db/{date_str}{provider}')


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
                          open(f'assetViewDict{provider}.json', 'w', encoding='UTF-8'),
                          ensure_ascii=False)