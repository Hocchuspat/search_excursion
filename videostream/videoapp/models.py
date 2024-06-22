# models.py
from django.contrib.auth.models import User
from django.db import models

class Excursion(models.Model):
    title = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    customers_review_rating = models.FloatField()
    image_big = models.URLField()
    url = models.URLField()

    def __str__(self):
        return self.title

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    excursion = models.ForeignKey(Excursion, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'excursion')

    def __str__(self):
        return f'{self.user.username} - {self.excursion.title}'
