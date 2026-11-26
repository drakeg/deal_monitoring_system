"""Bounded offline Scrapling integration; no network requests."""
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from scrapling import Selector
from .models import Campaign
from .deals import DealForm

@login_required
@require_POST
def scan(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk, owner=request.user)
    page = Selector(content="""<article class="product"><h2>Demo camping tent</h2><span class="price">69.00</span><span class="regular">119.00</span><a href="https://example.com/demo-tent">Product</a></article>
<article class="product"><h2>Demo exercise mat</h2><span class="price">19.00</span><span class="regular">39.00</span><a href="https://example.com/demo-mat">Product</a></article>""")
    results = []
    for item in page.css(".product"):
        form = DealForm({"title": item.css("h2::text").get(), "url": item.css("a::attr(href)").get(), "price": item.css(".price::text").get(), "reference_price": item.css(".regular::text").get()})
        if form.is_valid():
            deal = form.save(commit=False)
            if deal.discount >= campaign.minimum_discount:
                results.append(deal)
    return render(request, "scan.html", {"campaign": campaign, "results": results})
