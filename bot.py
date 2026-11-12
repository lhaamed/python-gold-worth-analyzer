import requests # type: ignore
import os
from bs4 import BeautifulSoup # type: ignore



# توکن ربات و آیدی چت (یا @channelusername)
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')
TIMEOUT = 15

COIN_WEIGHT_G = 8.136      # وزن سکه امامی
COIN_PURITY = 0.900        # عیار ۹۰۰
GOLD18_PURITY = 0.750
BUBBLE_LOW, BUBBLE_HIGH = 5, 10   # درصد


session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Encoding': 'gzip, deflate',
})

def gold_to_coin_ratio(gold18_price, coin_price):
    # ارزش ذاتی = قیمت طلای خالص موجود در سکه (به معادل ۱۸ عیار)
    intrinsic = gold18_price * (COIN_WEIGHT_G * COIN_PURITY / GOLD18_PURITY)

    bubble = coin_price - intrinsic            # حباب مطلق (ریال)
    bubble_pct = bubble / intrinsic * 100      # حباب درصدی

    if bubble_pct > BUBBLE_HIGH:
        advice = "خرید طلای خام بهتر است (حباب سکه بالا)"
    elif bubble_pct < BUBBLE_LOW:
        advice = "خرید سکه بهتر است (حباب سکه کم)"
    else:
        advice = "تصمیم بستگی به استراتژی شما دارد (حباب متعادل)"

    recommendation = f"{advice}\nحباب: {int(bubble // 10):,} تومن ({bubble_pct:.1f}٪)"
    return bubble_pct, recommendation

def extract_integer_part(text, as_float=False):
    cleaned = text.replace(',', '').replace('٬', '').strip()
    return float(cleaned) if as_float else int(cleaned.split('.')[0])

def fetch_price(url, adapter):
    response = session.get(url, timeout=TIMEOUT)
    response.raise_for_status()
    return adapter(response.content)


def tgju_adapter(content, as_float=False):
    soup = BeautifulSoup(content, 'html.parser')
    element = soup.find('span', {'data-col': 'info.last_trade.PDrCotVal'})
    if not element:
        print(content[:500])
        raise ValueError("tgju: tag not found")
    return extract_integer_part(element.text, as_float)

def sarafiyaran_adapter(content):
    soup = BeautifulSoup(content, 'html.parser')
    h2 = soup.find('h2', string=lambda s: s and 'فروش' in s)
    if not h2:
        raise ValueError("sarafiyaran: h2 not found")
    h3 = h2.find_next('h3')
    if not h3:
        raise ValueError("sarafiyaran: h3 not found")
    return extract_integer_part(h3.get_text(strip=True))


def send_to_telegram(message):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    response = session.post(
        url,
        data={'chat_id': CHANNEL_ID, 'text': message},
        timeout=TIMEOUT,
    )
    response.raise_for_status()

def main():

    if not TOKEN or not CHANNEL_ID:
        raise SystemExit("TELEGRAM_TOKEN or CHANNEL_ID is not set")

    gold18_gram_price = fetch_price("https://www.tgju.org/profile/geram18", tgju_adapter)
    gold24_gram_price = fetch_price("https://www.tgju.org/profile/geram24", tgju_adapter)
    
    silver925_gram_price = fetch_price("https://www.tgju.org/profile/silver_925", tgju_adapter)
    silver999_gram_price = fetch_price("https://www.tgju.org/profile/silver_999", tgju_adapter)

    
    quarter_coin_price = fetch_price("https://www.tgju.org/profile/rob", tgju_adapter)
    half_coin_price = fetch_price("https://www.tgju.org/profile/nim", tgju_adapter)
    geram_coin_price = fetch_price("https://www.tgju.org/profile/gerami", tgju_adapter)
    bahar_azadi_coin_price = fetch_price("https://www.tgju.org/profile/sekeb", tgju_adapter)
    emami_coin_price = fetch_price("https://www.tgju.org/profile/sekee", tgju_adapter)
    emami_coin_bubble_price = fetch_price("https://www.tgju.org/profile/coin_blubber", tgju_adapter)
    ounce_price = fetch_price("https://www.tgju.org/profile/ons", lambda c: tgju_adapter(c, as_float=True))
    
    usd_price = fetch_price("https://www.tgju.org/profile/price_dollar_rl", tgju_adapter)
    euro_price = fetch_price("https://www.tgju.org/profile/price_eur", tgju_adapter)
    gbp_price = fetch_price("https://www.tgju.org/profile/price_gbp", tgju_adapter)
    aed_price = fetch_price("https://www.tgju.org/profile/price_aed", tgju_adapter)


    # yaran_shemsh5 = fetch_price("https://www.sarafiyaran.com/price/334/%D8%B4%D9%85%D8%B4-5-%DA%AF%D8%B1%D9%85%DB%8C-18-%D8%B9%DB%8C%D8%A7%D8%B1", sarafiyaran_adapter)

    
    ratio, recommendation = gold_to_coin_ratio(gold18_gram_price, emami_coin_price)

    message = (
        f"💰 قیمت‌ها امروز:\n"
        f"• هرگرم طلا ۱۸عیار: {(gold18_gram_price//10):,} تومن\n"
        f"• هرگرم طلا ۲۴عیار: {(gold24_gram_price//10):,} تومن\n"
        f"\n"
        f"• هرگرم نقره ۹۲۵: {(silver925_gram_price//10):,} تومن\n"
        f"• هرگرم نقره ۹۹۹: {(silver999_gram_price//10):,} تومن\n"
        f"\n"
        f"\n"
        f"• ربع سکه: {(quarter_coin_price//10):,} تومن\n"
        f"• نیم سکه: {(half_coin_price//10):,} تومن\n"
        f"• سکه گرمی: {(geram_coin_price//10):,} تومن\n"
        f"• سکه بهارآزادی: {(bahar_azadi_coin_price//10):,} تومن\n"
        f"• سکه امامی: {(emami_coin_price//10):,} تومن\n"
        f"• حباب سکه امامی: {(emami_coin_bubble_price//10):,} تومن\n"
        f"• اونس جهانی: {ounce_price:,.2f} دلار آمریکا\n"
        f"\n"
        f"• دلار آمریکا: {(usd_price//10):,} تومن\n"
        f"• یورو: {(euro_price//10):,} تومن\n"
        f"• پوند انگلیس: {(gbp_price//10):,} تومن\n"
        f"• درهم امارات: {(aed_price//10):,} تومن\n"
        f"\n"
        f"\n📌 توصیه:\n{recommendation}"
    )
    
    send_to_telegram(message)

if __name__ == '__main__':
    main()
