import requests
from bs4 import BeautifulSoup

# مقادیر مرزی تحلیل
UPPER_BOUND = 4.4
LOWER_BOUND = 3.8

# توکن ربات و آیدی چت (یا @channelusername)
BOT_TOKEN = 'YOUR_BOT_TOKEN'
CHAT_ID = 'YOUR_CHAT_ID_OR_CHANNEL'

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')

def get_prices():
    url = 'https://www.tgju.org/'
    headers = {'User-Agent': 'Mozilla/5.0'}

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    coin_element = soup.find('td', string='سکه امامی')
    gold_element = soup.find('td', string='طلای ۱۸ عیار')

    if not coin_element or not gold_element:
        return None, None

    coin_price = int(coin_element.find_next_sibling('td').text.replace(',', '').strip())
    gold_price = int(gold_element.find_next_sibling('td').text.replace(',', '').strip())

    return coin_price, gold_price

def analyze_market(coin_price, gold_price):
    if not coin_price or not gold_price:
        return "❌ خطا در دریافت قیمت‌ها از tgju.org"

    ratio = coin_price / gold_price
    message = f"💰 نسبت سکه به طلا: {ratio:.2f}\n"

    if ratio > UPPER_BOUND:
        message += "📉 سکه گرونه، بهتره طلا بخری."
    elif ratio < LOWER_BOUND:
        message += "📈 سکه ارزونه، فرصت برای خرید سکه."
    else:
        message += "⚖️ بازار نرماله. عجله نکن!"

    return message

def send_to_telegram(message):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    data = {
        'chat_id': CHANNEL_ID,
        'text': message
    }
    requests.post(url, data=data)

if __name__ == '__main__':
    coin, gold = get_prices()
    msg = analyze_market(coin, gold)
    send_to_telegram(msg)
