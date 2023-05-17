# translator 

Automatically selects the best translation API and falls back to native translators on failure.

## Auto Endpoint
```py
from oy3opy.translator import auto_endpoint, translate
# find the endpoints with the highest availability
auto_endpoint('en', 'zh', proxies = { 'https://': 'http://127.0.0.1:1081' })
# translate with auto endpoint
translate('hello', 'en', 'zh')
# full arguments call
translate(text = 'hello', src='en', dest='zh', endpoints = ['bing','deepl'], proxies = { 'https://': 'http://127.0.0.1:1081' }, timeout = 4)
```

## Manually Endpoint
```py
from oy3opy.translator import check_performace
print(check_performace(src='en', dest='zh', endpoints=['None','or','list','of','endpoint'], text = 'None or custom', proxies={}))
# result: ('bing', 'translation') ('deepl', 'translation') ('iciba', 'translation')
```

## Dependencies
- [Argos Translate](https://github.com/argosopentech/argos-translate)
- [UlionTse/translators](https://github.com/UlionTse/translators)