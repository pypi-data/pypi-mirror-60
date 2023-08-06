
values = {}

def webParse(url,regularExpression):
  try:
    headers = {}
    headers['User-Agent'] = "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"
    req = urllib.request.Request(url, headers = headers)
    resp = urllib.request.urlopen(req)
    respData = resp.read()
    data = re.findall(regularExpression, str(respData))
    return
  except Exception as e:
    print(str(e))
    
def advancedWebParse(url,values):
  try:
    parseData = urllib.parse.urlencode(values)
    parseData = data.encode('utf-8')
    req = urllib.request.Request(url,parseData)
    resp = urllib.request.urlopen(req)
    readData = resp.read()
    return 
  except Exception as e:
    print(str(e))
    
def getValues(url):
  SplitValues = re.split(r'[?&=]', url)
  SplitValues.pop(0)
  for val in range(0,len(SplitValues),2):
    values.update({SplitValues[val] : SplitValues[val + 1]})
  return values
  
def changeValues(value,changedvalue):
  values[value] = changedvalue

