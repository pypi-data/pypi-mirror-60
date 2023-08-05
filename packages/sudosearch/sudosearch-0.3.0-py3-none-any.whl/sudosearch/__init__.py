__version__ = '0.3.0'

from bs4 import BeautifulSoup
import urllib.parse as urlparse
import urllib.request as urllib
import html
import re
import json

from sudosearch.spacy_keywords import Keywords

class SudoSearch:
    __request_url = 'https://www.google.com/search?{0}'
    __request_query_param = 'q'
    __request_data = None
    __request_headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    }

    def __init__(self):
        pass

    def __build_request(self, text):
        query_safe_text = urlparse.urlencode({self.__request_query_param: text})
        request = urllib.Request(self.__request_url.format(query_safe_text), self.__request_data, self.__request_headers)
        
        return request

    def __parse_results(self, request):
        try:
            response = urllib.urlopen(request)
            response_readable = response.read().decode('UTF-8')

            page_bs = BeautifulSoup(response_readable, 'html.parser')
            return self.__travese_doc(page_bs)
        except Exception:
            pass

        return []

    def __travese_doc(self, page):
        result = []

        for group in page.select('.g'):
            '''
            Traverse result groups
            '''

            result_group = {
                'link': self.__traverse_link_in_group(group),
                'preview': self.__traverse_preview_in_group(group),
                'hot_words': None
            }

            sp_key = Keywords()
            
            result_group['hot_words'] = sp_key.get_hotties(result_group['preview'])

            result.append(result_group)

        return result

    def __traverse_link_in_group(self, group):
        source_link = None

        for link in group.find_all('a'):
            src = link.attrs['href']

            if src.find("#") == -1 and src.find("webcache") == -1 and src.startswith("http", 0, len(src) - 1):
                source_link = src
                break

        return source_link
    
    def __traverse_preview_in_group(self, group):
        content = None

        for preview in group.select('.st'):
            content = preview
            break

        return self.__sanitize_content(content)

    def __sanitize_content(self, text):
        text = re.sub(r'<[^>]*>', "", str(text))
        text = html.unescape(text)
        return text

    def find(self, text):
        request = self.__build_request(text)
        return self.__parse_results(request)

    def find_json(self, text):
        request = self.__build_request(text)
        return json.dumps(self.__parse_results(request))

