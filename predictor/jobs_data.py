JOBS_DATABASE = [
    {
        'title': 'Software Engineer',
        'company': 'Google',
        'min_cgpa': 7.5,
        'min_skill': 85,
        'salary': '25-35 LPA',
        'location': 'Bangalore',
        'skills': ['Python', 'DSA', 'System Design']
    },
    {
        'title': 'Data Scientist',
        'company': 'Microsoft',
        'min_cgpa': 7.0,
        'min_skill': 80,
        'salary': '20-30 LPA',
        'location': 'Hyderabad',
        'skills': ['Python', 'ML', 'Statistics']
    },
    {
        'title': 'Web Developer',
        'company': 'Amazon',
        'min_cgpa': 6.5,
        'min_skill': 75,
        'salary': '12-20 LPA',
        'location': 'Chennai',
        'skills': ['React', 'Node.js', 'MongoDB']
    },
    {
        'title': 'Business Analyst',
        'company': 'Deloitte',
        'min_cgpa': 6.0,
        'min_skill': 70,
        'salary': '8-12 LPA',
        'location': 'Mumbai',
        'skills': ['Excel', 'SQL', 'Communication']
    },
    {
        'title': 'Intern',
        'company': 'Startup',
        'min_cgpa': 5.5,
        'min_skill': 60,
        'salary': '3-6 LPA',
        'location': 'Remote',
        'skills': ['Basic Programming', 'Learning Attitude']
    }
]

def get_job_recommendations(cgpa, skill_score, course):
    recommended = []
    for job in JOBS_DATABASE:
        if cgpa >= job['min_cgpa'] and skill_score >= job['min_skill']:
            recommended.append(job)
    return recommended[:5]