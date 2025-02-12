import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

logger = logging.getLogger(__name__)

def send_price_alert_email(to_email, product_name, current_price, target_price, url):
    """Send a price drop alert email with HTML formatting"""
    
    from_email = "arif.cloud.july@gmail.com"
    from_password = "guea cnxg wuqf ekfv"
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "🎯 Price Drop Alert! Your Target Price Has Been Reached"
        msg['From'] = from_email
        msg['To'] = to_email

        savings = float(target_price) - float(current_price)
        percentage = (savings / float(target_price)) * 100

        html = f"""
        <html>
            <head>
                <style>
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        font-family: Arial, sans-serif;
                        padding: 20px;
                        background-color: #f9f9f9;
                    }}
                    .header {{
                        background: linear-gradient(45deg, #00ff87, #60efff);
                        color: #000;
                        padding: 20px;
                        text-align: center;
                        border-radius: 10px 10px 0 0;
                    }}
                    .content {{
                        background: white;
                        padding: 20px;
                        border-radius: 0 0 10px 10px;
                        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                    }}
                    .price-box {{
                        background: #f5f5f5;
                        padding: 15px;
                        margin: 10px 0;
                        border-radius: 5px;
                        text-align: center;
                    }}
                    .button {{
                        display: inline-block;
                        padding: 10px 20px;
                        background: linear-gradient(45deg, #00ff87, #60efff);
                        color: #000;
                        text-decoration: none;
                        border-radius: 25px;
                        margin-top: 20px;
                    }}
                    .savings {{
                        color: #00c853;
                        font-weight: bold;
                        font-size: 1.2em;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎯 Price Drop Alert!</h1>
                    </div>
                    <div class="content">
                        <h2>Great news! Your target price has been reached!</h2>
                        
                        <h3>Product Details:</h3>
                        <p><strong>{product_name}</strong></p>
                        
                        <div class="price-box">
                            <p>Current Price: <strong>₹{current_price:,.2f}</strong></p>
                            <p>Your Target: ₹{target_price:,.2f}</p>
                            <p class="savings">You Save: ₹{savings:,.2f} ({percentage:.1f}%)</p>
                        </div>
                        
                        <p>Don't miss out on this opportunity!</p>
                        
                        <center>
                            <a href="{url}" class="button">Buy Now!</a>
                        </center>
                        
                        <p style="margin-top: 30px; font-size: 0.9em; color: #666;">
                            This is an automated message from Price Drop Alert System.<br>
                            If you didn't request this alert, please ignore this email.
                        </p>
                    </div>
                </div>
            </body>
        </html>
        """

        msg.attach(MIMEText(html, 'html'))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(from_email, from_password)
            server.send_message(msg)
        
        logger.info(f"Price alert email sent successfully to {to_email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send price alert email: {str(e)}")
        return False

def send_confirmation_email(to_email, product_name, current_price, target_price, url):
    """Send a tracking confirmation email with HTML formatting"""
    
    from_email = "arif.cloud.july@gmail.com"
    from_password = "guea cnxg wuqf ekfv"
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "✅ Price Tracking Started Successfully"
        msg['From'] = from_email
        msg['To'] = to_email

        html = f"""
        <html>
            <head>
                <style>
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        font-family: Arial, sans-serif;
                        padding: 20px;
                        background-color: #f9f9f9;
                    }}
                    .header {{
                        background: linear-gradient(45deg, #2196F3, #00BCD4);
                        color: white;
                        padding: 20px;
                        text-align: center;
                        border-radius: 10px 10px 0 0;
                    }}
                    .content {{
                        background: white;
                        padding: 20px;
                        border-radius: 0 0 10px 10px;
                        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                    }}
                    .price-box {{
                        background: #f5f5f5;
                        padding: 15px;
                        margin: 10px 0;
                        border-radius: 5px;
                        text-align: center;
                    }}
                    .target {{
                        color: #2196F3;
                        font-weight: bold;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>✅ Price Tracking Confirmed</h1>
                    </div>
                    <div class="content">
                        <h2>We're tracking prices for you!</h2>
                        
                        <h3>Product Details:</h3>
                        <p><strong>{product_name}</strong></p>
                        
                        <div class="price-box">
                            <p>Current Price: ₹{current_price:,.2f}</p>
                            <p class="target">Your Target: ₹{target_price:,.2f}</p>
                        </div>
                        
                        <p>We'll notify you as soon as the price drops below your target!</p>
                        
                        <p style="margin-top: 30px; font-size: 0.9em; color: #666;">
                            This is an automated message from Price Drop Alert System.<br>
                            We'll keep tracking prices for you 24/7.
                        </p>
                    </div>
                </div>
            </body>
        </html>
        """

        msg.attach(MIMEText(html, 'html'))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(from_email, from_password)
            server.send_message(msg)
        
        logger.info(f"Confirmation email sent successfully to {to_email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send confirmation email: {str(e)}")
        return False
