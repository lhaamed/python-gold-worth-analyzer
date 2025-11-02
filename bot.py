import requests # type: ignore
import os
from bs4 import BeautifulSoup # type: ignore



# توکن ربات و آیدی چت (یا @channelusername)
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')



def gold_to_coin_ratio(gold_price, coin_price):
    if gold_price is None or coin_price is None:
        return None, "خطا در استخراج قیمت‌ها"
    
    ratio = coin_price / (gold_price * 7.32);
    
    # آستانه‌ها
    if ratio > 1.10:
        recommendation = "خرید طلای خام بهتر است (حباب سکه بالا) " + f"{ratio:.3}"
    elif ratio < 1.05:
        recommendation = "خرید سکه بهتر است (حباب سکه کم) " + str(ratio)
    else:
        recommendation = "تصمیم بستگی به استراتژی شما دارد (حباب متعادل) " + f"{ratio:.3}"
    
    return ratio, recommendation

def extract_integer_part(text):
    cleaned = text.replace(',', '')
    integer_str = cleaned.split('.')[0]  # اگر نقطه نباشه، همون رشته رو برمی‌گردونه
    return int(integer_str)

def extract_price_out_of_url(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    element = soup.find('span', {'data-col': 'info.last_trade.PDrCotVal'})
    if element:
        price = extract_integer_part(element.text)
        return price
    else:
        raise ValueError("tag not found")



def send_to_telegram(gold_price,coin_price,coin_bubble_price,ounce_price,recommendation):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'

    message = (
        f"💰 قیمت‌ها امروز:\n"
        f"• طلا: {(gold_price//10):,} تومن\n"
        f"• سکه: {(coin_price//10):,} تومن\n"
        f"• حباب سکه: {(coin_bubble_price//10):,} تومن\n"
        f"• اونس جهانی: {(ounce_price):,} دلار آمریکا\n"
        f"\n📌 توصیه:\n{recommendation}"
    )
    
    data = {
        'chat_id': CHANNEL_ID,
        'text': message
    }
    requests.post(url, data=data)

def main():

    gold_price = extract_price_out_of_url("https://www.tgju.org/profile/geram18")
    coin_price = extract_price_out_of_url("https://www.tgju.org/profile/sekee")
    coin_bubble_price = extract_price_out_of_url("https://www.tgju.org/profile/coin_blubber")
    ounce_price = extract_price_out_of_url("https://www.tgju.org/profile/ons")
    ratio, recommendation = gold_to_coin_ratio(gold_price, coin_price)
    
    send_to_telegram(gold_price, coin_price,coin_bubble_price,ounce_price,recommendation)

if __name__ == '__main__':
    main()
