from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Auction, Bid, Comment, CATEGORY_CHOICES
from .forms import AuctionForm, BidForm, CommentForm


def index(request):
    all_auctions = Auction.objects.all()
    return render(request, "auctions/index.html", {
        "auctions": all_auctions
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required
def create_listing(request):
    if request.method == "POST":
        creator = User.objects.get(username=request.user.username)
        form = AuctionForm(request.POST)
        if form.is_valid():
            new_auction = Auction(
                name=form.cleaned_data["name"],
                description=form.cleaned_data["description"],
                highest_bid=form.cleaned_data["highest_bid"],
                image=form.cleaned_data["image"],
                category=form.cleaned_data["category"],
                listed_by=creator
            )
            new_auction.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/create.html", {
                "form": form
            })
    return render(request, "auctions/create.html", {
        "form": AuctionForm()
    })


def listing_view(request, id):
    auction = Auction.objects.get(id=id)

    if request.method == "POST":
        form = BidForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["bid"] <= auction.highest_bid:
                return render(request, "auctions/listing.html", {
                    "message": "Bid must be bigger than current price",
                    "auction": auction,
                    "form": BidForm(),
                    "highest_bid": Bid.objects.filter(bid_on=auction).order_by("-bid").first()
                })
            else:
                auction.highest_bid = form.cleaned_data["bid"]
                auction.save()

                new_bid = Bid(
                    bid=auction.highest_bid,
                    bid_author=User.objects.get(username=request.user.username),
                    bid_on=auction
                )
                new_bid.save()
                # TODO flash "Succesfully placed a bet"
                return HttpResponseRedirect(reverse("listing", args=[id]))
        else:
            return render(request, "auctions/listing.html", {
                "auction": auction,
                "form": BidForm(),
                "highest_bid": Bid.objects.filter(bid_on=auction).order_by("-bid").first()
            })
    else:
        return render(request, "auctions/listing.html", {
            "auction": auction,
            "form": BidForm(),
            "highest_bid": Bid.objects.filter(bid_on=auction).order_by("-bid").first(),
            "comments": Comment.objects.filter(comment_on=auction).order_by("-id"), # TODO zrobic to w kazdym wariancie
            "comment_form": CommentForm()
        })

def user_listings(request, username):
    user = User.objects.get(username=username)
    auctions = Auction.objects.filter(listed_by=user)
    return render(request, "auctions/user.html", {
        "auctions": auctions,
        "username": username
    })

def categories_page(request):
    categories = []
    for category in CATEGORY_CHOICES:
        categories.append(category[0])
    return render(request, "auctions/categories.html", {
        "categories": categories
    })

def category_page(request, category):
    auctions = Auction.objects.filter(category=category)
    return render(request, "auctions/index.html", {
        "auctions": auctions
    })

def action_comment(request, id): # TODO handle user putting /listings/13/comment
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            auction = Auction.objects.get(id=id)
            user = User.objects.get(username=request.user.username)
            comment = form.cleaned_data["comment"]
            Comment(comment=comment, author=user, comment_on=auction).save()
            return HttpResponseRedirect(reverse("listing", args=[id]))