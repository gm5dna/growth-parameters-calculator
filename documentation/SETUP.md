# Setup Guide

Quick setup instructions for running the Growth Parameters Calculator locally.

## Current Status

✅ **Application is ready to run!**

The app has been refactored with the following improvements completed:
- Modular architecture (constants, validation, calculations, models, utils)
- Client-side validation with localStorage persistence
- Loading states and ARIA labels
- Rate limiting (optional - disabled if Flask-Limiter not installed)

## Running the Application

### Quick Start

```bash
./run.sh
```

Then open your browser to: **http://localhost:8080**

### What You'll See

```
⚠ Flask-Limiter not installed - rate limiting disabled
 * Serving Flask app 'app'
 * Debug mode: off
 * Running on http://127.0.0.1:8080
```

**Note**: The Flask-Limiter warning is expected and doesn't affect functionality. Rate limiting is optional and will be enabled automatically if you install Flask-Limiter later.

## Optional: Install Rate Limiting

If you want to enable rate limiting (recommended for production):

```bash
source venv/bin/activate
pip install Flask-Limiter
```

Then restart the app. You'll see:
```
✓ Rate limiting enabled
```

## Optional: Install Testing Framework

If you want to run the unit tests:

```bash
source venv/bin/activate
pip install pytest pytest-cov
```

Then run tests:
```bash
pytest
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'flask_limiter'"

**This is expected!** The app has been updated to make Flask-Limiter optional. The app will run fine without it, just with rate limiting disabled.

If you want to enable rate limiting, install Flask-Limiter:
```bash
source venv/bin/activate
pip install Flask-Limiter
```

### "ModuleNotFoundError: No module named 'constants'" (or validation, calculations, etc.)

Make sure you're in the correct directory:
```bash
cd "/Users/stuart/Documents/working/coding/growth app"
./run.sh
```

### Virtual Environment Issues

If you have issues with the virtual environment:

```bash
# Recreate the virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate

# Install core dependencies
pip install Flask rcpchgrowth python-dateutil gunicorn

# Run the app
python app.py
```

## What Works Without Optional Dependencies

The following features work perfectly without Flask-Limiter or pytest:

✅ All growth calculations (age, weight, height, BMI, OFC)
✅ Interactive growth charts
✅ Height velocity
✅ Body surface area (Boyd and cBNF)
✅ GH dose calculator
✅ Mid-parental height
✅ Gestational age correction
✅ Client-side validation
✅ Form persistence (localStorage)
✅ Basic/Advanced mode toggle
✅ All user interface features

### What's Disabled Without Optional Dependencies

❌ Rate limiting (Flask-Limiter) - API endpoints unprotected
❌ Unit tests (pytest) - Can't run test suite

## Production Deployment

For production deployment, install all dependencies:

```bash
source venv/bin/activate
pip install Flask rcpchgrowth python-dateutil gunicorn Flask-Limiter

# For production, also consider Redis for rate limiting storage:
# Update app.py: storage_uri="redis://localhost:6379"
```

Then use Gunicorn:
```bash
gunicorn --bind 0.0.0.0:8080 --workers 4 app:app
```

## Documentation

- **User Guide**: [docs/USER_GUIDE.md](docs/USER_GUIDE.md)
- **Features**: [docs/FEATURES.md](docs/FEATURES.md)
- **Technical Docs**: [docs/TECHNICAL.md](docs/TECHNICAL.md)
- **Improvements**: [docs/IMPROVEMENTS_SUMMARY.md](docs/IMPROVEMENTS_SUMMARY.md)

## Next Steps

1. **Run the app**: `./run.sh`
2. **Open browser**: http://localhost:8080
3. **Try a calculation**: Enter patient data and click Calculate
4. **View charts**: Click "Show Growth Charts" after calculation
5. **Read documentation**: Check out the docs/ folder for detailed guides

## Need Help?

- **Issues**: https://github.com/gm5dna/growth-parameters-calculator/issues
- **Discussions**: https://github.com/gm5dna/growth-parameters-calculator/discussions
- **Documentation**: [docs/README.md](docs/README.md)
