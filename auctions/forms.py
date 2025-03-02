from django.forms import ModelForm
from .models import Auction, Bid, Comment

class AuctionForm(ModelForm):
    class Meta:
        model = Auction
        fields = [
            "name",
            "description",
            "highest_bid",
            "image",
            "category",
        ]

class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = [
            "bid",
        ]

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = [
            "comment",
        ]