import warnings
warnings.filterwarnings('ignore')
import os
import pickle
import numpy as np
import pandas as pd
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from django.db.models import Count, Avg
from django.core.mail import send_mail
from django.conf import settings
import json
from datetime import datetime
import io

# Try to import models
try:
    from .models import Prediction
    MODELS_AVAILABLE = True
except ImportError:
    MODELS_AVAILABLE = False
    print("Models not yet migrated. Run: python manage.py makemigrations && python manage.py migrate")

# ReportLab for PDF
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.colors import HexColor
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# OpenPyXL for Excel
try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

model_path = os.path.join(BASE_DIR, 'predictor', 'placement_model.pkl')
scaler_path = os.path.join(BASE_DIR, 'predictor', 'scaler.pkl')

model = pickle.load(open(model_path, 'rb'))
scaler = pickle.load(open(scaler_path, 'rb'))

# ==================== COMPANY CRITERIA ====================
COMPANY_CRITERIA = {
    'Google': {'min_cgpa': 8.5, 'min_skill': 85, 'min_aptitude': 85, 'icon': 'fab fa-google', 'color': '#4285f4'},
    'Microsoft': {'min_cgpa': 8.0, 'min_skill': 82, 'min_aptitude': 80, 'icon': 'fab fa-microsoft', 'color': '#f25022'},
    'Amazon': {'min_cgpa': 7.5, 'min_skill': 78, 'min_aptitude': 75, 'icon': 'fab fa-amazon', 'color': '#ff9900'},
    'TCS': {'min_cgpa': 6.5, 'min_skill': 70, 'min_aptitude': 65, 'icon': 'fas fa-building', 'color': '#0077b6'},
    'Infosys': {'min_cgpa': 6.0, 'min_skill': 65, 'min_aptitude': 60, 'icon': 'fas fa-chart-line', 'color': '#cc0000'},
    'Wipro': {'min_cgpa': 6.0, 'min_skill': 60, 'min_aptitude': 60, 'icon': 'fas fa-laptop-code', 'color': '#6c3483'},
}

# ==================== JOBS DATABASE ====================
JOBS_DATABASE = [
    {'title': 'Software Engineer', 'company': 'Google', 'min_cgpa': 8.0, 'min_skill': 85, 'salary': '25-35 LPA', 'location': 'Bangalore', 'skills': ['Python', 'DSA', 'System Design'], 'logo': 'fab fa-google'},
    {'title': 'Data Scientist', 'company': 'Microsoft', 'min_cgpa': 7.5, 'min_skill': 80, 'salary': '20-30 LPA', 'location': 'Hyderabad', 'skills': ['Python', 'ML', 'Statistics'], 'logo': 'fab fa-microsoft'},
    {'title': 'Full Stack Developer', 'company': 'Amazon', 'min_cgpa': 7.0, 'min_skill': 78, 'salary': '18-25 LPA', 'location': 'Chennai', 'skills': ['React', 'Node.js', 'AWS'], 'logo': 'fab fa-amazon'},
    {'title': 'Business Analyst', 'company': 'Deloitte', 'min_cgpa': 6.5, 'min_skill': 70, 'salary': '8-12 LPA', 'location': 'Mumbai', 'skills': ['Excel', 'SQL', 'Tableau'], 'logo': 'fas fa-chart-line'},
    {'title': 'Software Developer', 'company': 'Infosys', 'min_cgpa': 6.0, 'min_skill': 65, 'salary': '6-10 LPA', 'location': 'Pune', 'skills': ['Java', 'Spring Boot', 'SQL'], 'logo': 'fas fa-code'},
    {'title': 'Web Developer', 'company': 'TCS', 'min_cgpa': 6.0, 'min_skill': 60, 'salary': '5-8 LPA', 'location': 'Multiple', 'skills': ['HTML/CSS', 'JavaScript', 'React'], 'logo': 'fas fa-globe'},
]

