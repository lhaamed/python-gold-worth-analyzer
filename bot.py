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

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

        emami_coin_response = requests.get("https://www.tgju.org/profile/sekee", headers=headers)
        emami_coin_soup = BeautifulSoup(emami_coin_response.content, 'html.parser')

        gold_18k_response = requests.get("https://www.tgju.org/profile/geram18", headers=headers)
        gold_18k_soup = BeautifulSoup(gold_18k_response.content, 'html.parser')


        gold_18k_elem = gold_18k_soup.find('span', {'data-col': 'info.last_trade.PDrCotVal'})        
        if gold_18k_elem:
            price_text = gold_18k_elem.text  # خروجی: "146,000,000"
            gold_price_18k = int(price_text.replace(',', ''))  # خروجی: 146000000
        else:
            raise ValueError("tag not found")

        # استخراج قیمت سکه امامی
        coin_emami_elem = emami_coin_soup.find('span', {'data-col': 'info.last_trade.PDrCotVal'})

        if coin_emami_elem:
            price_text = coin_emami_elem.text  # خروجی: "146,000,000"
            coin_price = int(price_text.replace(',', ''))  # خروجی: 146000000
        else:
            raise ValueError("tag not found")

        
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
