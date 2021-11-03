from parse import *
import matplotlib.pyplot as plt
import numpy as np
import itertools

class WeekdayItems:
    def __init__(self, mo: list, tu: list, we: list, th: list, fr: list, sa: list, su: list):
        self.mo = mo
        self.tu = tu
        self.we = we
        self.th = th
        self.fr = fr
        self.sa = sa
        self.su = su

    def get_list(self) -> list:
        return [self.mo, self.tu, self.we, self.th, self.fr, self.sa, self.su]

    def get_all_items(self):
        return list(itertools.chain.from_iterable(self.get_list()))

    def get_len_all(self):
        return sum(map(lambda items: len(items), self.get_list()))

    def print_stuff(self):
        print('[Items per weekday]')
        i = 0
        for items in self.get_list():
            analyzer = Analyzer(items)
            print(f"--- {['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su'][i]} ---")
            analyzer.print_stuff()
            i += 1

    def plot_stuff(self):
        labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        av_sells_per_day = self.get_len_all() / 7
        y1 = list(map(lambda items: round((len(items) / av_sells_per_day - 1.0) * 100, 2), self.get_list()))
        av_total_price = Analyzer(self.get_all_items()).calc_av_total_price()
        y2 = list(map(lambda items: round((Analyzer(items).calc_av_total_price() / av_total_price - 1.0) * 100, 2), self.get_list()))

        x = np.arange(len(labels))  # the label locations
        width = 0.35  # the width of the bars

        fig, ax = plt.subplots()
        rects1 = ax.bar(x - width / 2, y1, width, label='Sells')
        rects2 = ax.bar(x + width / 2, y2, width, label='Price')

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_ylabel('Percentage')
        ax.set_title('Sells and price against average')
        plt.axhline(y=0.0, color='k', linestyle='-', linewidth=1.0)
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.legend()

        ax.bar_label(rects1, padding=3)
        ax.bar_label(rects2, padding=3)

        fig.tight_layout()

        plt.show()

class DayItems:
    def __init__(self, d: dict):
        self.d = d

    def print_stuff(self):
        print('[Items per days]')
        for date in self.d.keys():
            analyzer = Analyzer(self.d[date])
            print(f"--- {date.strftime('%d/%m/%Y')} ({['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su'][date.weekday()]}) ---")
            analyzer.print_stuff()

class Analyzer:
    def __init__(self, items: list):
        self.items = items

    def drop_by_min(self, min_total: float) -> int:
        i = 0
        for item in self.items:
            if item.calc_total_price() < min_total:
                self.items.remove(item)
                i += 1
        return i

    def drop_by_max(self, max_total: float) -> int:
        i = 0
        for item in self.items:
            if item.calc_total_price() > max_total:
                self.items.remove(item)
                i += 1
        return i

    def calc_av_price(self) -> float:
        return sum(map(lambda item: item.price, self.items)) / len(self.items)

    def calc_av_shipping(self) -> float:
        return sum(map(lambda item: item.shipping, self.items)) / len(self.items)

    def calc_av_total_price(self) -> float:
        return sum(map(lambda item: item.calc_total_price(), self.items)) / len(self.items)

    def get_weekday_items(self) -> WeekdayItems:
        weekday_item_list = [[], [], [], [], [], [], []]
        for item in self.items:
            weekday_item_list[item.date.weekday()].append(item)
        return WeekdayItems(weekday_item_list[0], weekday_item_list[1], weekday_item_list[2], weekday_item_list[3],
                            weekday_item_list[4], weekday_item_list[5], weekday_item_list[6])

    def get_day_items(self) -> DayItems:
        d1, d2 = {}, {}
        for item in self.items:
            days = item.calc_days_since_epoch()
            if days in d1.keys():
                d1[days].append(item)
            else:
                d1[days] = [item]
        for k in d1.keys():
            d2[datetime.datetime.fromtimestamp(k*86400)] = d1[k]
        return DayItems(d2)

    def print_stuff(self):
        print(f'Items: {len(self.items)}')
        # print(f'Ø-Price: {round(self.calc_av_price(), 2)}')
        # print(f'Ø-Shipping: {round(self.calc_av_shipping(), 2)}')
        print(f'Ø-Total-Price: {round(self.calc_av_total_price(), 2)}')

if __name__ == '__main__':
    with open('items.json', 'r') as f:
        data = json.load(f)
        f.close()

    all_items = list(map(lambda item_dic: Item.from_dict(item_dic), data))
    analyzer_all = Analyzer(all_items)

    # analyzer_all.drop_by_min(800.0)
    # analyzer_all.drop_by_max(1200.0)
    # analyzer_all.print_stuff()

    weekday_items = analyzer_all.get_weekday_items()
    weekday_items.print_stuff()
    # weekday_items.plot_stuff()

    # day_items = analyzer_all.get_day_items()
    # day_items.print_stuff()
