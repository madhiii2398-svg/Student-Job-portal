# Student Job Portal

A complete web application built with Python Flask that allows students to register, log in, browse and apply for jobs, and track their application status. It also includes an admin panel for managing jobs and applications.

## Features

### Student Features
- **Registration & Login** - Students can create an account and log in securely using Flask sessions
- **Job Listing** - Browse all available jobs on the jobs page
- **Job Search** - Case-insensitive search by job title, company name, or required skills
- **Apply for Jobs** - Apply for any job with one click (duplicate applications are prevented)
- **Dashboard** - View all submitted applications and their current statuses (Applied, Shortlisted, Selected, Rejected)
- **Profile** - View registered profile details on the dashboard
- **Logout** - Securely log out of the account

### Admin Features
- **Admin Login** - Dedicated admin login page (credentials: `admin` / `admin123`)
- **Admin Dashboard** - Overview of total jobs, applications, and registered students
- **Add Job** - Post new job listings with title, company, description, skills, location, and salary
- **View All Applications** - See every application submitted by all students
- **Update Application Status** - Change application status to Applied, Shortlisted, Selected, or Rejected
- **Delete Jobs** - Remove job listings (also removes related applications)
- **Logout** - Securely log out of the admin panel

## Tech Stack
- **Backend:** Python Flask
- **Frontend:** HTML, CSS (responsive blue/white theme)
- **Data Storage:** JSON files (students.json, jobs.json, applications.json)
- **Sessions:** Flask sessions for student and admin authentication

## Project Structure

```
student-job-portal/
├── app.py                 # Main Flask application with all routes
├── students.json          # Student account data
├── jobs.json              # Job listings data
├── applications.json      # Job application records
├── static/
│   └── style.css          # Responsive blue/white stylesheet
├── templates/
│   ├── index.html         # Home page with featured jobs
│   ├── register.html      # Student registration page
│   ├── login.html         # Student login page
│   ├── jobs.html          # Job listing with search
│   ├── dashboard.html     # Student dashboard
│   ├── admin_login.html   # Admin login page
│   ├── admin.html         # Admin dashboard
│   └── add_job.html       # Add new job page
└── README.md             # This file
```

## Installation & Running Instructions

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Step 1: Install Flask
Open a terminal and run:

```bash
pip install flask
```

### Step 2: Run the Application
Navigate to the project directory and run:

```bash
python app.py
```

### Step 3: Open in Browser
Open your web browser and go to:

```
http://127.0.0.1:5000
```

## Usage Guide

### For Students
1. Click **Register** on the home page to create a new account
2. Fill in your name, email, password, qualification, and skills
3. After registration, **Login** with your email and password
4. Browse jobs on the **Jobs** page and use the search bar to find jobs by title, company, or skills
5. Click **Apply Now** on any job to apply
6. Visit your **Dashboard** to see all applications and their statuses

### For Admin
1. Go to `http://127.0.0.1:5000/admin/login`
2. Enter the credentials:
   - **Username:** `admin`
   - **Password:** `admin123`
3. Use the admin dashboard to:
   - View statistics (total jobs, applications, students)
   - Add new jobs
   - View all applications
   - Update application statuses using the dropdown next to each application
   - Delete jobs

## Default Data
The application comes pre-loaded with 6 sample job listings in `jobs.json`. The `students.json` and `applications.json` files start empty and are populated as users register and apply.

## Notes
- Passwords are stored as SHA-256 hashes (not plaintext)
- Duplicate job applications by the same student for the same job are automatically prevented
- The UI is fully responsive and works on mobile, tablet, and desktop screens
