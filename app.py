from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our story generator
try:
    from main import generate_bedtime_story
    STORY_GENERATOR_AVAILABLE = True
except ImportError:
    STORY_GENERATOR_AVAILABLE = False

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')

@app.route('/')
def index():
    """Serve the main HTML page."""
    return render_template('index.html')

@app.route('/api/generate-story', methods=['POST'])
def generate_story():
    """
    API endpoint to generate bedtime stories.
    
    Expected JSON payload:
    {
        "request": "A story about a brave little rabbit",
        "mode": "balanced"  // "fast", "balanced", or "best"
    }
    
    Returns:
    {
        "success": true,
        "story": "...",
        "metadata": {
            "mode": "balanced",
            "category": "animal",
            "themes": ["courage", "friendship"],
            "score": 8.5,
            "api_calls": 6,
            "iterations": 2
        }
    }
    """
    try:
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        story_request = data.get('request', '').strip()
        mode = data.get('mode', 'balanced')
        
        # Validate inputs
        if not story_request:
            return jsonify({
                'success': False,
                'error': 'Story request is required'
            }), 400
        
        if mode not in ['fast', 'balanced', 'best']:
            return jsonify({
                'success': False,
                'error': 'Mode must be "fast", "balanced", or "best"'
            }), 400
        
        # Check if story generator is available
        if not STORY_GENERATOR_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'Story generator not available. Please check API key configuration.'
            }), 500
        
        # Generate story using our Tier 2 system
        try:
            result = generate_bedtime_story(story_request, mode=mode)
            
            # Prepare response
            response = {
                'success': True,
                'story': result.get('story', ''),
                'metadata': {
                    'mode': result.get('mode', mode),
                    'category': result.get('category', 'unknown'),
                    'themes': result.get('themes', []),
                    'tone': result.get('tone', 'gentle'),
                    'score': result.get('final_score', 'N/A'),
                    'api_calls': result.get('api_calls', 0),
                    'iterations': result.get('iterations', 1),
                    'estimated_quality': result.get('estimated_quality', 'N/A')
                }
            }
            
            return jsonify(response)
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Error generating story: {str(e)}'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'story_generator_available': STORY_GENERATOR_AVAILABLE,
        'api_key_configured': bool(os.environ.get('OPENAI_API_KEY')),
        'version': '1.0.0'
    })

@app.route('/api/examples', methods=['GET'])
def get_examples():
    """Get example story requests."""
    examples = [
        {
            'text': 'A story about a little dragon who is afraid of the dark',
            'icon': 'dragon',
            'category': 'fantasy'
        },
        {
            'text': 'A story about a shy turtle who makes new friends',
            'icon': 'turtle',
            'category': 'friendship'
        },
        {
            'text': 'An adventure where a robot learns about emotions',
            'icon': 'robot',
            'category': 'learning'
        },
        {
            'text': 'A story about a brave bunny who goes on an adventure',
            'icon': 'rabbit',
            'category': 'adventure'
        },
        {
            'text': 'A magical story about a unicorn who helps others',
            'icon': 'unicorn',
            'category': 'magic'
        }
    ]
    
    return jsonify({
        'success': True,
        'examples': examples
    })

@app.route('/api/modes', methods=['GET'])
def get_modes():
    """Get available story generation modes."""
    modes = [
        {
            'id': 'fast',
            'name': 'Fast Mode',
            'description': 'Quick stories for simple requests',
            'api_calls': 2,
            'time': '5-8 seconds',
            'quality': '7-8/10',
            'icon': 'rocket'
        },
        {
            'id': 'balanced',
            'name': 'Balanced Mode',
            'description': 'Default mode with great quality and efficiency',
            'api_calls': '5-6',
            'time': '12-15 seconds',
            'quality': '8-9/10',
            'icon': 'balance-scale'
        },
        {
            'id': 'best',
            'name': 'Best Mode',
            'description': 'Premium quality with guaranteed refinements',
            'api_calls': '8-10',
            'time': '20-30 seconds',
            'quality': '9-10/10',
            'icon': 'gem'
        }
    ]
    
    return jsonify({
        'success': True,
        'modes': modes
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    # Check if we're in development mode
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    print("🌟 AI Bedtime Story Generator - Web Server")
    print("=" * 50)
    print(f"Story Generator Available: {STORY_GENERATOR_AVAILABLE}")
    print(f"API Key Configured: {bool(os.environ.get('OPENAI_API_KEY'))}")
    print(f"Debug Mode: {debug_mode}")
    print("=" * 50)
    
    if not STORY_GENERATOR_AVAILABLE:
        print("⚠️  Warning: Story generator not available!")
        print("Please check your OpenAI API key configuration.")
    
    # Run the app
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=debug_mode
    )
