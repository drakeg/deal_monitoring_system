"""Import an operator-authorized category HTML export without network access."""
from django import forms
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from urllib.parse import urljoin, urlsplit
from scrapling import Selector
from .models import Campaign, Deal
from .deals import DealForm

class CategoryImportForm(forms.Form):
    listing_url = forms.URLField(max_length=2000, assume_scheme="https")
    html = forms.CharField(widget=forms.Textarea, max_length=500000)
    item_selector = forms.CharField(max_length=200)
    title_selector = forms.CharField(max_length=200)
    price_selector = forms.CharField(max_length=200)
    reference_selector = forms.CharField(max_length=200)
    url_selector = forms.CharField(max_length=200)
    authorized = forms.BooleanField(label="I have permission to use this retailer category export")

    def clean_listing_url(self):
        url = self.cleaned_data["listing_url"]
        p = urlsplit(url)
        if p.scheme != "https" or not p.hostname or p.username or p.password:
            raise forms.ValidationError("Use an HTTPS listing URL without credentials.")
        return url

def candidates(data):
    page = Selector(content=data["html"])
    origin = urlsplit(data["listing_url"])
    seen = set()
    for item in page.css(data["item_selector"])[:500]:
        def value(key):
            return str(item.css(data[key + "_selector"]).get() or "").strip()
        raw = value("url")
        if not raw:
            continue
        url = urljoin(data["listing_url"], raw)
        target = urlsplit(url)
        if target.scheme != "https" or target.netloc != origin.netloc:
            continue
        url = target._replace(fragment="").geturl()
        if url in seen:
            continue
        form = DealForm({"title": value("title"), "url": url, "price": value("price").removeprefix("$").replace(",", ""), "reference_price": value("reference").removeprefix("$").replace(",", "")})
        if form.is_valid():
            seen.add(url)
            yield form.cleaned_data

@login_required
def category_import(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk, owner=request.user)
    form = CategoryImportForm(request.POST if request.method == "POST" else None)
    count = None
    if request.method == "POST" and form.is_valid():
        try:
            rows = list(candidates(form.cleaned_data))
        except Exception:
            form.add_error(None, "Unable to parse category HTML or selectors.")
        else:
            with transaction.atomic():
                for row in rows:
                    Deal.objects.update_or_create(campaign=campaign, url=row["url"], defaults={**row, "observed_at": timezone.now()})
            count = len(rows)
    return render(request, "category_import.html", {"campaign": campaign, "form": form, "count": count})
