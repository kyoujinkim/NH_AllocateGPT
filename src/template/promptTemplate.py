def loadTemplate():
    template = """아래에 주어진 근거를 사용해서 질문에 대한 자세한 정답의 목록을 생성해줘.
    정답의 형식은 아래 <예시>를 참고해. 정답은 <실제> 부분만을 보고 작성해줘.

    <예시>
    질문: 기술주 상승 배경과 향후 전망
    =========
    근거: 일반적으로 선진국의 은행위기가 발생했을 경우, 변동성과 위험자산 회피심리가 확대되며 신흥국에 더 큰 리스크 프리미엄을 요구
    출처: 전병하,엄서진. (2023, April 17). Changing. 20pg
    근거: 하지만 금리 인상의 정점 부근에서는 우리가 알 수 없는 이벤트 리스크라는 공포가 등장할 수 있다. IT버블, 서브프라임 모기지 등 여러 경기 충격이 금리 인상 시기의 말미에 등장했다.
    출처: 리서치센터. (2023, April 10). NH FICC. 4pg
    =========
    정답: - 선진국의 은행위기 발생시 변동성과 위험자산 회피심리가 확대되며 신흥국에 더 큰 리스크 프리미엄을 요구할 수 있음(*1)
    - 금리 인상의 정점 부근에서는 알 수 없는 이벤트 리스크 등장 가능. 경기 충격이 금리 인상 시기의 말미에 등장(*2)

    <실제>
    질문: {question}
    =========
    근거: {summaries}
    =========
    정답:"""

    template_s = """ 아래에 주어진 근거를 질문과 관련이 없는 근거는 제외하고 올바른 순서대로 다시 정렬해줘. 질문과 관련있는 근거만을 사용해줘.
    정답의 형식은 아래 <예시>를 참고해. 정답은 <실제> 부분만을 보고 작성해줘.

    <예시>
    질문: 2차전지 소재
    =========
    근거: - 2차전지 소재 업체 중 가장 빠른 성장성 기대하는 CNT도전재(*1)
    - 나노신소재가 고체 도전재 기술 보유로 인한 주가 탄력(*3)
    - 유럽 CRMA의 2차전지 Upstream 정책으로 인한 2차전지 셀, 소재 주가 소폭 하락(*6)
    - CNT도전재의 원료인 CNT 파우더 생산 업체인 동사는 전자의 통로 역할을 하는 필수 소재인 도전재를 생산함(*7)
    - 2차전지 내 기술 경쟁력을 토대로 성장이 본격화되는 소재는 실리콘 음극재, CNT 도전재 등이 남아 있다(*8)
    - LG에너지솔루션, 삼성SDI가 Top Pick으로 추천됨(*11)
    =========
    정답: - 2차전지 내 기술 경쟁력을 토대로 성장이 본격화되는 소재는 실리콘 음극재, CNT 도전재 등이 남아 있다(*8)
    - 2차전지 소재 업체 중 가장 빠른 성장성 기대하는 CNT도전재(*1)
    - 나노신소재가 고체 도전재 기술 보유로 인한 주가 탄력(*3)
    - 동사는 CNT도전재의 원료인 CNT 파우더 생산 업체인 동사는 전자의 통로 역할을 하는 필수 소재인 도전재를 생산함(*7)

    <실제>
    질문: {question}
    =========
    근거: {summaries}
    =========
    정답: """

    template_agg = """아래에 주어진 근거를 종합해서 질문에 대한 결론을 간단하고 명료한 어조로 작성해줘. 질문과 관련있는 근거만을 사용해줘. 관련있는 근거가 없다면 답변을 작성하지 않아도 돼.
    정답의 형식은 아래 <예시>를 참고해. 정답은 <실제> 부분만을 보고 작성해줘.

    <예시>
    질문: 기술주 상승 배경과 향후 전망
    =========
    근거: - 인공지능에 대한 관심 증가로 최근 기술주 상승 주도.
    - 최근 기술주의 상승은 생성형 인공지능 시장으로 인해 생성된 기회에 기인하지만, 그와 동시에 강해질 경쟁 압력은 상승에 부정적.
    =========
    정답: 위 내용들을 종합하면, 기술주는 향후 상승할 가능성이 높습니다.

    <실제>
    질문: {question}
    =========
    근거: {summaries}
    =========
    정답: """

    return {'template':template,
            'template_s':template_s,
            'template_agg':template_agg}

