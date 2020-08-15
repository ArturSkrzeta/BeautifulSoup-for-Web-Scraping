from requests import get
from bs4 import BeautifulSoup
import pandas as pd

# currency_name / against_currency -- f.e. EUR/USD : EUR as BASE CURRENCY / USD as QUOTE CURRENCY
currency_name = 'EUR' # BASE CURRENCY
against_currency = 'PLN' # QUOTE CURRENCY, currency symbol or type ALL in order to get all currencies
url = 'https://www.xe.com/currencytables/?from=' + currency_name + '&date='
tag = 'td'
rates = [] # here all the currency rates will be stored

dates = [] # here all set dates will be stored
# 2020 July
year_start = 2020
year_stop = year_start # if it equals year_start then only that year
month_start = 7
month_stop = month_start # if it equal month_start then only for that month

def print_list_out(lst):
    for item in lst:
        print(item)

def chunk_data(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size] # 0:4 | 4:8 | 8:12 | 12:16 ...

        # [
        # 0 : <td><a href="https://www.xe.com/currency/usd-us-dollar">USD</a></td>,
        # 1 : <td>US Dollar</td>,
        # 2 : <td class="historicalRateTable-rateHeader">1.1325221897</td>,
        # 3 : <td class="historicalRateTable-rateHeader">0.8829849067</td>
        # ]

def get_page_content(date):
    URL = url + date
    page = get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup

def extract_data_from_tags(tags):
    for tag in tags:
        if len(tag[0].get_text()) == 3: # check if currency symbol = XXX
            yield tag[0].get_text(), tag[1].get_text(), tag[2].get_text()

def combine_data_with_dates(date, data_from_tags):
    for piece in data_from_tags:
        (currency, name, rate) = piece # unpacking tuple
        rates.append([date, currency, name, rate])
    return rates

def to_data_frame(rates):
    df = pd.DataFrame(rates, columns=['date', 'code', 'name', 'rate'])
    df['rate'] = df['rate'].astype(float)

    if not against_currency == 'ALL':
        df = df[df['code'] == against_currency]

    print(df)

    # df.to_csv(r'Data\currency_rates\data.csv', index=False)  # the name to be updated

def prepare_dates():
    days = [('0' + str(day))[-2:] for day in range(1, 32)] # it stops at 31
    months = [('0' + str(month))[-2:] for month in range(month_start, month_stop + 1)]
    years = [year for year in range(year_start, year_stop + 1)]

    for year in years:
        for month in months:
            for day in days:
                date = f'{year}-{month}-{day}' # yyyy-mm-dd - produces fake dates like 2020-02-31 however programm ignores it later
                dates.append(date)

def main():

    if not dates:
        prepare_dates()

    for date in dates:
        soup_content = get_page_content(date)
        if soup_content.find_all(tag): # check if tags found - there can be no rates for fake dates like 2020-02-31
            tags = chunk_data(soup_content.find_all(tag), 4)
            data_from_tags = extract_data_from_tags(tags)
            rates = combine_data_with_dates(date, data_from_tags)

    print_list_out(rates)
    to_data_frame(rates)


if __name__ == '__main__':
    main()
