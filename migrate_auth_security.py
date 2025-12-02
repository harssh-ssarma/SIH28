#!/usr/bin/env python3
"""
🔐 Authentication Security Migration Script

Migrates from localStorage-based JWT to Google-like HttpOnly cookie authentication.
Run this after deploying the new authentication system.

Usage:
    python migrate_auth_security.py
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, cwd=None, description=""):
    """Run shell command and handle errors"""
    print(f"\n{'='*60}")
    print(f"🔄 {description or cmd}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        if result.stderr:
            print(f"⚠️  {result.stderr}")
        print(f"✅ Success: {description or cmd}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        print(f"   stdout: {e.stdout}")
        print(f"   stderr: {e.stderr}")
        return False


def main():
    # Get project root
    script_dir = Path(__file__).parent
    backend_django = script_dir / "backend" / "django"
    frontend = script_dir / "frontend"
    
    print("\n" + "="*60)
    print("🔐 AUTHENTICATION SECURITY MIGRATION")
    print("="*60)
    print("\nThis script will:")
    print("1. Create Django migrations for token blacklist")
    print("2. Apply migrations to database")
    print("3. Install frontend dependencies")
    print("4. Clear old localStorage tokens")
    print("\n⚠️  WARNING: Users will need to re-login after this migration")
    
    response = input("\nProceed? (y/N): ")
    if response.lower() != 'y':
        print("❌ Migration cancelled")
        return
    
    # Step 1: Create Django migrations
    if not run_command(
        "python manage.py makemigrations",
        cwd=backend_django,
        description="Creating Django migrations for token blacklist"
    ):
        print("\n❌ Failed to create migrations")
        sys.exit(1)
    
    # Step 2: Apply migrations
    if not run_command(
        "python manage.py migrate",
        cwd=backend_django,
        description="Applying database migrations"
    ):
        print("\n❌ Failed to apply migrations")
        sys.exit(1)
    
    # Step 3: Install frontend dependencies (if package.json changed)
    if frontend.exists():
        run_command(
            "npm install",
            cwd=frontend,
            description="Installing frontend dependencies"
        )
    
    # Step 4: Print manual steps
    print("\n" + "="*60)
    print("✅ MIGRATION COMPLETED SUCCESSFULLY")
    print("="*60)
    
    print("\n📋 MANUAL STEPS REQUIRED:")
    print("\n1. Restart Backend Server:")
    print("   cd backend/django")
    print("   python manage.py runserver")
    
    print("\n2. Restart Frontend Server:")
    print("   cd frontend")
    print("   npm run dev")
    
    print("\n3. Clear Browser Data (One-Time):")
    print("   - Open Browser DevTools (F12)")
    print("   - Go to Application/Storage tab")
    print("   - Clear localStorage")
    print("   - Clear cookies")
    print("   - Refresh page")
    
    print("\n4. Test Login:")
    print("   - Navigate to /login")
    print("   - Login with credentials")
    print("   - Verify authentication works")
    print("   - Check cookies in DevTools (should see access_token, refresh_token)")
    
    print("\n5. Verify Security:")
    print("   - Open Console: type document.cookie")
    print("   - Should NOT show access_token or refresh_token (HttpOnly)")
    print("   - This confirms tokens are secure ✅")
    
    print("\n" + "="*60)
    print("📚 For more details, see: AUTHENTICATION_ARCHITECTURE.md")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
