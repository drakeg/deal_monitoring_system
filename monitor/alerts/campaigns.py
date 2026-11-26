from django import forms
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .models import Campaign

class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ["name", "retailer", "category", "event", "minimum_discount", "starts_on", "ends_on", "enabled"]
        widgets = {field: forms.DateInput(attrs={"type": "date"}) for field in ("starts_on", "ends_on")}

    def clean(self):
        data = super().clean()
        if data.get("starts_on") and data.get("ends_on") and data["ends_on"] < data["starts_on"]:
            self.add_error("ends_on", "End date must not precede start date.")
        return data

@login_required
def campaigns(request):
    form = CampaignForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        campaign = form.save(commit=False)
        campaign.owner = request.user
        campaign.save()
        return redirect("campaigns")
    return render(request, "campaigns.html", {"form": form, "campaigns": Campaign.objects.filter(owner=request.user).order_by("-id")})

@login_required
@require_POST
def toggle_campaign(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk, owner=request.user)
    campaign.enabled = not campaign.enabled
    campaign.save(update_fields=["enabled"])
    return redirect("campaigns")
