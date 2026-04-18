from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Prediction

class PredictionAdmin(admin.ModelAdmin):
    # Display these fields in the list view
    list_display = [
        'id', 
        'user_link', 
        'status_badge', 
        'probability_bar', 
        'skill_score', 
        'cgpa', 
        'course_short', 
        'timestamp_short'
    ]
    
    # Filters on the right side
    list_filter = [
        'status', 
        'course', 
        'work_experience', 
        'gender',
        'degree_type'
    ]
    
    # Search fields
    search_fields = [
        'user__username', 
        'user__email', 
        'course', 
        'course_specialization',
        'status'
    ]
    
    # Read-only fields
    readonly_fields = ['timestamp', 'prediction_id']
    
    # Date hierarchy for navigation
    date_hierarchy = 'timestamp'
    
    # Pagination
    list_per_page = 25
    
    # Default sorting
    ordering = ['-timestamp']
    
    # REMOVED list_editable - it was causing the error
    # list_editable = ['status']  # ← YEH LINE HATADO
    
    # Custom method for user link
    def user_link(self, obj):
        return format_html(
            '<a href="/admin/auth/user/{}/change/" style="color: #1e3c72; font-weight: bold;">{} ({})</a>',
            obj.user.id, 
            obj.user.username,
            obj.user.email if obj.user.email else 'no email'
        )
    user_link.short_description = 'Student'
    user_link.admin_order_field = 'user__username'
    
    # Custom method for status badge
    def status_badge(self, obj):
        if obj.status == 'Placed':
            color = '#28a745'
            bg = '#d4edda'
            icon = '✓'
            text = 'Placed'
        else:
            color = '#dc3545'
            bg = '#f8d7da'
            icon = '✗'
            text = 'Not Placed'
        
        return format_html(
            '<span style="background: {}; color: {}; padding: 5px 12px; border-radius: 20px; font-weight: bold; font-size: 12px;">{} {}</span>',
            bg, color, icon, text
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    # Custom method for probability bar
    def probability_bar(self, obj):
        percentage = obj.probability
        if percentage >= 70:
            color = '#28a745'
        elif percentage >= 40:
            color = '#ffc107'
        else:
            color = '#dc3545'
        
        return format_html('''
            <div style="background: #e0e0e0; border-radius: 10px; width: 120px; height: 20px; position: relative; overflow: hidden;">
                <div style="background: {}; width: {}%; height: 100%; border-radius: 10px; text-align: center; color: white; font-size: 11px; line-height: 20px;">
                    {}%
                </div>
            </div>
        ''', color, percentage, percentage)
    probability_bar.short_description = 'Probability'
    probability_bar.admin_order_field = 'probability'
    
    # Custom method for short course name
    def course_short(self, obj):
        if len(obj.course) > 20:
            return obj.course[:17] + '...'
        return obj.course
    course_short.short_description = 'Course'
    
    # Custom method for short timestamp
    def timestamp_short(self, obj):
        return obj.timestamp.strftime("%Y-%m-%d %H:%M")
    timestamp_short.short_description = 'Date'
    timestamp_short.admin_order_field = 'timestamp'
    
    # Custom method for prediction ID
    def prediction_id(self, obj):
        return f'PRED-{obj.id:05d}'
    prediction_id.short_description = 'Prediction ID'
    
    # Organize fields in the edit form
    fieldsets = (
        ('Basic Information', {
            'fields': ('prediction_id', 'user', 'timestamp')
        }),
        ('Student Personal Details', {
            'fields': ('gender',)
        }),
        ('Academic Performance', {
            'fields': (
                ('hs_percentage', 'hs_board'),
                ('twelfth_percentage', 'twelfth_board', 'twelfth_stream'),
                ('degree_percentage', 'degree_type', 'cgpa')
            ),
            'classes': ('wide',)
        }),
        ('Professional Skills & Experience', {
            'fields': (
                ('skill_score', 'etest_percentage'),
                ('internship', 'work_experience'),
                'final_year_percentage'
            ),
        }),
        ('Course Information', {
            'fields': ('course', 'course_specialization'),
        }),
        ('Prediction Result', {
            'fields': ('status', 'probability'),
            'classes': ('collapse',)
        }),
    )
    
    # Bulk actions
    actions = [
        'export_as_csv', 
        'mark_as_placed', 
        'mark_as_not_placed',
    ]
    
    # Export to CSV
    def export_as_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="placement_predictions.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Student', 'Email', 'Status', 'Probability (%)', 
            'Skill Score', 'CGPA', 'Course', 'Specialization', 
            'Internships', 'Work Experience', 'Gender', 'Timestamp'
        ])
        
        for obj in queryset:
            writer.writerow([
                obj.id, obj.user.username, obj.user.email, obj.status, obj.probability,
                obj.skill_score, obj.cgpa, obj.course, obj.course_specialization,
                obj.internship, obj.work_experience, obj.gender, obj.timestamp
            ])
        
        return response
    export_as_csv.short_description = "📊 Export selected to CSV"
    
    # Bulk mark as placed
    def mark_as_placed(self, request, queryset):
        count = queryset.update(status='Placed')
        self.message_user(request, f'{count} prediction(s) marked as Placed.')
    mark_as_placed.short_description = "✅ Mark selected as Placed"
    
    # Bulk mark as not placed
    def mark_as_not_placed(self, request, queryset):
        count = queryset.update(status='Not Placed')
        self.message_user(request, f'{count} prediction(s) marked as Not Placed.')
    mark_as_not_placed.short_description = "❌ Mark selected as Not Placed"
    
    # Custom save method
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.user = request.user
        super().save_model(request, obj, form, change)


# Custom User Admin
class CustomUserAdmin(UserAdmin):
    list_display = [
        'username', 
        'email', 
        'first_name', 
        'last_name', 
        'is_staff', 
        'is_active',
        'date_joined_short',
        'predictions_count',
    ]
    
    list_filter = ['is_staff', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    # Custom methods
    def date_joined_short(self, obj):
        return obj.date_joined.strftime("%Y-%m-%d")
    date_joined_short.short_description = 'Joined'
    
    def predictions_count(self, obj):
        count = Prediction.objects.filter(user=obj).count()
        if count > 0:
            return format_html(
                '<span style="background: #1e3c72; color: white; padding: 3px 10px; border-radius: 20px; font-size: 12px;">{}</span>',
                count
            )
        return '0'
    predictions_count.short_description = 'Predictions'


# Register Prediction model with custom admin
admin.site.register(Prediction, PredictionAdmin)

# Unregister default User admin and register custom
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Customize admin site header and title
admin.site.site_header = "Placement Prediction System Admin"
admin.site.site_title = "Placement Predictor Admin Portal"
admin.site.index_title = "Welcome to Placement Prediction Dashboard"