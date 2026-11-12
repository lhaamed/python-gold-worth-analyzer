import requests # type: ignore
import os
import time
import math
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
session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

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
    for attempt in range(1, 4):
        try:
            response = session.get(url, timeout=TIMEOUT)
        except (requests.Timeout, requests.ConnectionError):
            if attempt == 3:
                raise
            print(f"Connection failed, attempt {attempt}/3 ({url})", flush=True)
        else:
            response.raise_for_status()
            content = response.content
            details = (
                f"requested={url} final={response.url} "
                f"status={response.status_code} "
                f"content_type={response.headers.get('Content-Type', 'unknown')} "
                f"bytes={len(content)}"
            )
            if content.strip():
                try:
                    return adapter(content)
                except ValueError as exc:
                    raise ValueError(f"{exc} ({details})") from exc

            print(f"Empty response, attempt {attempt}/3 ({details})", flush=True)
            if attempt == 3:
                raise RuntimeError(f"Empty response after 3 attempts ({details})")

        time.sleep(2 ** (attempt - 1))



def tgju_adapter(content, as_float=False):
    soup = BeautifulSoup(content, 'html.parser')
    element = soup.find('span', {'data-col': 'info.last_trade.PDrCotVal'})
    if not element:
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

    price_groups = (
        (
            ("geram18", "هر گرم طلا ۱۸ عیار"),
            ("geram24", "هر گرم طلا ۲۴ عیار"),
            ("yaran_shemsh5", "شمش ۵ گرمی طلای ۱۸ عیار"),
        ),
        (
            ("silver_925", "هر گرم نقره ۹۲۵"),
            ("silver_999", "هر گرم نقره ۹۹۹"),
        ),
        (
            ("rob", "ربع سکه"),
            ("nim", "نیم سکه"),
            ("gerami", "سکه گرمی"),
            ("sekeb", "سکه بهار آزادی"),
            ("sekee", "سکه امامی"),
            ("coin_blubber", "حباب سکه امامی"),
            ("ons", "اونس جهانی"),
        ),
        (
            ("price_dollar_rl", "دلار آمریکا"),
            ("price_eur", "یورو"),
            ("price_gbp", "پوند انگلیس"),
            ("price_aed", "درهم امارات"),
        ),
    )

    prices = {}
    sections = []
    for group in price_groups:
        lines = []
        for symbol, label in group:
            url = f"https://www.tgju.org/profile/{symbol}"
            adapter = tgju_adapter
            if symbol == "ons":
                adapter = lambda content: tgju_adapter(content, as_float=True)
            elif symbol == "yaran_shemsh5":
                url = (
                    "https://www.sarafiyaran.com/price/334/"
                    "%D8%B4%D9%85%D8%B4-5-%DA%AF%D8%B1%D9%85%DB%8C-18-%D8%B9%DB%8C%D8%A7%D8%B1"
                )
                adapter = sarafiyaran_adapter

            try:
                price = fetch_price(url, adapter)
                if not math.isfinite(price):
                    raise ValueError("Price is not finite")
            except (requests.RequestException, ValueError, RuntimeError) as exc:
                print(f"Skipping {symbol}: {exc}", flush=True)
                continue

            prices[symbol] = price
            if symbol == "ons":
                lines.append(f"• {label}: {price:,.2f} دلار آمریکا")
            else:
                lines.append(f"• {label}: {price // 10:,} تومن")

        if lines:
            sections.append("\n".join(lines))

    if not sections:
        raise SystemExit("No prices available. No Telegram message was sent.")

    gold_price = prices.get("geram18")
    coin_price = prices.get("sekee")
    if gold_price is not None and gold_price > 0 and coin_price is not None:
        _, recommendation = gold_to_coin_ratio(gold_price, coin_price)
        sections.append(f"📌 توصیه:\n{recommendation}")

    message = "💰 قیمت‌ها امروز:\n" + "\n\n".join(sections)
    send_to_telegram(message)



if __name__ == '__main__':
    main()
