from django import forms
from .models import PriceTrack
import re
import requests
from urllib.parse import urlparse, parse_qs

class PriceTrackForm(forms.ModelForm):
    class Meta:
        model = PriceTrack
        fields = ['url_link', 'target_price', 'email']
        widgets = {
            'url_link': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Flipkart product URL'
            }),
            'target_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your desired price',
                'min': '1',
                'step': '1'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email for notifications'
            })
        }

    def clean_url_link(self):
        url = self.cleaned_data.get('url_link', '').strip()
        
        # Handle shortened URLs
        if 'dl.flipkart.com' in url or 'bit.ly' in url:
            try:
                session = requests.Session()
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
                }
                response = session.head(url, headers=headers, allow_redirects=True)
                url = response.url
            except Exception as e:
                raise forms.ValidationError('Unable to process the shortened URL. Please use the full Flipkart product URL')
        
        # Parse the URL
        parsed_url = urlparse(url)
        
        # Check if it's a Flipkart URL
        if not any(domain in parsed_url.netloc for domain in ['flipkart.com', 'www.flipkart.com']):
            raise forms.ValidationError('Please enter a valid Flipkart URL')
        
        # Clean the URL by removing unnecessary parameters
        query_params = parse_qs(parsed_url.query)
        important_params = ['pid']  # Keep only important parameters
        cleaned_query = '&'.join(f"{k}={v[0]}" for k, v in query_params.items() if k in important_params)
        
        # Reconstruct the clean URL
        clean_url = f"https://www.flipkart.com{parsed_url.path}"
        if cleaned_query:
            clean_url += f"?{cleaned_query}"
            
        return clean_url

    def clean_target_price(self):
        price = self.cleaned_data.get('target_price')
        if price and price <= 0:
            raise forms.ValidationError('Target price must be greater than 0')
        return price

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("Please enter a valid email address")
        return email