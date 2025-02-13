import tweepy
import schedule
import time
from openai import OpenAI
from datetime import datetime
import json
import os
import logging
from dotenv import load_dotenv
from flask import Flask, render_template, jsonify
import threading

# Logging dizinini kontrol et ve oluştur
log_directory = "logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# Logging ayarları
logging.basicConfig(
    filename=os.path.join(log_directory, 'twitter_bot.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Çevre değişkenlerini yükle
load_dotenv()

# API anahtarlarının varlığını kontrol et
required_env_vars = [
    'TWITTER_BEARER_TOKEN',
    'TWITTER_API_KEY',
    'TWITTER_API_SECRET',
    'TWITTER_ACCESS_TOKEN',
    'TWITTER_ACCESS_TOKEN_SECRET',
    'OPENAI_API_KEY'
]

for var in required_env_vars:
    if not os.getenv(var):
        logging.error(f"Eksik çevre değişkeni: {var}")
        raise EnvironmentError(f"{var} çevre değişkeni bulunamadı")

try:
    # Twitter API kimlik bilgileri
    client = tweepy.Client(
        bearer_token=os.getenv('TWITTER_BEARER_TOKEN'),
        consumer_key=os.getenv('TWITTER_API_KEY'),
        consumer_secret=os.getenv('TWITTER_API_SECRET'),
        access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
        access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
    )

    # OpenAI istemcisi
    openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
except Exception as e:
    logging.error(f"API istemcileri oluşturulurken hata: {e}")
    raise

def get_trending_tweets():
    """Trend olan tweetleri çeker"""
    try:
        logging.info("Trend tweetler alınıyor...")
        us_trends = client.get_trends(id="23424977")
        world_trends = client.get_trends(id="1")
        
        all_tweets = []
        for trend in us_trends.data + world_trends.data:
            logging.info(f"'{trend.name}' trendi için tweetler aranıyor")
            tweets = client.search_recent_tweets(
                query=trend.name,
                max_results=10,
                tweet_fields=['author_id', 'created_at', 'text']
            )
            if tweets.data:
                all_tweets.extend(tweets.data)
        
        logging.info(f"Toplam {len(all_tweets)} tweet toplandı")
        return all_tweets
    except Exception as e:
        logging.error(f"Tweet çekerken hata: {str(e)}", exc_info=True)
        return None

def analyze_and_respond(tweets):
    """Tweetleri analiz eder ve yanıt oluşturur"""
    try:
        tweet_content = "\n".join([tweet.text for tweet in tweets])
        logging.info("GPT analizi başlatılıyor")
        
        prompt = f"""
        Sen {os.getenv('BOT_NAME')} adlı bir Twitter botusun.
        Kişiliğin: {os.getenv('BOT_PERSONALITY')}
        
        Aşağıdaki trendler hakkında kişiliğine uygun bir yorum yap.
        Dil: {os.getenv('BOT_LANGUAGE')}
        Maximum 280 karakter kullan.
        
        Trendler:
        {tweet_content}
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        
        generated_response = response.choices[0].message.content
        logging.info(f"GPT yanıtı oluşturuldu: {generated_response}")
        return generated_response
    except Exception as e:
        logging.error(f"GPT analizi sırasında hata: {str(e)}", exc_info=True)
        return None

def post_tweet(response):
    """Oluşturulan yanıtı tweet olarak paylaşır"""
    try:
        client.create_tweet(text=response)
        logging.info(f"Tweet başarıyla paylaşıldı: {response}")
    except Exception as e:
        logging.error(f"Tweet paylaşırken hata: {str(e)}", exc_info=True)

def run_bot():
    """Ana bot fonksiyonu"""
    try:
        logging.info("Bot çalışması başladı")
        tweets = get_trending_tweets()
        
        if tweets:
            response = analyze_and_respond(tweets)
            if response:
                post_tweet(response)
        logging.info("Bot çalışması tamamlandı")
    except Exception as e:
        logging.error(f"Bot çalışması sırasında beklenmeyen hata: {str(e)}", exc_info=True)

app = Flask(__name__)
bot_thread = None
is_bot_running = False

def start_bot():
    global is_bot_running
    logging.info("Bot başlatıldı")
    try:
        schedule.every(3).hours.do(run_bot)
        is_bot_running = True
        
        run_bot()  # İlk çalıştırma
        
        while is_bot_running:
            try:
                schedule.run_pending()
                time.sleep(60)
            except Exception as e:
                logging.error(f"Zamanlayıcı döngüsünde hata: {str(e)}", exc_info=True)
                time.sleep(300)
    except Exception as e:
        logging.error(f"Kritik hata: {str(e)}", exc_info=True)
    
    is_bot_running = False

@app.route('/')
def index():
    return render_template('index.html', is_running=is_bot_running)

@app.route('/toggle_bot')
def toggle_bot():
    global bot_thread, is_bot_running
    
    if not is_bot_running:
        # Botu başlat
        is_bot_running = True
        bot_thread = threading.Thread(target=start_bot)
        bot_thread.start()
        return jsonify({"status": "started"})
    else:
        # Botu durdur
        is_bot_running = False
        return jsonify({"status": "stopped"})

if __name__ == "__main__":
    app.run(debug=True, port=5000) 