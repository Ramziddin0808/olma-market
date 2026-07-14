from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Izoh(models.Model):
    market = models.ForeignKey(
        'market_databaze', 
        on_delete=models.CASCADE, 
        related_name='izohlar'
    )
    ism = models.CharField(max_length=100)
    matn = models.TextField()
    rating = models.IntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(5)])
    rasm = models.ImageField(upload_to='izohlar/', blank=True, null=True) # Izoh rasmi uchun
    vaqt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ism} - {self.rating} ⭐"  
    
class market_databaze(models.Model):
    title = models.CharField(max_length=250)
    SIFATI = (
        ('yaxshi', 'yaxshi'),
        ("o'rtacha","o'rtacha"),
        ('yomon','yomon')
    )
    maxsulotlar_turi = (
        ('Elektronika','Elektronika'),
        ('musiqa','musiqa'),
        ('mebel','mebel')
    )
    
    sifati = models.CharField(choices=SIFATI,max_length=250)
    maxsulot = models.CharField(choices=maxsulotlar_turi,max_length=250)
    description = models.TextField()
    narx = models.IntegerField(default=0,verbose_name="narxi")
    image = models.ImageField(upload_to="images/",blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.title

class User(AbstractUser):
    username = models.CharField(max_length=150,unique=True)
    password = models.CharField(max_length=8)
    phone = models.CharField(max_length=20,unique=True)
    avatar = models.ImageField(upload_to='avatar/',null=True,blank=True)

class MarketImage(models.Model):
    market = models.ForeignKey(
        market_databaze,
        related_name='gallery',
        on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to='market_images/gallery/')

    def __str__(self):
        return f"{self.market.title} - imageJ"
    
class saralangan(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="saralanganlar")
    mahsulot = models.ForeignKey(market_databaze, on_delete=models.CASCADE, related_name="saralangan_mahsulotlar")
    qo_shilgan_vaqt = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'mahsulot') # Bitta mahsulotni ikki marta saralay olmaslik uchun

    def __str__(self):
        return f"{self.user.username} - {self.mahsulot.title}"