# ==================== AUTHENTICATION VIEWS ====================

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password!')
    
    return render(request, 'login.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validation
        if not username or not email or not password:
            messages.error(request, 'All fields are required!')
            return render(request, 'register.html')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match!')
            return render(request, 'register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return render(request, 'register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered!')
            return render(request, 'register.html')
        
        # Create user
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            messages.success(request, 'Account created successfully! Please login.')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return render(request, 'register.html')
    
    return render(request, 'register.html')

def logout_view(request):
    logout(request)
    return redirect('login')

# ==================== MAIN PAGE VIEWS ====================

@login_required(login_url='login')
def home(request):
    return render(request, 'home.html')

@login_required(login_url='login')
def about(request):
    return render(request, 'about.html')

@login_required(login_url='login')
def dashboard(request):
    if MODELS_AVAILABLE:
        all_predictions = Prediction.objects.all()
        total_predictions = all_predictions.count()
        placed_count = all_predictions.filter(status='Placed').count()
        
        if total_predictions > 0:
            placement_rate = (placed_count / total_predictions) * 100
            avg_skill_score = all_predictions.aggregate(Avg('skill_score'))['skill_score__avg'] or 0
            avg_probability = all_predictions.aggregate(Avg('probability'))['probability__avg'] or 0
        else:
            placement_rate = 0
            avg_skill_score = 0
            avg_probability = 0
        
        recent_predictions = all_predictions.order_by('-timestamp')[:10]
        recent_list = []
        for pred in recent_predictions:
            recent_list.append({
                'timestamp': pred.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                'status': pred.status,
                'probability': pred.probability,
                'skill_score': pred.skill_score,
                'cgpa': pred.cgpa
            })
    else:
        total_predictions = 0
        placed_count = 0
        placement_rate = 0
        avg_skill_score = 0
        avg_probability = 0
        recent_list = []
    
    stats = {
        'total_predictions': total_predictions,
        'placed_count': placed_count,
        'placement_rate': round(placement_rate, 1),
        'avg_skill_score': round(avg_skill_score, 1),
        'avg_probability': round(avg_probability, 1),
        'recent_predictions': recent_list,
        'company_criteria': COMPANY_CRITERIA,
    }
    
    return render(request, 'dashboard.html', stats)

@login_required(login_url='login')
def profile(request):
    if MODELS_AVAILABLE:
        user_predictions = Prediction.objects.filter(user=request.user).order_by('-timestamp')
        total = user_predictions.count()
        placed = user_predictions.filter(status='Placed').count()
        placement_rate = (placed/total*100) if total > 0 else 0
        avg_skill = user_predictions.aggregate(Avg('skill_score'))['skill_score__avg'] or 0
        avg_prob = user_predictions.aggregate(Avg('probability'))['probability__avg'] or 0
        
        latest_pred = user_predictions.first()
        if latest_pred:
            job_recommendations = get_job_recommendations(latest_pred.cgpa, latest_pred.skill_score, latest_pred.course)
        else:
            job_recommendations = []
        
        context = {
            'predictions': user_predictions[:10],
            'total_predictions': total,
            'placement_rate': round(placement_rate, 1),
            'avg_skill_score': round(avg_skill, 1),
            'avg_probability': round(avg_prob, 1),
            'job_recommendations': job_recommendations,
            'has_predictions': total > 0
        }
    else:
        context = {
            'predictions': [],
            'total_predictions': 0,
            'placement_rate': 0,
            'avg_skill_score': 0,
            'avg_probability': 0,
            'job_recommendations': [],
            'has_predictions': False
        }
    
    return render(request, 'profile.html', context)

@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match!')
            return render(request, 'change_password.html')
        
        if request.user.check_password(old_password):
            request.user.set_password(new_password)
            request.user.save()
            messages.success(request, 'Password changed! Please login again.')
            return redirect('login')
        else:
            messages.error(request, 'Old password is incorrect!')
    
    return render(request, 'change_password.html')

# ==================== JOB RECOMMENDATION FUNCTION ====================

def get_job_recommendations(cgpa, skill_score, course):
    recommended = []
    for job in JOBS_DATABASE:
        if cgpa >= job['min_cgpa'] and skill_score >= job['min_skill']:
            job_copy = job.copy()
            match = 50
            if cgpa >= job['min_cgpa'] + 1:
                match += 20
            elif cgpa >= job['min_cgpa']:
                match += 10
            if skill_score >= job['min_skill'] + 15:
                match += 20
            elif skill_score >= job['min_skill']:
                match += 10
            job_copy['match_percentage'] = min(95, match)
            recommended.append(job_copy)
    
    recommended.sort(key=lambda x: x['match_percentage'], reverse=True)
    return recommended[:5]

# ==================== PREDICTION HELPER FUNCTIONS ====================

def generate_recommendations(cgpa, aptitude, skill, internship, workex, probability):
    recommendations = []
    
    if cgpa < 6.0:
        recommendations.append("📚 Improve your CGPA - focus on core subjects")
    elif cgpa < 7.0:
        recommendations.append("📖 Your CGPA is good, aim for above 7.5")
    elif cgpa >= 8.0:
        recommendations.append("🎓 Excellent CGPA! Highlight this in your resume")
    
    if aptitude < 60:
        recommendations.append("🧠 Practice aptitude tests daily")
    elif aptitude < 75:
        recommendations.append("📊 Practice more complex aptitude problems")
    else:
        recommendations.append("🎯 Great aptitude score! Focus on speed")
    
    if skill < 70:
        recommendations.append("💻 Take online courses to enhance skills")
    elif skill < 85:
        recommendations.append("🚀 Build projects to showcase your skills")
    else:
        recommendations.append("⭐ Outstanding skills! Contribute to open source")
    
    if internship == 0:
        recommendations.append("🏢 Apply for internships immediately")
    elif internship < 2:
        recommendations.append("💼 Try to get one more internship")
    
    if workex == 'No':
        recommendations.append("📝 Focus on projects and certifications")
    
    if probability < 40:
        recommendations.append("⚠️ Consider skill development courses")
    elif probability < 70:
        recommendations.append("🎯 Apply to multiple companies")
    else:
        recommendations.append("✨ Excellent chances! Focus on interviews")
    
    return list(dict.fromkeys(recommendations))[:5]

def get_company_predictions(cgpa, skill_score, aptitude):
    company_predictions = []
    for company, criteria in COMPANY_CRITERIA.items():
        chance = 0
        if cgpa >= criteria['min_cgpa']:
            chance += 40
        if skill_score >= criteria['min_skill']:
            chance += 35
        if aptitude >= criteria['min_aptitude']:
            chance += 25
        
        if chance >= 70:
            status = "High Chance"
            color = "#28a745"
        elif chance >= 40:
            status = "Moderate Chance"
            color = "#ffc107"
        else:
            status = "Low Chance"
            color = "#dc3545"
        
        company_predictions.append({
            'name': company,
            'chance': chance,
            'status': status,
            'color': color,
            'icon': criteria['icon'],
        })
    
    return sorted(company_predictions, key=lambda x: x['chance'], reverse=True)

# ==================== PREDICTION API ====================

@login_required(login_url='login')
@csrf_exempt
@require_http_methods(["POST"])
def predict_api(request):
    try:
        data = json.loads(request.body)
        
        gender = data.get('gender')
        hs_p = float(data.get('hs_p'))
        hs_b = data.get('hs_b')
        hs_12_p = float(data.get('12_p'))
        hs_12_b = data.get('12_b')
        hs_12_s = data.get('12_s')
        degree_p = float(data.get('degree_p'))
        degree_t = data.get('degree_t')
        workex = data.get('workex')
        etest_p = float(data.get('etest_p'))
        final_year_p = float(data.get('final_year_p'))
        course = data.get('course')
        course_specialization = data.get('course_specialization')
        skill_score = float(data.get('skill_score'))
        internship = int(data.get('internship'))
        
        # Encoding mappings
        gender_map = {'M': 0, 'F': 1}
        hs_b_map = {'Central': 0, 'Others': 1}
        hs_12_b_map = {'Central': 0, 'Others': 1}
        hs_12_s_map = {'Commerce': 0, 'Science': 1, 'Arts': 2}
        degree_t_map = {'Sci&Tech': 0, 'Comm&Mgmt': 1, 'Others': 2}
        workex_map = {'No': 0, 'Yes': 1}
        course_map = {'B.Tech': 0, 'BCA': 1, 'MCA': 2, 'MBA': 3, 'Pharmacy': 4}
        course_spec_map = {
            'ECE': 0, 'Web Dev': 1, 'Data Science': 2, 'App Dev': 3,
            'Finance': 4, 'Pharmacology': 5, 'Software': 6, 
            'Clinical Research': 7, 'HR': 8, 'CSE': 9, 'IT': 10
        }
        
        input_data = pd.DataFrame([{
            'gender': gender_map.get(gender, 0),
            'hs p': hs_p,
            'hs b': hs_b_map.get(hs_b, 0),
            '12_p': hs_12_p,
            '12_b': hs_12_b_map.get(hs_12_b, 0),
            '12_s': hs_12_s_map.get(hs_12_s, 0),
            'degree_p': degree_p,
            'degree_t': degree_t_map.get(degree_t, 0),
            'workex': workex_map.get(workex, 0),
            'etest_p': etest_p,
            'final_year_p': final_year_p,
            'course': course_map.get(course, 0),
            'course_specialization': course_spec_map.get(course_specialization, 0),
            'skill_score': skill_score,
            'internship': internship
        }])
        
        features_scaled = scaler.transform(input_data)
        prediction = model.predict(features_scaled)
        probability = model.predict_proba(features_scaled)[0][1] * 100
        
        recommendations = generate_recommendations(degree_p, etest_p, skill_score, internship, workex, probability)
        company_predictions = get_company_predictions(degree_p, skill_score, etest_p)
        
        result = {
            'success': True,
            'placement_status': 'Placed' if prediction[0] == 1 else 'Not Placed',
            'probability': round(probability, 2),
            'recommendations': recommendations,
            'company_predictions': company_predictions,
            'student_data': {
                'cgpa': degree_p,
                'aptitude_score': etest_p,
                'skill_score': skill_score,
                'internship': internship,
                'work_experience': workex,
            }
        }
        
        # Save to database
        if MODELS_AVAILABLE:
            try:
                Prediction.objects.create(
                    user=request.user,
                    status=result['placement_status'],
                    probability=result['probability'],
                    skill_score=int(skill_score),
                    cgpa=degree_p,
                    gender=gender,
                    hs_percentage=hs_p,
                    hs_board=hs_b,
                    twelfth_percentage=hs_12_p,
                    twelfth_board=hs_12_b,
                    twelfth_stream=hs_12_s,
                    degree_percentage=degree_p,
                    degree_type=degree_t,
                    work_experience=workex,
                    etest_percentage=etest_p,
                    final_year_percentage=final_year_p,
                    course=course,
                    course_specialization=course_specialization,
                    internship=internship
                )
            except Exception as e:
                print(f"DB Error: {e}")
        
        # Send email (optional)
        try:
            if request.user.email:
                send_mail(
                    f'Placement Prediction Result - {result["placement_status"]}',
                    f'Hello {request.user.username},\n\nYour placement prediction:\nStatus: {result["placement_status"]}\nProbability: {result["probability"]}%\n\nBest regards,\nPlacement Predictor',
                    settings.EMAIL_HOST_USER if hasattr(settings, 'EMAIL_HOST_USER') else 'noreply@placement.com',
                    [request.user.email],
                    fail_silently=True,
                )
        except:
            pass
        
        return JsonResponse(result)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)})

