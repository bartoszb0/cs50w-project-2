from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class User(AbstractUser):
    pass

CATEGORY_CHOICES = [
    ('Electronics', 'Electronics'),
    ('Fashion', 'Fashion'),
    ('Home', 'Home'),
    ('Sports', 'Sports'),
    ('Toys', 'Toys'),
    ('Music', 'Music'),
]

def validateURL(url): # TODO THIS MIGHT NOT WORK
    if url.endswith(".jpg") or url.endswith(".png"):
        return True
    raise ValidationError("URL must be an image")


class Auction(models.Model):
    # name
    name = models.CharField(max_length=50)
    # description
    description = models.TextField(max_length=250)
    # price
    highest_bid = models.IntegerField(validators=[MinValueValidator(1)])
    # photo
    image = models.URLField(blank=True, validators=[validateURL])
    # when created
    created_on = models.DateTimeField(auto_now_add=True)
    # category
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    # listed by who
    listed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="author")
    # is the auction open or closed
    is_open = models.BooleanField(default=True)
    # each auction can have multiple users, each user can watch multiple auctions
    watchlist = models.ManyToManyField(User, blank=True, related_name="watchers")
    # remember starting price
    starting_price = models.IntegerField(default=1)

    def __str__(self):
        return f"'{self.name}', created by {self.listed_by}"
    
    def save(self):
        super().save()
        Bid(bid=self.highest_bid, bid_on=self).save()

class Bid(models.Model):
    # bid amount
    bid = models.IntegerField()
    # who bid
    bid_author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidder")
    # on what auction is the bid
    bid_on = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="bidOnAuction")

    def __str__(self):
        return f"${self.bid} placed on '{self.bid_on.name}'"
    
    # When calling .save(), it checks whether passed bid is higher than the current highest bid for certain auction, if it is,
    # new bid overwrites the highest bid on certain auction
    def save(self):
        if self.bid > self.bid_on.highest_bid:
            self.bid_on.highest_bid = self.bid
            self.bid_on.save()
            super().save()

    def delete(self):
        super().delete()
        if Bid.objects.filter(bid_on=self.bid_on).exists():
            self.bid_on.highest_bid = Bid.objects.filter(bid_on=self.bid_on).order_by("-bid").first().bid
        else:
            self.bid_on.highest_bid = self.bid_on.starting_price
        self.bid_on.save()

    # TODO ogarnac co sie dzieje jak kasuje bida w Django Admin Inteface

class Comment(models.Model):
    # actual comment
    comment = models.TextField(max_length=250)
    # who commented
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commenter")
    # on what auction is the comment
    comment_on = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="commentOnAuction")

    def __str__(self):
        return f"Comment ID{self.id}, placed on '{self.comment_on.name}' by {self.author.username}"