import json
def pt1_check(id):
    with open(f'test/response_{id}.json',encoding='utf-8') as js:
        dict = json.load(js)
        print(dict['name'])

pt1_check(9869958)