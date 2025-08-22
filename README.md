# Learning Management System (LMS)

A comprehensive Learning Management System built with Django and Django REST Framework, featuring user authentication, course management, interactive quizzes, and responsive design.

## 📋 Project Overview

This Learning Management System (LMS) is a full-featured web application that enables instructors to create and manage educational courses while allowing students to enroll, learn, and track their progress. The system supports both reading materials and interactive quizzes with automatic grading, providing a complete e-learning experience.

### Key Features:
- **User Management**: Role-based authentication (Instructor/Student)
- **Course Management**: Create, edit, and publish courses with sequential content
- **Lecture Types**: Support for reading materials (text, URLs, file uploads) and interactive quizzes
- **Progress Tracking**: Real-time progress monitoring with completion status
- **Quiz System**: Multiple-choice questions with automatic grading (70% pass threshold)
- **Responsive Design**: Mobile-first approach with Bootstrap 5
- **Search Functionality**: Course search by title, description, or instructor
- **File Upload**: Support for PDFs, images, and other educational materials

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- pip (Python package installer)
- Git

### Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd SCALER PROJECT
   ```

2. **Create and activate virtual environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Navigate to Django project directory**
   ```bash
   cd lms_backend
   ```

5. **Apply database migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Seed the database with sample data (optional)**
   ```bash
   python manage.py seed_data
   ```

## 🏃‍♂️ Running the Application

### Development Server
```bash
# Make sure you're in the lms_backend directory
cd lms_backend

# Start the development server
python manage.py runserver
```

### Access the Application
- Open your web browser and navigate to: `http://127.0.0.1:8000/` or `http://localhost:8000/`
- The application will be running and ready to use!

### Sample Data (if seeded)
- **Instructor Account**: `username: instructor1`, `password: testpassword`
- **Student Accounts**: `username: student1`, `password: testpassword` and `username: student2`, `password: testpassword`

## 🏗️ Project Architecture

### Technology Stack

#### Backend
- **Python 3.9+**: Chosen for its readability, extensive libraries, and strong community support
- **Django 5.x**: Full-featured web framework providing robust ORM, admin interface, and security features
- **Django REST Framework**: For building RESTful APIs with serialization, authentication, and permissions
- **SQLite**: Lightweight database for development (easily switchable to PostgreSQL for production)

#### Frontend
- **Bootstrap 5**: Modern CSS framework for responsive design and consistent UI components
- **Bootstrap Icons**: Icon library for consistent visual elements
- **Google Fonts**: Typography enhancement for better readability
- **Server-side rendering**: Django templates for SEO-friendly, fast-loading pages

#### Authentication & Security
- **JWT (JSON Web Tokens)**: Stateless authentication for API endpoints
- **Session Authentication**: Traditional Django session-based auth for web interface
- **CSRF Protection**: Built-in Django CSRF protection for form security
- **Role-based Access Control**: Custom decorators for instructor/student permissions

#### File Handling
- **Pillow**: Python Imaging Library for image processing and validation
- **Django File Storage**: Secure file upload handling with validation

### Project Structure
```
lms_backend/
├── lms_project/          # Django project settings and configuration
├── users/               # User management, authentication, and profiles
├── courses/             # Course creation and management
├── lectures/            # Lecture content (reading materials and quizzes)
├── quizzes/             # Quiz questions, answers, and grading
├── enrollments/         # Student course enrollment system
├── progress/            # Student progress tracking and completion
├── templates/           # HTML templates with Bootstrap 5
├── static/              # CSS, JavaScript, and static assets
├── media/               # User-uploaded files (PDFs, images, etc.)
└── manage.py           # Django management script
```

### Database Schema
- **Users**: Custom user model with roles (Instructor/Student) and profile information
- **Courses**: Course information with instructor relationship and publication status
- **Lectures**: Base lecture model with types (reading/quiz) and ordering
- **ReadingLectures**: Text content, URLs, and file attachments
- **QuizLectures**: Quiz-specific data with time constraints
- **Questions**: Multiple-choice questions with options and correct answers
- **Enrollments**: Student-course relationships
- **Progress**: Student progress tracking with completion status and scores
- **Messages**: Internal messaging system between users

### API Architecture
The application follows RESTful API principles with:
- **Resource-based URLs**: `/api/courses/`, `/api/lectures/`, etc.
- **HTTP methods**: GET, POST, PUT, DELETE for CRUD operations
- **Status codes**: Proper HTTP status codes for responses
- **Authentication**: JWT tokens for API access
- **Permissions**: Role-based access control for all endpoints

## 🎯 Key Design Decisions

### Why Django?
- **Rapid Development**: Django's "batteries-included" approach speeds up development
- **Admin Interface**: Built-in admin panel for content management
- **Security**: Django's security features protect against common web vulnerabilities
- **Scalability**: Django can handle high-traffic applications with proper optimization
- **Community**: Large, active community with extensive documentation and third-party packages

### Why Bootstrap 5?
- **Mobile-First**: Responsive design that works on all devices
- **Consistency**: Pre-built components ensure consistent UI/UX
- **Accessibility**: Built-in accessibility features
- **Customization**: Easy to customize with CSS variables and custom styles
- **Performance**: Lightweight and fast-loading

### Why SQLite for Development?
- **Simplicity**: No server setup required
- **Portability**: Database file can be easily shared and backed up
- **Performance**: Fast for development and small to medium applications
- **Django Integration**: Seamless integration with Django ORM

## 🔧 Development Features

### Code Quality
- **Modular Structure**: Each feature is a separate Django app
- **Clean Code**: Well-documented functions and classes
- **Type Hints**: Python type hints for better code clarity
- **Error Handling**: Comprehensive error handling with user-friendly messages

### Security Features
- **Authentication**: Multi-layered authentication system
- **Authorization**: Role-based access control throughout the application
- **Input Validation**: Form validation and sanitization
- **File Upload Security**: Secure file handling with type validation

### Performance Optimizations
- **Database Queries**: Optimized queries with select_related and prefetch_related
- **Static Files**: Proper static file serving and caching
- **Template Optimization**: Efficient template rendering
- **API Response**: Optimized API responses with proper serialization

## 🚀 Deployment Considerations

### Production Setup
1. **Database**: Switch to PostgreSQL for production
2. **Static Files**: Configure static file serving (nginx/Apache)
3. **Media Files**: Set up cloud storage (AWS S3, Google Cloud Storage)
4. **Environment Variables**: Secure configuration management
5. **SSL Certificate**: HTTPS for security
6. **Backup Strategy**: Regular database and file backups

### Environment Variables
```bash
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com
DATABASE_URL=postgresql://user:password@localhost/dbname
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the code comments

---

**Built with ❤️ using Django and Bootstrap 5**

*This Learning Management System demonstrates modern web development practices with a focus on user experience, security, and scalability.*
