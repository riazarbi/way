# Real-Time AI Hypothesis Evaluation System

## Overview
A simple Flask web application that provides real-time AI-powered hypothesis evaluation. Users can submit hypotheses through a web form and receive immediate feedback with scoring and detailed justifications.

## Prerequisites
- Python 3.7 or higher
- python3-venv package (install with: `sudo apt install python3-venv` on Ubuntu/Debian)
- Internet connection for optional Gemini AI API integration

## Quick Start

### 1. Environment Setup
```bash
# Clone or navigate to project directory
cd /path/to/hypothesis-evaluation-system

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Application
```bash
# Start the server
python3 app.py

# Or use Flask's development server
flask --app app run --debug
```

### 3. Access the Application
Open your browser and navigate to: http://localhost:5000

## Configuration

### API Key Setup (Optional)
The system can integrate with Google's Gemini AI for enhanced evaluation. Without an API key, it uses intelligent mock responses.

#### To enable Gemini AI integration:
1. Get a Gemini API key from Google AI Studio
2. Set the environment variable:
   ```bash
   export GEMINI_API_KEY="your-api-key-here"
   ```
3. Restart the application

#### Security Best Practices:
- Never commit API keys to version control
- Use environment variables or secure key management systems
- Consider using a `.env` file for local development:
  ```bash
  echo "GEMINI_API_KEY=your-api-key-here" > .env
  # Add .env to your .gitignore file
  ```

## System Architecture

### Core Components
- **Flask Web Server**: Handles HTTP requests and serves the web interface
- **Gemini AI Client**: Manages AI API integration with fallback to mock responses
- **Response Processing**: Formats AI responses for web display with proper error handling
- **Single-File Design**: All functionality contained in `app.py` for simplicity

### Dependencies (7 total)
- **Flask 3.1.1**: Main web framework
- **Supporting packages**: blinker, click, itsdangerous, jinja2, markupsafe, werkzeug

## Usage

### Web Interface
1. Navigate to http://localhost:5000
2. Enter your hypothesis in the text area
3. Click "Evaluate Hypothesis"
4. View the AI evaluation results with score and detailed feedback

### API Endpoints
- `GET /`: Main form interface
- `POST /`: Hypothesis evaluation submission
- `GET /health`: System health check

## Troubleshooting

### Common Issues

**Problem**: "Module 'flask' not found"
```bash
# Solution: Ensure virtual environment is activated and dependencies installed
source venv/bin/activate
pip install -r requirements.txt
```

**Problem**: "Port 5000 already in use"
```bash
# Solution: Use a different port
python3 app.py --port 5001
# Or kill the process using port 5000
lsof -ti:5000 | xargs kill -9
```

**Problem**: "Permission denied" when creating virtual environment
```bash
# Solution: Install python3-venv package
sudo apt update
sudo apt install python3-venv
```

**Problem**: Application starts but form doesn't work
- Check browser console for JavaScript errors
- Verify the form submission URL matches your server address
- Try submitting a hypothesis with at least 10 characters

**Problem**: Slow response times
- The system includes intelligent mock responses when Gemini API is not configured
- Response times should be <100ms for mock responses
- Check network connectivity if using live Gemini API

### Debugging

**Enable detailed logging**:
```bash
# The application includes comprehensive logging by default
# Check console output for detailed request/response information
```

**Test system components**:
```bash
# Verify Flask installation
python3 -c "import flask; print(f'Flask version: {flask.__version__}')"

# Test application startup
python3 -c "from app import app; print('Application imports successfully')"

# Check health endpoint
curl http://localhost:5000/health
```

## Demonstration Script

### Test Cases for System Validation

Run these test cases to validate system functionality:

#### Test Case 1: Well-Structured Hypothesis
**Input**: 
```
Due to: Low conversion rates on our product page (currently 2.1%)
If: We add customer testimonials and social proof above the fold
Then: This will increase user trust and confidence
Measured by: 15% increase in conversion rate over 4 weeks
```
**Expected**: Score of "Very Good" or "Good" with positive feedback on structure

#### Test Case 2: Basic Hypothesis
**Input**: 
```
Improving our website design will increase sales
```
**Expected**: Score of "Bad" or "Average" with suggestions for more specificity

#### Test Case 3: Data-Rich Hypothesis
**Input**: 
```
Based on analytics showing 65% mobile traffic, implementing mobile-first design will improve user engagement metrics by 25%
```
**Expected**: Score of "Good" or "Very Good" with recognition of data usage

#### Test Case 4: Empty Input
**Input**: (empty)
**Expected**: Error message requesting hypothesis input

#### Test Case 5: Very Long Hypothesis
**Input**: (500+ character hypothesis)
**Expected**: System handles gracefully, provides evaluation

### Performance Validation
- Response time should be <100ms for mock responses
- Form should be responsive and accessible
- System should handle concurrent requests appropriately
- Error states should display helpful messages

### Browser Compatibility
Test in major browsers:
- Chrome/Chromium
- Firefox
- Safari
- Edge

## Development Notes

### Code Organization
- Single-file architecture for simplicity
- Clear separation of concerns within the file
- Comprehensive error handling and logging
- HTML template embedded for minimal dependencies

### Testing Approach
- Manual testing via web interface
- Health check endpoint for monitoring
- Detailed logging for debugging
- Graceful fallback when AI API unavailable

### Future Enhancements
- Database integration for hypothesis history
- User authentication and personal workspaces
- Advanced AI model integration
- Batch hypothesis evaluation
- Export functionality for results

## System Validation Checklist

### Core Functionality
- [ ] Web server starts successfully on localhost:5000
- [ ] HTML form displays correctly
- [ ] Form accepts text input and validates minimum length
- [ ] Hypothesis evaluation returns structured results
- [ ] Results display with proper formatting and colors
- [ ] Error handling works for invalid inputs
- [ ] Health check endpoint responds correctly

### Performance Requirements
- [ ] Response time <500ms for 95% of requests (mock mode)
- [ ] System handles multiple concurrent requests
- [ ] Memory usage remains stable during operation
- [ ] No memory leaks during extended operation

### Constraint Compliance
- [ ] Single-file implementation (app.py)
- [ ] Exactly 7 dependencies as specified
- [ ] Runs on localhost:5000
- [ ] Uses Flask framework as required
- [ ] Includes proper error handling and logging

### Security Validation
- [ ] Input sanitization prevents XSS attacks
- [ ] API key properly secured via environment variables
- [ ] No sensitive data logged or exposed
- [ ] Proper error messages without system information disclosure

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review application logs for error details
3. Test with the provided demonstration script
4. Verify all prerequisites are met

The system is designed to be self-contained and easy to debug with comprehensive logging and clear error messages.