# ==================== COMPARE VIEWS ====================

@login_required(login_url='login')
def compare(request):
    return render(request, 'compare.html')

@login_required(login_url='login')
@csrf_exempt
@require_http_methods(["POST"])
def compare_api(request):
    try:
        data = json.loads(request.body)
        student1 = data.get('student1', {})
        student2 = data.get('student2', {})
        
        def calc_score(s):
            score = float(s.get('degree_p', 0)) * 0.4
            score += float(s.get('skill_score', 0)) * 0.4
            score += int(s.get('internship', 0)) * 10
            if s.get('workex') == 'Yes':
                score += 10
            return round(score, 2)
        
        score1 = calc_score(student1)
        score2 = calc_score(student2)
        
        return JsonResponse({
            'success': True,
            'student1_score': score1,
            'student2_score': score2,
            'winner': 'Student 1' if score1 > score2 else 'Student 2',
            'difference': abs(score1 - score2)
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# ==================== EXPORT FEATURES ====================

@login_required(login_url='login')
def download_report(request):
    if not REPORTLAB_AVAILABLE:
        return HttpResponse("ReportLab not installed", status=400)
    
    try:
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        p.setFillColor(HexColor('#1e3c72'))
        p.rect(0, height - 80, width, 80, fill=True)
        p.setFillColor(HexColor('#ffffff'))
        p.setFont("Helvetica-Bold", 24)
        p.drawString(50, height - 50, "Placement Prediction Report")
        
        p.setFillColor(HexColor('#000000'))
        p.setFont("Helvetica", 12)
        p.drawString(50, height - 120, f"Student: {request.user.username}")
        p.drawString(50, height - 140, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if MODELS_AVAILABLE:
            last_pred = Prediction.objects.filter(user=request.user).order_by('-timestamp').first()
            if last_pred:
                y = height - 200
                p.setFont("Helvetica-Bold", 14)
                p.drawString(50, y, "Latest Prediction:")
                y -= 30
                p.setFont("Helvetica", 12)
                p.drawString(50, y, f"Status: {last_pred.status}")
                y -= 25
                p.drawString(50, y, f"Probability: {last_pred.probability}%")
                y -= 25
                p.drawString(50, y, f"Skill Score: {last_pred.skill_score}")
            else:
                p.drawString(50, height - 200, "No predictions found")
        
        p.save()
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="report.pdf"'
        return response
    except Exception as e:
        return HttpResponse(f"Error: {e}", status=400)

@login_required(login_url='login')
def export_excel(request):
    if not OPENPYXL_AVAILABLE:
        return HttpResponse("OpenPyXL not installed", status=400)
    
    try:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "My Predictions"
        
        headers = ['Date', 'Status', 'Probability', 'Skill Score', 'CGPA', 'Course']
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="1e3c72", end_color="1e3c72", fill_type="solid")
        
        if MODELS_AVAILABLE:
            predictions = Prediction.objects.filter(user=request.user).order_by('-timestamp')
            for row, pred in enumerate(predictions, 2):
                ws.cell(row=row, column=1, value=pred.timestamp.strftime("%Y-%m-%d %H:%M"))
                ws.cell(row=row, column=2, value=pred.status)
                ws.cell(row=row, column=3, value=pred.probability)
                ws.cell(row=row, column=4, value=pred.skill_score)
                ws.cell(row=row, column=5, value=pred.cgpa)
                ws.cell(row=row, column=6, value=pred.course)
        
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="predictions.xlsx"'
        wb.save(response)
        return response
    except Exception as e:
        return HttpResponse(f"Error: {e}", status=400)

@login_required(login_url='login')
@csrf_exempt
def share_result_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            result_data = data.get('result', {})
            share_text = f"🎓 Placement Prediction: {result_data.get('placement_status', 'N/A')} with {result_data.get('probability', 0)}% probability!"
            return JsonResponse({'success': True, 'share_text': share_text})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

# ==================== DARK MODE ====================

def set_dark_mode(request):
    response = JsonResponse({'success': True})
    if request.GET.get('dark') == 'true':
        response.set_cookie('dark_mode', 'true', max_age=365*24*60*60)
    else:
        response.delete_cookie('dark_mode')
    return response