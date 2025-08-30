#!/usr/bin/env python
"""
Deployment preparation script for Social Media Platform
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return None

def check_requirements():
    """Check if all requirements are installed."""
    print("📋 Checking requirements...")
    
    # Check if requirements.txt exists
    if not Path('requirements.txt').exists():
        print("❌ requirements.txt not found")
        return False
    
    # Try to import key packages
    try:
        import django
        import PIL
        import decouple
        print(f"✅ Django {django.get_version()} installed")
        print("✅ All required packages are available")
        return True
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        return False

def run_tests():
    """Run all tests."""
    return run_command("python manage.py test", "Running tests")

def collect_static():
    """Collect static files."""
    return run_command("python manage.py collectstatic --noinput", "Collecting static files")

def check_migrations():
    """Check for unapplied migrations."""
    result = run_command("python manage.py showmigrations --plan", "Checking migrations")
    if result and "[ ]" in result:
        print("⚠️  Unapplied migrations found. Run 'python manage.py migrate'")
        return False
    print("✅ All migrations are applied")
    return True

def security_check():
    """Run Django security checks."""
    return run_command("python manage.py check --deploy", "Running security checks")

def optimize_images():
    """Optimize images for production."""
    return run_command("python manage.py optimize_images", "Optimizing images")

def create_production_settings():
    """Create production settings template."""
    production_settings = """
# Production settings for Social Media Platform
import os
from .settings import *

# Security settings
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com']

# Database (replace with your production database)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files (use cloud storage in production)
# AWS S3 example:
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
# AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
# AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')

# Security
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
"""
    
    settings_dir = Path('social_platform')
    production_file = settings_dir / 'production_settings.py'
    
    if not production_file.exists():
        with open(production_file, 'w') as f:
            f.write(production_settings)
        print("✅ Created production_settings.py template")
    else:
        print("ℹ️  production_settings.py already exists")

def create_deployment_files():
    """Create deployment configuration files."""
    
    # Procfile for Heroku
    procfile_content = "web: gunicorn social_platform.wsgi --log-file -"
    with open('Procfile', 'w') as f:
        f.write(procfile_content)
    
    # runtime.txt for Heroku
    runtime_content = "python-3.11.0"
    with open('runtime.txt', 'w') as f:
        f.write(runtime_content)
    
    # Docker configuration
    dockerfile_content = """
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "social_platform.wsgi:application", "--bind", "0.0.0.0:8000"]
"""
    
    with open('Dockerfile', 'w') as f:
        f.write(dockerfile_content)
    
    print("✅ Created deployment files (Procfile, runtime.txt, Dockerfile)")

def main():
    """Main deployment preparation function."""
    print("🚀 Social Media Platform - Deployment Preparation")
    print("=" * 50)
    
    # Change to project directory
    os.chdir(Path(__file__).parent)
    
    # Check requirements
    if not check_requirements():
        print("❌ Requirements check failed. Install missing packages first.")
        sys.exit(1)
    
    # Run tests
    if not run_tests():
        print("❌ Tests failed. Fix issues before deployment.")
        sys.exit(1)
    
    # Check migrations
    if not check_migrations():
        print("❌ Migration check failed.")
        sys.exit(1)
    
    # Security check
    if not security_check():
        print("⚠️  Security check found issues. Review before deployment.")
    
    # Collect static files
    collect_static()
    
    # Optimize images
    optimize_images()
    
    # Create production files
    create_production_settings()
    create_deployment_files()
    
    print("\n🎉 Deployment preparation completed!")
    print("\n📝 Next steps:")
    print("1. Review and update production_settings.py with your production values")
    print("2. Set up your production database")
    print("3. Configure your web server (nginx, Apache, etc.)")
    print("4. Set up SSL certificates")
    print("5. Configure environment variables")
    print("6. Deploy to your hosting platform")
    
    print("\n🔧 Useful commands:")
    print("- Run with production settings: python manage.py runserver --settings=social_platform.production_settings")
    print("- Create superuser: python manage.py createsuperuser")
    print("- Migrate database: python manage.py migrate")

if __name__ == "__main__":
    main()
