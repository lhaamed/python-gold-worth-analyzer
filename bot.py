import requests # type: ignore
import os
from bs4 import BeautifulSoup # type: ignore



# توکن ربات و آیدی چت (یا @channelusername)
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')


def get_prices():
    try:
        gold_price = extract_price_out_of_url("https://www.tgju.org/profile/geram18")
        coin_price = extract_price_out_of_url("https://www.tgju.org/profile/sekee")     
        
        return gold_price, coin_price
    except Exception as e:
        return None, None


def gold_to_coin_ratio(gold_price, coin_price):
    if gold_price is None or coin_price is None:
        return None, "خطا در استخراج قیمت‌ها"
    
    ratio = gold_price / coin_price
    
    # آستانه‌ها
    if ratio > 0.00032:
        recommendation = "خرید طلای خام بهتر است (حباب سکه بالا)"
    elif ratio < 0.00028:
        recommendation = "خرید سکه بهتر است (حباب سکه کم)"
    else:
        recommendation = "تصمیم بستگی به استراتژی شما دارد (حباب متعادل)"
    
    return ratio, recommendation

def send_to_telegram(gold_price,coin_price,recommendation):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'

    message = (
        f"💰 قیمت‌ها امروز:\n"
        f"• طلا: {gold_price:,} ریال\n"
        f"• سکه: {coin_price:,} ریال\n"
        f"\n📌 توصیه:\n{recommendation}"
    )
    
    data = {
        'chat_id': CHANNEL_ID,
        'text': message
    }
    requests.post(url, data=data)

def extract_price_out_of_url(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    element = soup.find('span', {'data-col': 'info.last_trade.PDrCotVal'})
    if element:
        price_text = element.text  # خروجی: "146,000,000"
        price = int(price_text.replace(',', ''))  # خروجی: 146000000
        return price
    else:
        raise ValueError("tag not found")


def main():
    gold_price, coin_price = get_prices()
    ratio, recommendation = gold_to_coin_ratio(gold_price, coin_price)
    
    send_to_telegram(gold_price, coin_price,recommendation)

if __name__ == '__main__':
    main()
