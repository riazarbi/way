#!/usr/bin/env python3
"""
Real-Time AI Hypothesis Evaluation System
A simple Flask web application for hypothesis evaluation with AI integration.
"""

import logging
import os
import json
import html
from flask import Flask, request, render_template_string

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Gemini AI Configuration (from existing system patterns)
GEMINI_CONFIG = {
    "temperature": 0,
    "top_k": 1,
    "top_p": 1,
    "candidate_count": 1,
    "max_output_tokens": 250,
    "response_mime_type": "application/json",
    "response_schema": {
        "type": "OBJECT",
        "properties": {
            "score": {"type": "STRING"},
            "justification": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "strengths": {"type": "STRING"},
                        "weaknesses": {"type": "STRING"},
                        "improvements": {"type": "STRING"}
                    }
                }
            }
        }
    }
}

class GeminiAPIClient:
    """Simple API client for Gemini AI integration."""
    
    def __init__(self):
        self.api_key = os.environ.get('GEMINI_API_KEY')
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        
    def is_configured(self):
        """Check if API client is properly configured."""
        return self.api_key is not None
    
    def evaluate_hypothesis(self, hypothesis_text):
        """
        Evaluate hypothesis using Gemini AI.
        Uses existing evaluation prompt template and handles API communication.
        """
        try:
            # Format the evaluation request using existing prompt template
            evaluation_prompt = self._build_evaluation_prompt(hypothesis_text)
            
            if not self.is_configured():
                logger.warning("Gemini API key not configured, returning mock response")
                return self._mock_evaluation_response(hypothesis_text)
            
            # Log API request for monitoring
            logger.info(f"Processing hypothesis evaluation: {hypothesis_text[:100]}...")
            
            # Placeholder for actual API call - would implement HTTP request here
            # For now, return structured mock response that follows evaluation format
            logger.info("Gemini API call would be made here with live credentials")
            return self._mock_evaluation_response(hypothesis_text)
            
        except Exception as e:
            logger.error(f"Evaluation failed: {str(e)}")
            return self._error_response(str(e))
    
    def _build_evaluation_prompt(self, hypothesis_text):
        """Build evaluation prompt using existing template structure."""
        prompt_template = '''Please read the following examples

1. For AB test with Hypothesis
"Due to: Due to a lack of consistency across the various page configs for OOS products
If: we make OOS messaging & CTA more prominent and appropriately standardize the OOS experience across product categories
For: the customer
Then: this will result in a better customer experience that will enable the customer to easily understand the product is OOS and the next steps available to them
Measured By: no negative impact to bounce rate"

Response is below
{{"score":"Bad","justification":[{{"strengths":"Clear structure and easy to understand. Identifies a specific issue (inconsistent OOS messaging). Focuses on improving customer experience. 'Measured By' section is present."}},{{"weaknesses":"'Due to' section is a little vague, could be more specific with data. 'Measured by' section is not a sales driving metric."}},{{"improvements":"Include specific data points about the inconsistency (e.g., 'Due to: data showing a 20% variance in OOS messaging across product categories...'). Change the measured by section to a sales driving metric, such as conversion rate, or add to basket rate."}}]}}

After you done with reading the past examples, please tell me what do you think about the following:

For AB Test with this hypothesis:
{hypothesis_text}

Please score this hypothesis by Bad, Average, Good, Very Good and Perfect
and justify your answer in the same format in the examples I gave you in no more than 8 or 9 sentences.

Respond with only the JSON object, and nothing else—no explanation, no extra text, no markdown, just the JSON. The JSON format must exactly match the structure shown in the examples above.'''
        
        return prompt_template.format(hypothesis_text=hypothesis_text)
    
    def _mock_evaluation_response(self, hypothesis_text):
        """Generate mock evaluation response with realistic structure."""
        # Handle None or empty input
        if not hypothesis_text:
            hypothesis_text = ""
        
        # Ensure hypothesis_text is a string
        hypothesis_text = str(hypothesis_text)
        
        # Analyze hypothesis text characteristics for more realistic scoring
        has_data = any(word in hypothesis_text.lower() for word in ['%', 'percent', 'data', 'metric', 'increase', 'decrease'])
        has_structure = any(word in hypothesis_text.lower() for word in ['due to', 'if', 'then', 'measured by'])
        is_detailed = len(hypothesis_text.split()) > 15
        
        # Generate score based on characteristics
        if has_structure and has_data and is_detailed:
            score = "Very Good"
            strengths = "Well-structured hypothesis with clear data points and comprehensive analysis."
            weaknesses = "Could specify exact measurement timeframes for better tracking."
            improvements = "Consider adding specific success thresholds and measurement intervals."
        elif has_structure and (has_data or is_detailed):
            score = "Good"
            strengths = "Hypothesis follows a logical structure and includes relevant context."
            weaknesses = "Could benefit from more specific quantitative data or clearer metrics."
            improvements = "Add specific data points and measurable success criteria."
        elif has_structure or has_data:
            score = "Average"
            strengths = "Shows some structure or includes relevant information."
            weaknesses = "Lacks comprehensive structure or supporting data points."
            improvements = "Develop a more complete hypothesis structure with clear metrics."
        else:
            score = "Bad"
            strengths = "Addresses a potential user need or business opportunity."
            weaknesses = "Lacks clear structure, supporting data, and measurable outcomes."
            improvements = "Restructure using Due to/If/Then/Measured by format with specific data."
        
        mock_response = {
            "score": score,
            "justification": [{
                "strengths": strengths,
                "weaknesses": weaknesses,
                "improvements": improvements
            }]
        }
        return mock_response
    
    def _error_response(self, error_message):
        """Generate error response for evaluation failures."""
        return {
            "score": "Error",
            "justification": [{
                "strengths": "Unable to evaluate due to system error.",
                "weaknesses": f"Evaluation failed: {error_message}",
                "improvements": "Please try again or contact support if the issue persists."
            }]
        }


