import requests
import os
from bs4 import BeautifulSoup

# مقادیر مرزی تحلیل
UPPER_BOUND = 4.4
LOWER_BOUND = 3.8

# توکن ربات و آیدی چت (یا @channelusername)

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')


def get_prices():
    try:
        url = "https://www.tgju.org/"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        # استخراج قیمت طلای 18 عیار
        gold_18k_elem = soup.find('tr', {'data-market-row': 'price_geram18'})
        gold_price_18k = float(gold_18k_elem.find('td', {'data-col': 'close'}).text.replace(',', ''))

        # استخراج قیمت سکه امامی
        coin_emami_elem = soup.find('tr', {'data-market-row': 'price_emami'})
        coin_price = float(coin_emami_elem.find('td', {'data-col': 'close'}).text.replace(',', ''))

        return gold_price_18k, coin_price
    except Exception as e:
        return None, None


def gold_to_coin_ratio(gold_price_18k, coin_price):
    if gold_price_18k is None or coin_price is None:
        return None, "خطا در استخراج قیمت‌ها"
    
    ratio = gold_price_18k / coin_price
    
    # آستانه‌ها
    if ratio > 0.00032:
        recommendation = "خرید طلای خام بهتر است (حباب سکه بالا)"
    elif ratio < 0.00028:
        recommendation = "خرید سکه بهتر است (حباب سکه کم)"
    else:
        recommendation = "تصمیم بستگی به استراتژی شما دارد (حباب متعادل)"
    
    return ratio, recommendation

def send_to_telegram(message):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    data = {
        'chat_id': CHANNEL_ID,
        'text': message
    }
    requests.post(url, data=data)


def main():
    gold_price_18k, coin_price = get_prices()
    ratio, recommendation = gold_to_coin_ratio(gold_price_18k, coin_price)
    
    send_to_telegram(recommendation)



if __name__ == '__main__':
    main()
