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
        recommendation = "خرید طلای خام بهتر است (حباب سکه بالا) " + f"{ratio:.2f}"
    elif ratio < 1.05:
        recommendation = "خرید سکه بهتر است (حباب سکه کم) " + str(ratio)
    else:
        recommendation = "تصمیم بستگی به استراتژی شما دارد (حباب متعادل) " + f"{ratio:.2f}"
    
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



def send_to_telegram(message):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    
    data = {
        'chat_id': CHANNEL_ID,
        'text': message
    }
    requests.post(url, data=data)

def main():

    gold18_gram_price = extract_price_out_of_url("https://www.tgju.org/profile/geram18")
    gold24_gram_price = extract_price_out_of_url("https://www.tgju.org/profile/geram24")

    
    quarter_coin_price = extract_price_out_of_url("https://www.tgju.org/profile/rob")
    half_coin_price = extract_price_out_of_url("https://www.tgju.org/profile/nim")
    geram_coin_price = extract_price_out_of_url("https://www.tgju.org/profile/gerami")
    bahar_azadi_coin_price = extract_price_out_of_url("https://www.tgju.org/profile/sekeb")
    emami_coin_price = extract_price_out_of_url("https://www.tgju.org/profile/sekee")
    emami_coin_bubble_price = extract_price_out_of_url("https://www.tgju.org/profile/coin_blubber")
    ounce_price = extract_price_out_of_url("https://www.tgju.org/profile/ons")
    
    usd_price = extract_price_out_of_url("https://www.tgju.org/profile/price_dollar_rl")
    euro_price = extract_price_out_of_url("https://www.tgju.org/profile/price_eur")
    gbp_price = extract_price_out_of_url("https://www.tgju.org/profile/price_gbp")
    aed_price = extract_price_out_of_url("https://www.tgju.org/profile/price_aed")
    
    ratio, recommendation = gold_to_coin_ratio(gold18_gram_price, emami_coin_price)

    message = (
        f"💰 قیمت‌ها امروز:\n"
        f"• هرگرم طلا ۱۸عیار: {(gold18_gram_price//10):,} تومن\n"
        f"• هرگرم طلا ۲۴عیار: {(gold24_gram_price//10):,} تومن\n"
        f"\n"
        f"• ربع سکه: {(quarter_coin_price//10):,} تومن\n"
        f"• نیم سکه: {(half_coin_price//10):,} تومن\n"
        f"• سکه گرمی: {(geram_coin_price//10):,} تومن\n"
        f"• سکه بهارآزادی: {(bahar_azadi_coin_price//10):,} تومن\n"
        f"• سکه امامی: {(emami_coin_price//10):,} تومن\n"
        f"• حباب سکه امامی: {(emami_coin_bubble_price//10):,} تومن\n"
        f"• اونس جهانی: {(ounce_price):,} دلار آمریکا\n"
        f"\n"
        f"• دلار آمریکا: {(usd_price):,} تومن\n"
        f"• یورو: {(euro_price):,} تومن\n"
        f"• پوند انگلیس: {(gbp_price):,} تومن\n"
        f"• درهم امارات: {(aed_price):,} تومن\n"
        f"\n"
        f"\n📌 توصیه:\n{recommendation}"
    )
    
    send_to_telegram(message)

if __name__ == '__main__':
    main()