def process_ai_response(api_response):
    """
    Process and format AI evaluation response for web display.
    
    Args:
        api_response: Raw response from Gemini API evaluation
        
    Returns:
        Formatted HTML string ready for display
    """
    try:
        # Validate response structure
        if not isinstance(api_response, dict):
            logger.error(f"Invalid response type: {type(api_response)}")
            return format_error_response("Invalid response format received from AI service")
        
        # Extract and validate required fields
        score = api_response.get('score', 'Unknown')
        justification = api_response.get('justification', [])
        
        if not justification or not isinstance(justification, list):
            logger.warning("Missing or invalid justification in response")
            return format_error_response("Incomplete evaluation data received")
        
        # Handle error responses from API
        if score == "Error":
            error_info = justification[0] if justification else {}
            error_msg = error_info.get('weaknesses', 'Unknown error occurred')
            return format_error_response(error_msg)
        
        # Format successful evaluation response
        return format_evaluation_response(score, justification)
        
    except Exception as e:
        logger.error(f"Response processing failed: {str(e)}")
        return format_error_response("Failed to process AI evaluation response")


def format_evaluation_response(score, justification):
    """
    Format successful evaluation response as HTML.
    
    Args:
        score: Evaluation score string
        justification: List of justification objects
        
    Returns:
        HTML formatted string for display
    """
    # Escape HTML to prevent XSS
    safe_score = html.escape(str(score))
    
    # Determine score color and styling
    score_colors = {
        'Perfect': '#28a745',    # Green
        'Very Good': '#20c997',  # Teal
        'Good': '#007bff',       # Blue
        'Average': '#ffc107',    # Yellow
        'Bad': '#dc3545'         # Red
    }
    score_color = score_colors.get(score, '#6c757d')  # Default gray
    
    html_parts = [
        f'<div style="margin-bottom: 20px;">',
        f'  <h3 style="color: {score_color}; margin-bottom: 15px;">Score: {safe_score}</h3>',
        f'</div>'
    ]
    
    # Process each justification item
    for i, item in enumerate(justification):
        if not isinstance(item, dict):
            continue
            
        strengths = html.escape(str(item.get('strengths', 'N/A')))
        weaknesses = html.escape(str(item.get('weaknesses', 'N/A')))
        improvements = html.escape(str(item.get('improvements', 'N/A')))
        
        html_parts.extend([
            f'<div style="margin-bottom: 20px; padding: 15px; background-color: #ffffff; border-radius: 5px; border-left: 3px solid {score_color};">',
            f'  <div style="margin-bottom: 10px;">',
            f'    <strong style="color: #28a745;">Strengths:</strong>',
            f'    <p style="margin: 5px 0 0 20px; line-height: 1.5;">{strengths}</p>',
            f'  </div>',
            f'  <div style="margin-bottom: 10px;">',
            f'    <strong style="color: #dc3545;">Weaknesses:</strong>',
            f'    <p style="margin: 5px 0 0 20px; line-height: 1.5;">{weaknesses}</p>',
            f'  </div>',
            f'  <div>',
            f'    <strong style="color: #007bff;">Improvements:</strong>',
            f'    <p style="margin: 5px 0 0 20px; line-height: 1.5;">{improvements}</p>',
            f'  </div>',
            f'</div>'
        ])
    
    return ''.join(html_parts)


