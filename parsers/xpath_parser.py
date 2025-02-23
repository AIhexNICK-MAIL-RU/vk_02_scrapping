import io
from lxml import etree
import re
from urllib.parse import urljoin


class XPathParser:
    def __init__(self):
        self._parser = etree.HTMLParser()

    def _get_text_content(self, root, xpath, regex=None):
        result = root.xpath(xpath)
        if not result:
            return None
        result = ''.join(result)
        if not regex:
            return result.strip()
        match = re.search(regex, result)
        if match:
            return match.group().strip()
        return None

    # def _parse_product_page(self, tree):
    #     result = {}
    #     result['title'] = self._get_text_content(tree, '//title/text()')

    #     return result

    def _parse_product_page(self, tree):
        result = {}
        
        # Описание книги
        description = self._get_text_content(tree, 
            '//div[@class="sub-header"]/following-sibling::p/text()')
        result['description'] = description if description else ''
        
        # Жанр (берем из URL категории)
        category_url = self._get_text_content(tree, 
            '//ul[@class="breadcrumb"]/li[3]/a/@href')
        result['genre'] = category_url.split('/')[1] if category_url else ''
        
        # Цена
        price = self._get_text_content(tree, 
            '//p[@class="price_color"]/text()')
        result['price'] = price if price else ''
        
        # Количество в наличии
        availability = self._get_text_content(tree, 
            '//p[@class="instock availability"]/text()')
        if availability:
            match = re.search(r'\((\d+)\)', availability)
            result['stock_quantity'] = int(match.group(1)) if match else 0
        else:
            result['stock_quantity'] = 0
        
        # Рейтинг (количество звезд)
        star_class = self._get_text_content(tree, 
            '//p[@class="star-rating"]/@class')
        if star_class:
            star_map = {
                'One': 1, 'Two': 2, 'Three': 3, 
                'Four': 4, 'Five': 5
            }
            result['rating'] = star_map.get(star_class.split()[-1], 0)
        else:
            result['rating'] = 0
        
        return result

    def _get_next_links(self, tree, cur_page_url):
        next = []
        # ссылки на товары
        for elem in tree.xpath('//*[contains(@class, "product_pod")]/*/a[@title]/@href'):
            next.append(urljoin(cur_page_url, elem))
        # след. страница
        next_page = tree.xpath('//li[@class="next"]/a/@href')
        if next_page:
            next.append(urljoin(cur_page_url, next_page[0]))
        return next

    def parse(self, content, cur_page_url):
        tree = etree.parse(io.BytesIO(content), self._parser)
        product_page_root = tree.xpath('//article[contains(@class, "product_page")]')
        result = None
        if product_page_root:
            result = self._parse_product_page(tree)
            return result, []
        next = self._get_next_links(tree, cur_page_url)
        return None, next
