from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.cache import cache
from bs4 import BeautifulSoup
from decimal import Decimal
import requests
import logging
import threading
import time
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from django.http import JsonResponse

from .forms import PriceTrackForm
from .models import PriceTrack

# Set up logging
logger = logging.getLogger(__name__)

def get_product_details(url):
    try:
        # Set up headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }

        # Create a session and set retry strategy
        session = requests.Session()
        retries = 3
        
        for attempt in range(retries):
            try:
                # Handle URL redirects with timeout
                response = session.get(url, headers=headers, allow_redirects=True, timeout=10)
                response.raise_for_status()  # Raise an exception for bad status codes
                break
            except requests.RequestException as e:
                if attempt == retries - 1:  # Last attempt
                    logger.error(f"Failed to fetch URL {url} after {retries} attempts: {str(e)}")
                    return None, None
                time.sleep(2)  # Wait before retrying
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try multiple selectors for price and name as Flipkart's structure might vary
        price_selectors = [
            '._30jeq3._16Jk6d',  # Common price selector
            '.Nx9bqj.CxhGGd',    # Alternative price selector
            '._30jeq3',          # Basic price selector
            '.CEmiEU ._30jeq3',  # Price with discount
            '[data-price]',      # Data attribute price
            '.dyC4hf .CEmiEU',   # Another price container
            '._16Jk6d'           # Simple price class
        ]
        
        name_selectors = [
            '.B_NuCI',           # Common product name selector
            '.VU-ZEz',           # Alternative name selector
            '._35KyD6',          # Basic name selector
            '.yhB1nd span',      # Product title selector
            '[data-title]',      # Data attribute title
            '.G6XhRU',          # Another title class
            'h1'                # Fallback to h1 tag
        ]
        
        # Try to find price using different selectors
        price = None
        for selector in price_selectors:
            price_element = soup.select_one(selector)
            if price_element:
                # Try to get price from data attribute first
                price_text = price_element.get('data-price', '') or price_element.text.strip()
                # Remove currency symbols and clean the string
                price_text = re.sub(r'[^\d,.]', '', price_text)
                price_match = re.findall(r'[\d,]+\.?\d*', price_text)
                if price_match:
                    try:
                        # Handle both comma and dot as decimal separator
                        price_str = price_match[0].replace(',', '')
                        price = float(price_str)
                        break
                    except ValueError:
                        continue
        
        # Try to find product name using different selectors
        name = None
        for selector in name_selectors:
            name_element = soup.select_one(selector)
            if name_element:
                # Try to get name from data attribute first
                name = name_element.get('data-title', '') or name_element.text.strip()
                if name:
                    # Clean the name string
                    name = re.sub(r'\s+', ' ', name).strip()
                    break
        
        if not price or not name:
            logger.error(f"Failed to extract price or name from {url}")
            return None, None
            
        return price, name
        
    except Exception as e:
        logger.error(f"Error processing URL {url}: {str(e)}")
        return None, None

def get_price(url):
    price, _ = get_product_details(url)
    return price

def send_email(subject, body, to_email):
    from_email = "arif.cloud.july@gmail.com"  
    from_password = "guea cnxg wuqf ekfv"  
    try:
        # Create HTML version of the email
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #2c3e50;">{subject}</h2>
                <div style="color: #34495e; line-height: 1.6;">
                    {body.replace('\n', '<br>')}
                </div>
                <p style="color: #7f8c8d; margin-top: 20px;">
                    This is an automated message from Price Drop Alert
                </p>
            </body>
        </html>
        """

        # Create message container
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = to_email

        # Add plain text and HTML parts
        text_part = MIMEText(body, 'plain')
        html_part = MIMEText(html_content, 'html')
        msg.attach(text_part)
        msg.attach(html_part)

        # Connect to SMTP server with explicit timeout
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=30)
        server.login(from_email, from_password)
        
        # Send email and log success
        server.send_message(msg)
        logger.info(f"Successfully sent email to {to_email}")
        
        server.quit()
        return True
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP Authentication failed: {e}")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error occurred: {e}")
        return False
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        return False

def track_price(url, target_price, check_interval, to_email, price_track_id):
    logger.info(f"Starting price tracking for {url} with target price {target_price}")
    while True:
        try:
            price_track = PriceTrack.objects.get(id=price_track_id)
            if price_track.progress == 'complete':
                logger.info(f"Tracking completed for {url}")
                break

            current_price, product_name = get_product_details(url)
            if current_price is not None:
                current_price_decimal = Decimal(str(current_price))
                target_price_decimal = Decimal(str(target_price))

                logger.info(f"Current price for {url}: {current_price_decimal}, Target: {target_price_decimal}")

                if current_price_decimal <= target_price_decimal:
                    subject = "Price Drop Alert! 🎉"
                    body = f"""Good news! The price has dropped!

Product: {product_name}
Current Price: ₹{current_price_decimal:,.2f}
Your Target: ₹{target_price_decimal:,.2f}
You Save: ₹{target_price_decimal - current_price_decimal:,.2f}

Check the product here: {url}"""

                    if send_email(subject, body, to_email):
                        logger.info(f"Price drop email sent for {url}")
                    else:
                        logger.error(f"Failed to send price drop email for {url}")

                    price_track.progress = 'complete'
                    price_track.save()
                    break
            else:
                logger.warning(f"Failed to get current price for {url}")

        except Exception as e:
            logger.error(f"Error in price tracking thread: {e}")

        time.sleep(check_interval)

def track_price_view(request):
    if request.method == 'POST':
        form = PriceTrackForm(request.POST)
        if form.is_valid():
            try:
                price_track = form.save(commit=False)
                price_track.progress = 'tracking'
                
                # Get initial product details
                current_price = get_price(price_track.url_link)
                if current_price is None:
                    return JsonResponse({
                        'success': False,
                        'error': 'Could not fetch product price. Please check the URL.'
                    })
                
                # Save the price track object
                price_track.save()
                
                # Send confirmation email
                subject = "Price Tracking Started!"
                body = f"""Your price tracking request has been received:

URL: {price_track.url_link}
Current Price: ₹{current_price:,.2f}
Target Price: ₹{price_track.target_price:,.2f}

You will be notified when the price drops below your target price."""
                
                email_sent = send_email(subject, body, price_track.email)
                
                # Start tracking thread
                tracking_thread = threading.Thread(
                    target=track_price,
                    args=(price_track.url_link, price_track.target_price, 3600, price_track.email, price_track.id)
                )
                tracking_thread.daemon = True
                tracking_thread.start()
                
                # Return JSON response for AJAX request
                return JsonResponse({
                    'success': True,
                    'email': price_track.email,
                    'current_price': float(current_price),
                    'target_price': float(price_track.target_price)
                })
                
            except Exception as e:
                logger.error(f"Error in track_price_view: {e}")
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Invalid form data. Please check your inputs.'
            })
    
    # For GET requests, just render the form
    return render(request, 'tracker/track_price.html', {'form': PriceTrackForm()})