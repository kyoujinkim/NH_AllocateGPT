from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from tqdm import tqdm

from src.readPDF import PDFReader

from glob import glob
from typing import List

import pandas as pd


class makeDB:
    def __init__(self, pdfPath:str, embeddingMethod:str, embeddingAi:str):
        '''
        폴더로부터 원하는 기간의 PDF 문서들을 가져온 후, 텍스트를 추출, 그리고 DB에 저장하는 클래스입니다.

        :param pdfPath:
        :param embeddingMethod:
        :param embeddingAi:
        '''
        #기간 지정(월 OR 분기 단위)
         #계속해서 기간을 재지정할거니까, init에 넣지는 말자
        #readPDF
        #DB에 저장(월 OR 분기 표시)
        self.pdfPath = pdfPath
        self.pr = PDFReader()
        if embeddingMethod == 'HuggingFace':
            self.embeddings = HuggingFaceEmbeddings(model_name=embeddingAi)
        elif embeddingMethod == 'OpenAi':
            self.embeddings = OpenAIEmbeddings(model=embeddingAi)
        else:
            raise ValueError('embeddingMethod는 HuggingFace 또는 OpenAi만 가능합니다.')

    def filterPDF(self, provider:str, start:str, end:str):
        '''
        PDF를 정해진 기간과 제공자를 기준으로 필터링합니다.

        :param start: string format start date
        :param end: string format end date
        :return: list of pdf file path
        '''
        pdfList = glob(self.pdfPath + '/*.pdf')
        pdfDate = [x.split('(')[1].split(')')[0] for x in pdfList]
        pdfProvider = [x.split('.')[-2].replace(' ','') for x in pdfList]

        pdfDf = pd.DataFrame({'pdfPath':pdfList, 'pdfDate':pdfDate, 'pdfProvider':pdfProvider})
        pdfDf.index = pd.to_datetime(pdfDf['pdfDate'], format='%Y, %B %d')
        pdfDf = pdfDf.sort_index()

        #filter pdfDf by provider, start and end parameter
        if provider == '':
            pdfDf = pdfDf.loc[start:end]
        else:
            pdfDf = pdfDf[pdfDf.pdfProvider == provider].loc[start:end]

        return pdfDf.pdfPath.tolist()

    def readPDF(self, pdfPath:List[str]):
        '''
        pdfPath를 받아서 readPDF.py의 getPDF 함수를 통해 list of Document를 반환합니다.

        :param pdfPath: list of pdf file path
        :return: list of Sub Document
        '''

        #get list of Document
        docList = self.pr.getPDF(pdfPath)

        #split Document
        subdocList = []
        for doc in tqdm(docList, desc='PDF 세부분할'):
            subdoc = self.pr.split_text_byChunk(doc,
                                                chunk_size=800,
                                                overlap=100)
            subdocList.extend(subdoc)

        return subdocList

    def makeDB(self, subdocList:List[Document], dbPath:str):
        '''
        Sub Document와 상응하는 embedding을 생성하고, DB에 저장합니다.
        :param subdocList: list of Sub Document
        :return:
        '''

        docsearch = Chroma.from_documents(subdocList, self.embeddings, persist_directory=dbPath)
        docsearch.persist()

        return docsearch

    def readDB(self, dbPath: str):
        '''
        Sub Document와 상응하는 embedding이 저장된 DB를 읽어옵니다.
        :param subdocList: list of Sub Document
        :return:
        '''
        return Chroma(persist_directory=dbPath, embedding_function=self.embeddings)

if __name__ == '__main__':
    pdfPath = r'C:\Users\NHWM\PycharmProjects\AllocateGPT\data\pdf_logs'
    db = makeDB(pdfPath,
                embeddingMethod='OpenAi',
                embeddingAi='BM-K/KoSimCSE-bert-multitask')
    doclist = db.filterPDF('', '2023-10-01', '2023-12-31')
    subdoclist = db.readPDF(doclist)
    monthlyDb = db.makeDB(subdoclist,
                          dbPath=r'C:\Users\NHWM\PycharmProjects\AllocateGPT\db\231231')