def loadTemplateV2():
    template = """I want you to act as a Financial Analyst.
    Firstly, analyze the given list of evidence and questions.
    For each question, filter out any evidence that is irrelevant to the particular question and asset.
    Then, arrange the remaining evidence in an order that logically supports the detail answer to the question.
    Finally, formulate a list of detailed answers for each question about asset based on the relevant evidence.
    Refer to the provided example for the format of answers,
    ensuring that your response solely reflects the actual facts or data from the 'Actual' section of the evidence.
    Structure your answers clearly and concisely, mirroring the example's format. Answer should be Explanatory and detailed with step by step.
    Given text will be in {input_lang}, but you can respond in English.

    <Example>
    Asset: Secondary Batteries Industry
    Asset Detail: The secondary battery industry is a industry which manufactures secondary batteries with lithium-ion batteries, lithium polymer batteries, and others.
    Question: The background of the rise in tech stocks and future prospects
    =========
    Evidence: Expecting the fastest growth among secondary battery material companies with CNT current collectors
    Source: Secondary Battery Materials. 10pg
    Evidence: Stock elasticity due to the possession of solid-state current collector technology by nanomaterials
    Source: NH Investment & Securities. Solid-state Current Collectors. 20pg
    Evidence: A slight decrease in the stock prices of secondary battery cells and materials due to the secondary battery Upstream policy of European CRMA
    Source: Secondary Battery Upstream. 7pg
    Evidence: The company, a producer of CNT powder which is the raw material of CNT current collectors, produces conductive materials that act as a conduit for electronics
    Source: Powder Production Companies. 1pg
    =========
    Answer: - Materials poised for growth based on technological competitiveness in secondary batteries include silicon anode materials, CNT current collectors, among others
    - Expecting the fastest growth among secondary battery material companies with CNT current collectors
    - Stock elasticity due to the possession of solid-state current collector technology by nanomaterials
    - The company produces conductive materials, which are essential for electronics and made from CNT powder, the raw material of CNT current collectors

    <Actual>
    Asset: {asset}
    Asset Detail: {asset_description}
    Question: {question}
    =========
    Evidence: {summaries}
    =========
    Answer:"""

    template = """I want you to act as a Financial Analyst.
    Firstly, analyze the given list of evidence and questions.
    For each question, filter out any evidence that is irrelevant to the particular question and asset.
    Then, arrange the remaining evidence in an order that logically supports the detail answer to the question.
    Finally, formulate a list of detailed answers for each question about asset based on the relevant evidence.
    Refer to the provided example for the format of answers, ensuring that your response solely reflects the actual facts or data from the the evidence.
    Answer with several key points in detail as much as possible.
    
    Asset: {asset}
    Asset Detail: {asset_description}
    Question: {question}
    =========
    Evidence: {summaries}
    =========
    Answer:"""

    template_agg = """I want you to act as a Financial Analyst.
    Using the evidence provided below, synthesize a conclusion for the question.
    You must have to follow the instructions below.
        1. Answer must include more than 5 key points.
        2. Only use evidence that is relevant to the question.
        3. Arrange the evidence in a logical order that supports the answer.
    
    Asset: {asset}
    Asset Detail: {asset_description}
    Question: {question}
    =========
    Evidence: {summaries}
    =========
    Answer: """

    return {'template': template,
            'template_agg': template_agg}
