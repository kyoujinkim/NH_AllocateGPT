import configparser
import json
from typing import List

import openai
import tiktoken
from langchain_openai import ChatOpenAI
from langchain.docstore.document import Document
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tqdm import tqdm

import src.template.promptTemplate as pTemp
import src.template.queryTemplate as qTemp
from makeDB import makeDB
from src.quoteChecker import changeQuoteNum, printQuote

from src.reranker import reRanker


class printAssetView:
    '''
    프롬프트와 데이터베이스를 받아서 LLM 입력 토큰으로 제공
    출력값으로 자산별 리스크/상승요인 요약텍스트를 출력해서 가져오는 로직
    '''
    def __init__(self,
                 API_KEY: str,
                 llmAiEngine: str = 'gpt-3.5-turbo-1106',
                 rerankerEngine: list = ['Alibaba-NLP/gte-multilingual-reranker-base'
                                         , 'amberoad/bert-multilingual-passage-reranking-msmarco'
                                         , 'Dongjin-kr/ko-reranker'],
                 numberOfReason: int = 10,
                 asset_descripion_path: str = './src/asset_description.json',
                 device='cpu'
                 ):

        self.API_KEY = API_KEY
        self.engine = llmAiEngine
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        self.numberOfReason = numberOfReason
        self.asset_description = json.load(open(asset_descripion_path, 'r', encoding='utf-8'))
        self.rR1 = reRanker(model=rerankerEngine[0], device=device)
        self.rR2 = reRanker(model=rerankerEngine[1], device=device)
        self.rR3 = reRanker(model=rerankerEngine[2], device=device)

        templates = pTemp.loadTemplate()
        q_template = qTemp.loadQueryGenTemplate()

        model = ChatOpenAI(model=self.engine
                           , openai_api_key=self.API_KEY
                           , max_retries=5)
        output_parser = StrOutputParser()

        q_prompt = ChatPromptTemplate.from_template(q_template)
        prompt = ChatPromptTemplate.from_template(templates['template'])
        prompt_agg = ChatPromptTemplate.from_template(templates['template_agg'])

        self.q_chain = q_prompt | model | output_parser
        self.chain = prompt | model | output_parser
        self.chain_agg = prompt_agg | model | output_parser

    def define_universe(self, assetTable: List[str]):
        self.assetTable = assetTable

    def generate_query(self, asset: str):
        #set query for printAssetView
        output = self.q_chain.invoke({
            "asset": asset
            , "asset_description": self.asset_description[asset]
            , "input_lang": 'korean'
        })

        return output

    def set_baseDocument(self, baseDocument):
        #set baseDocument for printAssetView
        self.baseDocument = baseDocument

    def get_similarDocs(self, query, filter=None):
        #get similar docs for printAssetView
        return self.baseDocument.similarity_search(query, k=self.numberOfReason*3, filter=filter)

    def printEvidence(self, docs, query, asset) -> List[Document]:

        '''근거 목록 저장'''
        output = self.chain.invoke({
            "input_lang": 'korean'
            , "question": query
            , "summaries": docs
            , "asset": asset
            , "asset_description": self.asset_description[asset]
        })

        return output

    def printConclusion(self, context_doc, query, asset) -> str:
        '''
        쿼리에 대한 응답을 생성하는 텍스트 컨센서스 생성 프로세스

        :param query:
        :param context_doc:
        :param docs:
        :return:
        '''

        '''요약 기준 결론 출력'''
        output = self.chain_agg.invoke({
            "question": query
            , "summaries": context_doc
            , "asset": asset
            , "asset_description": self.asset_description[asset]
        })

        return output

    def printQuote(self, rearr_context_doc, docs,) -> str:
        '''주석 출력'''
        quoteOutput = printQuote(rearr_context_doc, docs, verbose=False)

        return ''.join(quoteOutput)

    def printAssetView(self, filter=None):
        '''
        쿼리에 대한 자산관점 요약을 생성하는 텍스트 컨센서스 생성 프로세스
        :param query:
        :param docs:
        :return:
        '''

        result = {}
        archive = {}
        pbar = tqdm(self.assetTable)
        for asset in pbar:
            '''쿼리 세팅'''
            #query = self.generate_query(asset)
            query = qTemp.loadQueryTemplate(asset, self.asset_description[asset])

            '''유사 문서 목록 찾기'''
            pbar.set_postfix_str(f"{asset} : Find Similar Docs")
            docs = self.get_similarDocs(query, filter)

            '''유사 문서 재정렬'''
            pbar.set_postfix_str(f"{asset} : Re-ranking similar Docs")
            docs1 = self.rR1.rerank(query, docs, top_k=self.numberOfReason)
            docs2 = self.rR2.rerank(query, docs, top_k=self.numberOfReason)
            docs3 = self.rR3.rerank(query, docs, top_k=self.numberOfReason)
            docs = docs1 + docs2 + docs3

            '''근거 목록 저장'''
            pbar.set_postfix_str(f"{asset} : Print Evidence")
            context_doc_total = []
            for i in range(2):
                pbar.set_postfix_str(f"{asset} : Print Evidence - {i}")
                context_doc = self.printEvidence(docs, query, asset)
                context_doc_total.append(context_doc)
            context_doc = '\n'.join(context_doc_total)

            '''결론 출력'''
            pbar.set_postfix_str(f"{asset} : Print Conclusion")
            conclusion = self.printConclusion(context_doc, query, asset)

            '''주석 출력'''
            #quoteOutput = self.printQuote(context_doc, docs)

            '''전체문구'''
            totalOutput = ('\n[Conclusion]').join([context_doc, conclusion])

            result[asset] = context_doc
            archive[asset] = totalOutput

        return result, archive

if __name__ == "__main__" :
    config = configparser.ConfigParser()
    config.read('./src/config.ini')
    OPENAI_API_KEY = config.get('section', 'OPENAI_API_KEY')

    pdfPath = r'data/pdf_logs'
    mDB = makeDB(pdfPath,
                 embeddingMethod='HuggingFace',  # 'HuggingFace', OpenAi
                 embeddingAi='snunlp/KR-SBERT-V40K-klueNLI-augSTS',
                 # 'BM-K/KoSimCSE-bert-multitask', text-embedding-ada-002
                 )
    db = mDB.readDB(dbPath=f'C:/Users/NHWM/PycharmProjects/AllocateGPT/db/2023-12-31')
    a = printAssetView(API_KEY=OPENAI_API_KEY, numberOfReason=15)
    a.set_baseDocument(db)
    a.define_universe(['중국 주식', "미국주식"])
    b = a.printAssetView()
    c = 1