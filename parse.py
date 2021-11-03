from bs4 import BeautifulSoup
from bs4.element import Tag
import datetime
import locale
import json
import os

class Item:
    FMT = '%d %m %Y'

    def __init__(self, title: str, date: datetime.datetime, price: float, shipping: float, sold: bool):
        self.title = title
        self.date = date
        self.price = price
        self.shipping = shipping
        self.sold = sold

    def calc_total_price(self) -> float:
        return self.price + self.shipping

    def calc_days_since_epoch(self) -> int:
        return (self.date - datetime.datetime(1970, 1, 1)).days

    def get_dict(self):
        return {
            'title': self.title,
            'date': self.date.strftime(Item.FMT),
            'price': self.price,
            'shipping': self.shipping,
            'sold': self.sold
        }

    @staticmethod
    def from_dict(d: dict):
        return Item(
            d['title'],
            datetime.datetime.strptime(d['date'], Item.FMT),
            d['price'],
            d['shipping'],
            d['sold'])

class Scraper:
    def __init__(self, html_doc: str):
        self.soup = BeautifulSoup(html_doc, 'html.parser')

    def _get_results_tag(self) -> Tag:
        results_tag = self.soup.find('ul', {'class': 'srp-results srp-list clearfix'})
        if not results_tag:
            raise Exception('Results not found')
        return results_tag

    def _get_item_tags(self) -> list:
        result_list, results = self._get_results_tag(), []
        for result in result_list.find_all('li'):
            try:
                if 's-item' in result['class']:
                    results.append(result)
            except:
                pass
        if not results:
            raise Exception('Items not found')
        return results

    @staticmethod
    def _parse_title(item: Tag) -> str:
        for h3 in item.find_all('h3'):
            try:
                if 's-item__title' in h3['class']:
                    title = h3.text
                    if not title:
                        raise Exception('Title empty')
                    return title
            except:
                pass
        raise Exception('Title not found')

    @staticmethod
    def _parse_date(item: Tag) -> datetime.datetime:
        x = None
        for div in item.find_all('div'):
            try:
                if 's-item__title--tagblock' in div['class']:
                    x, span = div, div.next
                    if 'POSITIVE' in span['class']:
                        text = span.text.replace(f'{config["sold"]} ', '')
                    elif 'NEGATIVE' in span['class']:
                        text = span.text.replace(f'{config["ended"]} ', '')
                    else:
                        raise Exception('Unknown date format')
                    return datetime.datetime.strptime(text.strip(), config['fmt'])
            except Exception as e:
                print(e)
                pass
        if x:
            print(x)
        raise Exception('Date not found')

    @staticmethod
    def _parse_price_text(text: str) -> float:
        started, shipping, points = False, '', 0
        for c in text:
            if started:
                if c.isdigit():
                    shipping += c
                elif c in ',.':
                    points += 1
                    shipping += c
                else:
                    break
            elif c.isdigit():
                shipping += c
                started = True
        if not shipping:
            return 0.0
        if points != 0:
            shipping = shipping.replace(',', '.')
            if points > 1:
                parts = shipping.split('.')
                shipping = f'{"".join(parts[:-1])}.{parts[-1]}'
        return float(shipping)

    @staticmethod
    def _parse_price(item: Tag) -> float:
        for span in item.find_all('span'):
            try:
                if 's-item__price' in span['class']:
                    price_tag = span.find('span')
                    return Scraper._parse_price_text(price_tag.text)
            except:
                pass
        raise Exception('Price not found')

    @staticmethod
    def _parse_shipping(item: Tag) -> float:
        b = False
        for span in item.find_all('span'):
            try:
                if 's-item__shipping' in span['class']:
                    b = True
                    return Scraper._parse_price_text(span.text)
            except:
                pass
        if not b:
            return 0.0
        raise Exception('Shipping not found')

    @staticmethod
    def _parse_sold(item: Tag) -> bool:
        for span in item.find_all('span'):
            try:
                if 's-item__price' in span['class']:
                    classes = span.next['class']
                    if 'POSITIVE' in classes:
                        return True
                    elif 'NEGATIVE' in classes:
                        return False
                    raise Exception('Sold not parsed')
            except:
                pass
        raise Exception('Sold not found')

    @staticmethod
    def _parse_item_tag(item: Tag) -> Item:
        title = Scraper._parse_title(item)
        date = Scraper._parse_date(item)
        price = Scraper._parse_price(item)
        shipping = Scraper._parse_shipping(item)
        sold = Scraper._parse_sold(item)
        return Item(title, date, price, shipping, sold)

    def parse_items(self) -> list:
        item_tag_list = self._get_item_tags()
        items = []
        for item_tag in item_tag_list:
            items.append(self._parse_item_tag(item_tag))
        return items

config = {
    'locale': 'de_DE',
    'sold': 'Verkauft',
    'ended': 'Beendet',
    'fmt': '%d. %b %Y'
}

if __name__ == '__main__':
    out, overwrite = 'items.json', True
    html_docs_path = ['1.html']
    items = []
    locale.setlocale(locale.LC_TIME, config['locale'])
    for html_doc_path in html_docs_path:
        if not os.path.exists(html_doc_path):
            print(f'\'{html_doc_path}\' not found (skipped)')
            continue
        with open(html_doc_path, 'rb') as f:
            html_doc = f.read().decode()
            f.close()
        if not html_doc:
            print(f'\'{html_doc_path}\' empty (skipped)')
            continue
        scraper = Scraper(html_doc)
        items.extend(scraper.parse_items())
    if os.path.exists(out):
        if overwrite:
            data = []
        else:
            with open(out, 'r') as f:
                data = json.load(f)
                f.close()
    else:
        data = []
    with open(out, 'w') as f:
        data.extend(list(map(lambda item: item.get_dict(), items)))
        json.dump(data, f, indent=2)
        f.close()
