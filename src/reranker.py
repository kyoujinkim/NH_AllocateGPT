from transformers import AutoModelForSequenceClassification, AutoTokenizer

import pandas as pd
import numpy as np
import torch

def exp_normalize(x):
    b = x.max()
    y = np.exp(x - b)
    return y / y.sum()

class reRanker:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained('Dongjin-kr/ko-reranker')
        self.model = AutoModelForSequenceClassification.from_pretrained('Dongjin-kr/ko-reranker')
        self.model.eval()

    def __make_pair(self, query, docs):
        pairs = []
        for doc in docs:
            pairs.append([query, doc.page_content])
        return pairs

    def scoring(self, pairs, device):
        with torch.no_grad():
            inputs = self.tokenizer(pairs, padding=True, truncation=True, return_tensors='pt', max_length=512).to(device)
            scores = self.model(**inputs, return_dict=True).to(device).logits.view(-1, ).float()
            scores = exp_normalize(scores.numpy())
            return scores

    def rerank(self, query: str, docs: [list], top_k: int = 10, device='cpu'):
        pairs = self.__make_pair(query, docs)
        scores = self.scoring(pairs, device)

        result = pd.DataFrame([docs, scores], index=['Doc', 'Score']).T\
                     .sort_values(by='Score', ascending=False)[:top_k]
        result = result.Doc.to_list()

        return result

if __name__ == '__main__':
    rR = reRanker()
    query = "나는 너를 싫어해"
    docs = ["나는 너를 사랑해", "너에 대한 나의 감정은 사랑 일 수도 있어", "말의 의미를 잘 모르겠는데?"]

    result = rR.rerank(query, docs)