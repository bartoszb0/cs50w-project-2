from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models


class User(AbstractUser):
    pass

CATEGORY_CHOICES = [
    ('electronics', 'Electronics'),
    ('fashion', 'Fashion'),
    ('home', 'Home'),
    ('sports', 'Sports'),
    ('toys', 'Toys'),
]

class Auction(models.Model):
    # name
    name = models.CharField(max_length=50)
    # description
    description = models.TextField(max_length=250)
    # price
    starting_bid = models.IntegerField(validators=[MinValueValidator(0)])
    # current highest bid
    highest_bid = models.IntegerField(default=0)
    # photo
    image = models.URLField(blank=True)
    # when created
    created_on = models.DateTimeField(auto_now_add=True)
    # category
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    # listed by who
    listed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="author")
    # is the auction open or closed
    is_open = models.BooleanField(default=True)

class Bid(models.Model):
    # bid amount
    bid = models.IntegerField()
    # who bid
    bid_author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidder")
    # on what auction is the bid
    bid_on = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="bidOnAuction")


class Comment(models.Model):
    # actual comment
    comment = models.CharField(max_length=250)
    # who commented
    comment_author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commenter")
    # on what auction is the comment
    comment_on = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="commentOnAuction")