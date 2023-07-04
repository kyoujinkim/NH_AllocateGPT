from typing import List


def loadTemplate(assetViews: dict, constraint: List[str] = []):
    '''
    :param assetView: asset and each view (ex. {'국내주식시장': '상승', '해외주식시장': '상승', '채권시장': '상승', '원자재시장': '상승'})
    :return: template
    '''

    constraint = ' '.join(constraint)
    assetViewTemplate = ''
    counter = 1
    for asset in assetViews:
        assetViewTemplate += f'자산{counter}. {asset} : {assetViews[asset]}\n'
        counter += 1

    template = f'''다음 자산별 전망에 따라 수익률을 극대화할 수 있도록, 추천순위를 정하십시오. {constraint}
=========
[전망]
{assetViewTemplate}
=========
자산별 추천순위:'''

    return template