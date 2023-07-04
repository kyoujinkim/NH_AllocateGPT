import re
import unicodedata

def changeQuoteNum(txt, addnum):
  txtNumStrList = re.findall(r'\(\*\d+', txt)
  for txtNumStr in txtNumStrList:
    txtNum = [x for x in txtNumStr if x.isdigit()]
    txtNum = int(''.join(txtNum))
    txt = txt.replace(txtNumStr, f'(*{txtNum+addnum}')
  return txt

def printQuote(rearr_context_doc, docs, verbose:bool=True):
  txtNumStrList = re.findall(r'\*\d+', rearr_context_doc.page_content)
  txtNumList = []
  for txtNumStr in txtNumStrList:
    txtNum = [x for x in txtNumStr if x.isdigit()]
    txtNum = int(''.join(txtNum))
    txtNumList.append(txtNum)
  txtNumList = list(set(txtNumList))

  '''주석 표시'''
  quoteList = []
  for txtNum in txtNumList:
    #when marked Quote is not in the range of docs, Continue
    if txtNum-1 >= len(docs):
      continue
    doc = docs[txtNum-1]
    quote = f"(*{txtNum}){unicodedata.normalize('NFC',doc.metadata['source'].replace('/',''))}. {int(doc.metadata['page'])+1}pg"
    quoteList.append(quote)

  if verbose:
    print('출처: ', '; '.join(quoteList))

  return '출처: ', '; '.join(quoteList)