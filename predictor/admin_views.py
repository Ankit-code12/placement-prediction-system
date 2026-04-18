from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db.models import Count, Avg
from .models import Prediction

@staff_member_required
def admin_dashboard(request):
    """Custom admin dashboard with statistics"""
    total_predictions = Prediction.objects.count()
    placed_count = Prediction.objects.filter(status='Placed').count()
    not_placed_count = total_predictions - placed_count
    
    # Course-wise statistics
    course_stats = Prediction.objects.values('course').annotate(
        count=Count('id'),
        placed=Count('id', filter=models.Q(status='Placed')),
        avg_prob=Avg('probability')
    )
    
    # Monthly trends
    monthly_trends = Prediction.objects.extra(
        select={'month': "strftime('%%Y-%%m', timestamp)"}
    ).values('month').annotate(
        count=Count('id'),
        avg_prob=Avg('probability')
    ).order_by('-month')[:6]
    
    context = {
        'total_predictions': total_predictions,
        'placed_count': placed_count,
        'not_placed_count': not_placed_count,
        'placement_rate': (placed_count/total_predictions*100) if total_predictions > 0 else 0,
        'course_stats': course_stats,
        'monthly_trends': monthly_trends,
    }
    
    return render(request, 'admin/custom_dashboard.html', context)