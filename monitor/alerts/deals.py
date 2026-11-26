from decimal import Decimal
from django import forms
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.db import transaction
from django.utils import timezone
from .models import Campaign, Deal

class DealForm(forms.ModelForm):
    class Meta:
        model = Deal
        fields = ["title", "url", "price", "reference_price"]

    def clean(self):
        data = super().clean()
        if data.get("price") and data.get("reference_price") and data["reference_price"] <= data["price"]:
            self.add_error("reference_price", "Reference price must exceed sale price.")
        if data.get("url") and not data["url"].startswith("https://"):
            self.add_error("url", "Use an HTTPS product link.")
        return data

@login_required
def deals(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk, owner=request.user)
    form = DealForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        with transaction.atomic():
            Deal.objects.update_or_create(campaign=campaign, url=data["url"], defaults={**data, "observed_at": timezone.now()})
        return redirect("deals", pk=pk)
    results = list(campaign.deal_set.all())
    results = sorted((deal for deal in results if deal.discount >= campaign.minimum_discount), key=lambda deal: deal.discount, reverse=True)
    return render(request, "deals.html", {"campaign": campaign, "form": form, "deals": results})