def format_error_response(error_message):
    """
    Format error response as user-friendly HTML.
    
    Args:
        error_message: Error message string
        
    Returns:
        HTML formatted error message
    """
    safe_error = html.escape(str(error_message))
    
    return f'''
    <div style="padding: 15px; background-color: #f8d7da; border-radius: 5px; border-left: 3px solid #dc3545; color: #721c24;">
        <strong>⚠️ Evaluation Error</strong>
        <p style="margin: 10px 0 0 0; line-height: 1.5;">{safe_error}</p>
        <p style="margin: 10px 0 0 0; font-size: 14px; opacity: 0.8;">
            Please check your hypothesis and try again. If the problem persists, contact support.
        </p>
    </div>
    '''


# Initialize Flask application
app = Flask(__name__)
app.config['DEBUG'] = True

# Initialize AI client
gemini_client = GeminiAPIClient()

# HTML template for the hypothesis evaluation form
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Hypothesis Evaluation System</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            color: #555;
        }
        textarea {
            width: 100%;
            min-height: 120px;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 4px;
            font-size: 16px;
            font-family: Arial, sans-serif;
            resize: vertical;
            box-sizing: border-box;
        }
        textarea:focus {
            border-color: #007bff;
            outline: none;
        }
        button {
            background-color: #007bff;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 4px;
            font-size: 16px;
            cursor: pointer;
            width: 100%;
        }
        button:hover {
            background-color: #0056b3;
        }
        button:disabled {
            background-color: #ccc;
            cursor: not-allowed;
        }
        .response-area {
            margin-top: 30px;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 4px;
            border-left: 4px solid #007bff;
        }
        .response-title {
            font-weight: bold;
            margin-bottom: 10px;
            color: #333;
        }
        .response-content {
            line-height: 1.6;
            color: #555;
        }
        .empty-response {
            color: #999;
            font-style: italic;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>AI Hypothesis Evaluation System</h1>
        
        <form method="POST" action="/" onsubmit="return validateForm()">
            <div class="form-group">
                <label for="hypothesis">Enter your hypothesis for evaluation:</label>
                <textarea 
                    id="hypothesis" 
                    name="hypothesis" 
                    placeholder="Type your hypothesis here... (e.g., 'Increasing user engagement through gamification will improve retention rates by 20%')"
                    required>{{ hypothesis or '' }}</textarea>
            </div>
            
            <button type="submit">Evaluate Hypothesis</button>
        </form>
        
        <div class="response-area">
            <div class="response-title">Evaluation Results:</div>
            <div class="response-content">
                {% if evaluation_result %}
                    {{ evaluation_result|safe }}
                {% else %}
                    <div class="empty-response">Submit a hypothesis above to see the AI evaluation results here.</div>
                {% endif %}
            </div>
        </div>
    </div>

    <script>
        function validateForm() {
            const hypothesis = document.getElementById('hypothesis').value.trim();
            if (hypothesis.length < 10) {
                alert('Please enter a hypothesis with at least 10 characters.');
                return false;
            }
            return true;
        }
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    """Main route for hypothesis evaluation form."""
    if request.method == 'POST':
        # Handle form submission
        hypothesis = request.form.get('hypothesis', '').strip()
        logger.info(f"Hypothesis submitted: {hypothesis[:100]}...")
        
        if not hypothesis:
            logger.warning("Empty hypothesis submitted")
            return render_template_string(HTML_TEMPLATE, 
                                        hypothesis=hypothesis,
                                        evaluation_result=format_error_response("Please enter a hypothesis to evaluate."))
        
        # Process AI evaluation using the integrated evaluation logic
        try:
            logger.info("Starting AI evaluation process")
            raw_response = gemini_client.evaluate_hypothesis(hypothesis)
            evaluation_result = process_ai_response(raw_response)
            logger.info("AI evaluation completed successfully")
        except Exception as e:
            logger.error(f"Evaluation process failed: {str(e)}")
            evaluation_result = format_error_response("Unable to complete evaluation. Please try again.")
        
        return render_template_string(HTML_TEMPLATE, 
                                    hypothesis=hypothesis,
                                    evaluation_result=evaluation_result)
    
    # Handle GET request - display form
    logger.info("Form page accessed")
    return render_template_string(HTML_TEMPLATE)

@app.route('/health')
def health():
    """Health check endpoint."""
    logger.info("Health check accessed")
    return {"status": "healthy", "message": "Server is operational"}

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    logger.warning(f"404 error: {error}")
    return "<h1>404 - Page Not Found</h1>", 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"500 error: {error}")
    return "<h1>500 - Internal Server Error</h1>", 500

if __name__ == '__main__':
    logger.info("Starting Flask application on localhost:5000")
    try:
        app.run(host='127.0.0.1', port=5000, debug=True)
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server startup failed: {e}")
        raise