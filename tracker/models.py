from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

class PriceTrack(models.Model):
    PROGRESS_CHOICES = [
        ('tracking', 'Tracking'),
        ('complete', 'Complete'),
        ('error', 'Error')
    ]

    url_link = models.URLField(max_length=1000)  
    target_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    email = models.EmailField()
    progress = models.CharField(
        max_length=20,
        choices=PROGRESS_CHOICES,
        default='tracking'
    )
    last_checked_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    product_name = models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product_name or 'Product'} - Target: ₹{self.target_price}"

    class Meta:
        ordering = ['-created_at']