from django.contrib.auth.decorators import user_passes_test

def instructor_required(function=None, redirect_field_name=None, login_url='/auth/login'):
    """
    Decorator for views that checks that the user is logged in and is an instructor,
    redirects to the login page if not.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.role == 'INSTRUCTOR',
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def student_required(function=None, redirect_field_name=None, login_url='/auth/login'):
    """
    Decorator for views that checks that the user is logged in and is a student,
    redirects to the login page if not.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.role == 'STUDENT',
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
