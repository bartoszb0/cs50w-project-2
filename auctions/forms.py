from django.forms import ModelForm
from django import forms
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

        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Enter name"}),
            "description": forms.Textarea(attrs={"placeholder": "Enter description"}),
            "highest_bid": forms.NumberInput(attrs={"placeholder": "Enter starting price"}),
            "image": forms.URLInput(attrs={"placeholder": "Enter URL here"}),
        }

class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = [
            "bid",
        ]

        widgets = {
            "bid": forms.NumberInput(attrs={"placeholder": "Enter bid"})
        }

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = [
            "comment",
        ]

        widgets = {
            "comment": forms.Textarea(attrs={"placeholder": "Enter comment"})
        }