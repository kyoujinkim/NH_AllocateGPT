def loadTemplate(asset):
    '''
    :param asset: asset name (ex. '국내 주식시장', '선진국 주식시장', '이머징 주식시장', '채권시장', '원자재시장')
    :return: template
    '''

    template = f"{asset}에는 어떤 우려와 리스크가 있어? {asset}에 긍정적인 요인은 뭐야? 최대한 자세하게 대답해줘"

    return template