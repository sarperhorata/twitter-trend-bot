import tweepy
import schedule
import time
from openai import OpenAI
from datetime import datetime
import json
import os
import logging
from dotenv import load_dotenv
from twitter_bot.config import Config, TwitterAccount
from flask import Flask, request, jsonify, render_template, redirect
from auth import requires_auth
import secrets
from werkzeug.security import generate_password_hash
import threading
from functools import wraps

# Create logs directory if it doesn't exist
log_directory = "logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# Logging settings
logging.basicConfig(
    filename=os.path.join(log_directory, 'twitter_bot.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(16))

# Define global variables
bot_thread = None
is_bot_running = False
bot = None

class TwitterBot:
    def __init__(self):
        load_dotenv()
        self.config = Config.from_env()
        self.setup_clients()
        
    def setup_clients(self):
        """Create separate client for each account"""
        self.clients = []
        for account in self.config.accounts:
            try:
                client = tweepy.Client(
                    bearer_token=account.bearer_token,
                    consumer_key=account.api_key,
                    consumer_secret=account.api_secret,
                    access_token=account.access_token,
                    access_token_secret=account.access_token_secret
                )
                self.clients.append(client)
            except Exception as e:
                logging.error(f"Client oluşturulurken hata: {str(e)}", exc_info=True)
        
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    def get_trending_tweets(self):
        """Fetch trending tweets from USA"""
        current_account = self.config.get_current_account()
        
        if current_account.remaining_views <= 0:
            logging.info("Görüntüleme limiti doldu, hesap değiştiriliyor...")
            current_account = self.config.switch_account()
            
        try:
            client = self.clients[self.config.current_account_index]
            logging.info("ABD trendleri alınıyor...")
            
            # Sadece ABD trendlerini al
            trends = client.get_trends(id="23424977")  # ABD WOEID
            
            all_tweets = []
            for trend in trends.data[:5]:  # İlk 5 trend ile sınırla
                logging.info(f"'{trend.name}' trendi için tweetler aranıyor")
                tweets = client.search_recent_tweets(
                    query=trend.name,
                    max_results=10,
                    tweet_fields=['author_id', 'created_at', 'text']
                )
                if tweets.data:
                    all_tweets.extend(tweets.data)
            
            # Limit güncelle
            current_account.remaining_views -= 1
            
            logging.info(f"Toplam {len(all_tweets)} tweet toplandı")
            return all_tweets
            
        except Exception as e:
            logging.error(f"Tweet çekerken hata: {str(e)}", exc_info=True)
            return None

    def analyze_and_respond(self, tweets):
        """Analyze tweets and generate response"""
        try:
            tweet_content = "\n".join([tweet.text for tweet in tweets])
            logging.info("Starting GPT analysis")
            
            prompt = f"""
            You are a Twitter bot named {self.config.bot_name}.
            Personality: {self.config.bot_personality}
            
            Create a witty comment about the following trends.
            Language: {self.config.bot_language}
            Maximum 280 characters.
            
            Trends:
            {tweet_content}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}]
            )
            
            generated_response = response.choices[0].message.content
            logging.info(f"GPT response generated: {generated_response}")
            return generated_response
        except Exception as e:
            logging.error(f"Error during GPT analysis: {str(e)}", exc_info=True)
            return None

    def post_tweet(self, response):
        """Post the generated response as a tweet (always from first account)"""
        posting_account = self.config.get_posting_account()
        
        if posting_account.remaining_tweets <= 0:
            logging.error("Tweet limit reached for main account")
            return
        
        try:
            client = self.clients[0]  # Her zaman ilk hesabın client'ını kullan
            client.create_tweet(text=response)
            posting_account.remaining_tweets -= 1
            logging.info(f"Tweet successfully posted: {response}")
        except Exception as e:
            logging.error(f"Error while posting tweet: {str(e)}", exc_info=True)

    def run_bot(self):
        """Main bot function"""
        try:
            logging.info("Bot operation started")
            tweets = self.get_trending_tweets()
            
            if tweets:
                response = self.analyze_and_respond(tweets)
                if response:
                    self.post_tweet(response)
            logging.info("Bot operation completed")
        except Exception as e:
            logging.error(f"Unexpected error during bot operation: {str(e)}", exc_info=True)

def start_bot():
    """Function to start the bot"""
    global is_bot_running, bot
    
    logging.info("Bot başlatıldı")
    try:
        if bot is None:
            bot = TwitterBot()
            
        # Çalışma aralığını ayarla
        schedule.every(int(os.getenv('CHECK_INTERVAL', 3))).hours.do(bot.run_bot)
        
        # İlk çalıştırma
        bot.run_bot()
        
        # Zamanlayıcı döngüsü
        while is_bot_running:
            try:
                schedule.run_pending()
                time.sleep(60)
            except Exception as e:
                logging.error(f"Zamanlayıcı döngüsünde hata: {str(e)}", exc_info=True)
                time.sleep(300)  # Hata durumunda 5 dakika bekle
    except Exception as e:
        logging.error(f"Kritik hata: {str(e)}", exc_info=True)
        is_bot_running = False

# Simple decorator for rate limiting
def rate_limit(func):
    last_requests = {}
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        ip = request.remote_addr
        current_time = time.time()
        
        if ip in last_requests:
            time_passed = current_time - last_requests[ip]
            if time_passed < 1:  # 1 saniye bekleme süresi
                return jsonify({"error": "Too many requests"}), 429
        
        last_requests[ip] = current_time
        return func(*args, **kwargs)
    
    return wrapper

# Protect all routes with auth
@app.route('/')
@requires_auth
def index():
    return render_template('index.html', is_running=is_bot_running)

@app.route('/toggle_bot')
@requires_auth
@rate_limit
def toggle_bot():
    global bot_thread, is_bot_running
    
    if not is_bot_running:
        is_bot_running = True
        bot_thread = threading.Thread(target=start_bot)
        bot_thread.start()
        return jsonify({"status": "started"})
    else:
        is_bot_running = False
        if bot_thread and bot_thread.is_alive():
            bot_thread.join(timeout=1)  # Thread'in düzgün kapanmasını bekle
        return jsonify({"status": "stopped"})

@app.route('/get_logs')
@requires_auth
@rate_limit
def get_logs():
    try:
        with open(os.path.join(log_directory, 'twitter_bot.log'), 'r') as f:
            logs = f.readlines()[-20:]
            return jsonify({"logs": "".join(logs)})
    except Exception as e:
        return jsonify({"logs": f"Loglar okunamadı: {str(e)}"})

# HTTPS redirect
@app.before_request
def before_request():
    if not request.is_secure and app.env != 'development':
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url, code=301)

if __name__ == "__main__":
    # Production'da debug mode'u kapat
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    
    # SSL sertifikası kullan (production'da)
    if not debug_mode:
        app.run(
            host='0.0.0.0',
            port=int(os.getenv('PORT', 5000)),
            ssl_context=('cert.pem', 'key.pem')
        )
    else:
        app.run(debug=True, port=5000) 