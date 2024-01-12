from typing import List

import openai
import tiktoken
from langchain_community.chat_models import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.template import weightTemplate
from src.template import recommendTemplate


class printAssetWeight:
    def __init__(self,
                 llmAiEngine: str = 'gpt-4-1106-preview'
                 , OPENAI_API_KEY: str = ''
                 ):
        self.OPENAI_API_KEY = OPENAI_API_KEY
        self.Engine = llmAiEngine
        self.tokenizer = tiktoken.encoding_for_model(llmAiEngine)
        self.model = ChatOpenAI(model=self.Engine
                           , openai_api_key=self.OPENAI_API_KEY
                           , max_retries=5)
        self.output_parser = StrOutputParser()

    def printAssetWeight(self, assetView: dict, constraint: List[str] = [], method: str = 'weight'):

        if method == 'weight':
            template = weightTemplate.loadTemplate(assetView, constraint)
        elif method == 'recommend':
            template = recommendTemplate.loadTemplate(assetView, constraint)

        prompt = ChatPromptTemplate.from_template(template)

        chain = prompt | self.model | self.output_parser

        output = chain.invoke({
        })

        return output
