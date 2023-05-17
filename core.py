from .testcase import cases
from oy3opy.utils.task import downgrade, doneQueue, Task
import difflib
import os
from typing import List, Tuple
import translators
import argostranslate.package
import argostranslate.translate

endpoints = translators.translators_pool
invalid_endpoints = {}
auto_endpoints = {}
argostranslate.package.update_package_index()
offline_translate = argostranslate.translate.translate
diff = difflib.Differ()

try:
    os.environ['ARGOS_DEVICE_TYPE'] = 'cuda'
    offline_translate('this app is cool', 'en', 'en')
except:
    del os.environ['ARGOS_DEVICE_TYPE']
    print('WARN: run offline translate without CUDA')

def offline_translate_preload(src:str, dest:str):
    argostranslate_to_install = next(filter(lambda x: (x.from_code == src and x.to_code == dest), argostranslate.package.get_available_packages()))
    argostranslate.package.install_from_path(argostranslate_to_install.download())

def translate(text:str, src:str='en', dest:str='en', endpoints = 'auto', proxies = {}, timeout = 4):
    if src == dest:
        return text
    if endpoints == 'auto':
        endpoints = auto_endpoints[type]
    try:
        return downgrade(translators.translate_text, [((text, endpoint, src, dest),{'proxies': proxies, 'timeout': timeout}) for endpoint in [*endpoints, *translators.translators_pool]])
    except:
        offline_translate_preload(src, dest)
        return offline_translate(text, src, dest)



def get_case(code:str, proxies = {}):
    if code not in cases:
        cases[code] = translate(cases['en'], code, 'en', check_availability('en', code, proxies), proxies)
    return cases[code]

def test_endpoint(src:str, dest:str, endpoint:str, text = None, proxies={}):
    type = f'{src}->{dest}'
    if not invalid_endpoints.get(type):
        invalid_endpoints[type] = []
    if endpoint in invalid_endpoints[type]:
        return None
    try:
        text = text if text else get_case(src, proxies)
        output = translators.translate_text(text, endpoint, src, dest, timeout = 4, proxies = proxies)
        if len(output) > (len(text)/4):
            return output
    except Exception as e:
        invalid_endpoints[type].append(endpoint)

def test_endpoints(src:str, dest:str, endpoints = endpoints, text = None, proxies={}):
    outputs = []
    for (endpoint, output) in doneQueue([(endpoint, Task(Task(test_endpoint,(src, dest, endpoint, text, proxies)).catch)) for endpoint in endpoints]):
        if output:
            outputs.append((endpoint, output))
    return outputs

def check_availability(src:str, dest:str, endpoints=endpoints, text = None, proxies={}) -> List[str]:
    return [endpoint for (endpoint, output) in test_endpoints(src, dest, endpoints, text, proxies) if output]

def check_performace(src:str, dest:str, endpoints=endpoints, text = None, proxies={}) -> List[Tuple[str,str]]:
    return [(endpoint, output) for (endpoint, output) in test_endpoints(src, dest, endpoints, text, proxies) if output]

def auto_endpoint(src:str, dest:str, proxies = {}) -> List[str]:
    type = f'{src}->{dest}'
    if type in auto_endpoints:
        return auto_endpoints[type]
    endpoints = []
    if (src == 'en') and (dest == 'en'):
        return []
    if (dest in cases) and (src in cases):
        testcase = get_case(src)
        for (endpoint, output) in check_performace(src, dest, text=testcase, proxies = proxies):
            endpoints.append((len(list(diff.compare(output.split(), testcase.split()))), endpoint))
    else:
        if dest == 'en':
            (src, dest) = (dest, src)
        testcase = get_case('en')
        for (endpoint, output) in check_performace('en', dest, check_availability(src, dest), testcase, proxies):
            best = 2 * len(testcase)
            for (_, check) in check_performace(dest, 'en', text=output, proxies=proxies):
                distance = len(list(diff.compare(check.split(), testcase.split())))
                best = distance if distance < best else best
            endpoints.append((best, endpoint))
    endpoints.sort(key=lambda t:t[0])
    auto_endpoints[type] = list(filter(lambda endpoint: endpoint not in invalid_endpoints[type], [endpoint for (_, endpoint) in endpoints]))
    return auto_endpoints[type]
