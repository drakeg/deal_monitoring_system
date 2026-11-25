from django.contrib.auth.decorators import login_required
from django.forms import ModelForm
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .models import Alert

class AlertForm(ModelForm):
    class Meta:
        model = Alert
        fields = ["name", "product_url", "target_price", "enabled"]

@login_required
def dashboard(request):
    form = AlertForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        alert = form.save(commit=False)
        alert.owner = request.user
        alert.save()
        return redirect("/")
    return render(request, "dashboard.html", {"form":form, "alerts":Alert.objects.filter(owner=request.user).order_by("-created_at")})

@login_required
@require_POST
def delete_alert(request, pk):
    get_object_or_404(Alert, pk=pk, owner=request.user).delete()
    return redirect("/")
