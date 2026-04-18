from django.db import models
from django.contrib.auth.models import User

class Prediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20)
    probability = models.FloatField()
    skill_score = models.IntegerField()
    cgpa = models.FloatField()
    
    # Store all input features
    gender = models.CharField(max_length=10)
    hs_percentage = models.FloatField()
    hs_board = models.CharField(max_length=50)
    twelfth_percentage = models.FloatField()
    twelfth_board = models.CharField(max_length=50)
    twelfth_stream = models.CharField(max_length=50)
    degree_percentage = models.FloatField()
    degree_type = models.CharField(max_length=50)
    work_experience = models.CharField(max_length=10)
    etest_percentage = models.FloatField()
    final_year_percentage = models.FloatField()
    course = models.CharField(max_length=50)
    course_specialization = models.CharField(max_length=100)
    internship = models.IntegerField()
    
    def __str__(self):
        return f"{self.user.username} - {self.status} - {self.timestamp}"
