def loadTemplate(asset):
    '''
    :param asset: asset name (ex. '국내 주식시장', '선진국 주식시장', '이머징 주식시장', '채권시장', '원자재시장')
    :return: template
    '''

    template = f"{asset}에는 어떤 우려와 리스크가 있어? {asset}에 긍정적인 요인은 뭐야? 최대한 자세하게 대답해줘"

    return template

def loadQueryTemplate(asset, asset_description):

    template = f'''
    {asset}는 다음과 특성을 지니는 투자자산이야: {asset_description}
    
    
    1. {asset}의 과거 성과 및 트렌드를 알려줘.
    2.{asset}의 현재 상황 및 전망을 알려줘.
    3.{asset}에 대한 위험과 우려, 기회를 알려줘.'''

    return template


def loadQueryGenTemplate():
    template = '''
    Create a query for retrieve appropriate information from Retrieval Augmentation method.
    Information trying to retrieve is past, current, trend, and outlook of {asset}.
    Also want to know risk, concern, and opportunity of {asset}.
    You don't need to write a query for all of them.
    {asset}: {asset_description}
    
    When create a query, you should consider the following:
    1. You should create a query in various context as much as possible.
    2. Consider the most distinctive attributes, relationships, or functions relevant to your search.
    3. Use step by step instruction.
    4. Query should be written in {input_lang}.
        
    Query:'''

    return template