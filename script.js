// Global variables
let selectedMode = 'balanced';
let currentStory = null;

// DOM elements
const modeCards = document.querySelectorAll('.mode-card');
const generateBtn = document.getElementById('generateBtn');
const storyRequest = document.getElementById('storyRequest');
const loadingIndicator = document.getElementById('loadingIndicator');
const loadingText = document.getElementById('loadingText');
const storyOutput = document.getElementById('storyOutput');
const exampleBtns = document.querySelectorAll('.example-btn');
const newStoryBtn = document.getElementById('newStoryBtn');
const copyBtn = document.getElementById('copyBtn');
const shareBtn = document.getElementById('shareBtn');

// Initialize the app
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    addAnimations();
});

// Event Listeners
function initializeEventListeners() {
    // Mode selection
    modeCards.forEach(card => {
        card.addEventListener('click', function() {
            selectMode(this.dataset.mode);
        });
    });

    // Generate button
    generateBtn.addEventListener('click', generateStory);

    // Example buttons
    exampleBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            storyRequest.value = this.dataset.example;
            storyRequest.focus();
        });
    });

    // Story actions
    newStoryBtn.addEventListener('click', resetForm);
    copyBtn.addEventListener('click', copyStory);
    shareBtn.addEventListener('click', shareStory);

    // Enter key to generate
    storyRequest.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && e.ctrlKey) {
            generateStory();
        }
    });

    // Auto-resize textarea
    storyRequest.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = this.scrollHeight + 'px';
    });
}

// Mode Selection
function selectMode(mode) {
    selectedMode = mode;
    
    // Update UI
    modeCards.forEach(card => {
        card.classList.remove('active');
        if (card.dataset.mode === mode) {
            card.classList.add('active');
        }
    });

    // Add animation
    const activeCard = document.querySelector('.mode-card.active');
    activeCard.classList.add('success-animation');
    setTimeout(() => {
        activeCard.classList.remove('success-animation');
    }, 600);
}

// Generate Story
async function generateStory() {
    const request = storyRequest.value.trim();
    
    if (!request) {
        showNotification('Please enter a story request!', 'error');
        storyRequest.focus();
        return;
    }

    // Show loading state
    showLoading(true);
    generateBtn.disabled = true;
    
    try {
        // Make actual API call
        const response = await fetch('/api/generate-story', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                request: request,
                mode: selectedMode
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayStory(result);
            showNotification('Story generated successfully!', 'success');
        } else {
            throw new Error(result.error || 'Failed to generate story');
        }
        
    } catch (error) {
        console.error('Error generating story:', error);
        showNotification(`Error: ${error.message}`, 'error');
    } finally {
        showLoading(false);
        generateBtn.disabled = false;
    }
}

// Simulate Story Generation (Replace with actual API call)
async function simulateStoryGeneration(request, mode) {
    // Simulate API delay based on mode
    const delays = {
        fast: 3000,
        balanced: 8000,
        best: 15000
    };
    
    const delay = delays[mode];
    const steps = {
        fast: [
            'Categorizing request...',
            'Generating with strong constraints...',
            'Finalizing story...'
        ],
        balanced: [
            'Categorizing request...',
            'Generating multiple plans...',
            'Evaluating plans...',
            'Generating story from best plan...',
            'Judging story quality...',
            'Refining if needed...'
        ],
        best: [
            'Categorizing request...',
            'Generating multiple plans...',
            'Evaluating plans...',
            'Generating story from best plan...',
            'Judging story quality...',
            'First refinement...',
            'Second refinement...',
            'Final evaluation...'
        ]
    };

    const modeSteps = steps[mode];
    const stepDelay = delay / modeSteps.length;

    for (let i = 0; i < modeSteps.length; i++) {
        loadingText.textContent = modeSteps[i];
        await new Promise(resolve => setTimeout(resolve, stepDelay));
    }

    // Return mock result
    return generateMockStory(request, mode);
}

// Generate Mock Story
function generateMockStory(request, mode) {
    const stories = {
        dragon: {
            title: "Luna the Brave Little Dragon",
            content: `Once upon a time, in a magical kingdom high in the mountains, there lived a little dragon named Luna. Unlike other dragons who loved to breathe fire and soar through stormy skies, Luna was afraid of the dark.

Every evening when the sun began to set, Luna would hide in her cozy cave, trembling at the thought of the shadows that danced on her walls. "What if there are monsters in the dark?" she would whisper to herself.

One day, Luna's friend, a wise old owl named Oliver, noticed her fear. "Dear Luna," he said gently, "the dark is not something to fear. It's simply the absence of light, and it can be filled with wonder and magic."

That night, Oliver took Luna on a gentle flight through the starlit sky. As they soared together, Luna discovered that the darkness was filled with twinkling stars, glowing fireflies, and the soft light of the moon.

"Look, Luna," Oliver pointed out, "the night sky is like a beautiful blanket of lights. The dark makes the stars shine even brighter!"

From that moment on, Luna learned that courage isn't about not being afraid—it's about facing your fears with the help of friends and discovering the beauty that can be found in unexpected places.

And so, Luna the Brave Little Dragon learned to love both the light and the dark, knowing that each brought its own special kind of magic to her world.

The end.`,
            category: "fantasy",
            themes: ["courage", "friendship", "overcoming fears"],
            score: mode === 'fast' ? 7.8 : mode === 'balanced' ? 8.5 : 9.2
        },
        turtle: {
            title: "Timmy the Shy Turtle",
            content: `In a peaceful pond surrounded by tall reeds and colorful lily pads, there lived a young turtle named Timmy. Timmy was very shy and spent most of his time hiding in his shell, watching other animals play together from a distance.

"Timmy, come play with us!" the frogs would call out, but Timmy would just peek out from his shell and shake his head. "I'm too shy," he would whisper.

One sunny morning, Timmy noticed a new turtle swimming alone near the shore. Her name was Lily, and she looked just as shy as Timmy felt. Timmy watched her for a while, and his heart felt a little flutter of courage.

Taking a deep breath, Timmy slowly swam over to Lily. "Hello," he said quietly. "I'm Timmy. Would you like to explore the pond with me?"

Lily looked up with surprise and then smiled. "I'd love to!" she said. "I'm new here and don't know anyone yet."

Together, Timmy and Lily explored the pond, meeting friendly fish, gentle ducks, and even a wise old turtle who shared stories of faraway places. As they made more friends, Timmy realized that being shy didn't mean he couldn't make friends—it just meant he needed to be brave in his own gentle way.

From that day forward, Timmy became the pond's best friend-maker, always ready to welcome new animals with a kind smile and a patient heart.

And so, Timmy the Shy Turtle learned that friendship begins with a single hello and a willingness to be brave, even when you're feeling shy.

The end.`,
            category: "friendship",
            themes: ["friendship", "shyness", "courage"],
            score: mode === 'fast' ? 7.5 : mode === 'balanced' ? 8.3 : 9.0
        },
        robot: {
            title: "Robbie the Learning Robot",
            content: `In a bright, colorful classroom filled with curious children, there was a special robot named Robbie. Robbie could solve math problems in seconds, remember every fact in the encyclopedia, and even help with science experiments. But there was one thing Robbie couldn't understand—emotions.

"Why do the children laugh when they're happy?" Robbie asked his teacher, Ms. Johnson. "And why do they cry when they're sad? I don't understand these feelings."

Ms. Johnson smiled warmly. "Emotions are what make us human, Robbie. They help us connect with each other and understand the world around us."

Determined to learn about emotions, Robbie began to observe the children carefully. He noticed how Sarah's eyes lit up when she helped a friend, how Marcus's face scrunched up when he was concentrating, and how Emma's whole body bounced with excitement when she learned something new.

One day, Robbie saw a little boy named Alex sitting alone, looking sad. Remembering how the children comforted each other, Robbie rolled over and gently patted Alex's shoulder. "I may not understand sadness completely," Robbie said, "but I know that friends help each other feel better."

Alex looked up and smiled. "Thank you, Robbie. You're a good friend."

In that moment, Robbie felt something warm and wonderful inside his circuits. It wasn't quite happiness, and it wasn't quite pride, but it was definitely something special. Robbie had learned that understanding emotions wasn't about having them yourself—it was about caring for others and being there when they needed you.

And so, Robbie the Learning Robot discovered that the most important lessons aren't found in books or programs, but in the connections we make with the people around us.

The end.`,
            category: "learning",
            themes: ["learning", "emotions", "friendship"],
            score: mode === 'fast' ? 7.9 : mode === 'balanced' ? 8.6 : 9.3
        }
    };

    // Determine which story to use based on request
    let storyKey = 'dragon';
    if (request.toLowerCase().includes('turtle')) storyKey = 'turtle';
    if (request.toLowerCase().includes('robot')) storyKey = 'robot';

    const story = stories[storyKey];
    const apiCalls = {
        fast: 2,
        balanced: 5,
        best: 8
    };

    return {
        story: story.content,
        title: story.title,
        category: story.category,
        themes: story.themes,
        mode: mode,
        score: story.score,
        apiCalls: apiCalls[mode],
        iterations: mode === 'best' ? 3 : mode === 'balanced' ? 2 : 1,
        request: request
    };
}

// Display Story
function displayStory(result) {
    currentStory = result;
    const metadata = result.metadata || {};
    
    // Update metadata
    document.getElementById('storyMode').textContent = `${(metadata.mode || 'unknown').toUpperCase()} Mode`;
    document.getElementById('storyCategory').textContent = (metadata.category || 'unknown').charAt(0).toUpperCase() + (metadata.category || 'unknown').slice(1);
    document.getElementById('storyScore').textContent = `Score: ${metadata.score || 'N/A'}/10`;
    document.getElementById('apiCalls').textContent = `${metadata.api_calls || 'N/A'} API calls`;
    
    // Update story content
    const storyText = result.story || 'No story generated';
    document.getElementById('storyContent').innerHTML = `
        ${storyText.split('\n\n').map(paragraph => 
            paragraph.trim() ? `<p style="margin-bottom: 1rem;">${paragraph}</p>` : ''
        ).join('')}
    `;
    
    // Show story output
    storyOutput.classList.add('show');
    storyOutput.scrollIntoView({ behavior: 'smooth' });
}

// Story Actions
function resetForm() {
    storyRequest.value = '';
    storyOutput.classList.remove('show');
    storyRequest.focus();
    showNotification('Ready for a new story!', 'info');
}

function copyStory() {
    if (!currentStory) return;
    
    const storyText = `${currentStory.title}\n\n${currentStory.story}`;
    
    navigator.clipboard.writeText(storyText).then(() => {
        showNotification('Story copied to clipboard!', 'success');
    }).catch(() => {
        showNotification('Failed to copy story', 'error');
    });
}

function shareStory() {
    if (!currentStory) return;
    
    const shareText = `Check out this amazing bedtime story generated by AI: "${currentStory.title}"`;
    const shareUrl = window.location.href;
    
    if (navigator.share) {
        navigator.share({
            title: 'AI Generated Bedtime Story',
            text: shareText,
            url: shareUrl
        });
    } else {
        // Fallback to copying URL
        navigator.clipboard.writeText(shareUrl).then(() => {
            showNotification('Story URL copied to clipboard!', 'success');
        });
    }
}

// Loading State
function showLoading(show) {
    if (show) {
        loadingIndicator.classList.add('show');
        generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
    } else {
        loadingIndicator.classList.remove('show');
        generateBtn.innerHTML = '<i class="fas fa-magic"></i> Generate Story';
    }
}

// Notifications
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(notification => notification.remove());
    
    // Create notification
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        </div>
    `;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#4CAF50' : type === 'error' ? '#f44336' : '#2196F3'};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        z-index: 1000;
        animation: slideInRight 0.3s ease;
        max-width: 300px;
    `;
    
    // Add animation styles
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideInRight {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        .notification-content {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
    `;
    document.head.appendChild(style);
    
    // Add to page
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideInRight 0.3s ease reverse';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Animations
function addAnimations() {
    // Add fade-in animation to main content
    const mainContent = document.querySelector('.main-content');
    mainContent.classList.add('fade-in');
    
    // Add staggered animation to mode cards
    modeCards.forEach((card, index) => {
        setTimeout(() => {
            card.classList.add('slide-up');
        }, index * 100);
    });
}

// Modal functions
function showAbout() {
    document.getElementById('aboutModal').classList.add('show');
}

function closeModal() {
    document.getElementById('aboutModal').classList.remove('show');
}

// Close modal when clicking outside
document.addEventListener('click', function(e) {
    const modal = document.getElementById('aboutModal');
    if (e.target === modal) {
        closeModal();
    }
});

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Escape key to close modal
    if (e.key === 'Escape') {
        closeModal();
    }
    
    // Ctrl+Enter to generate story
    if (e.ctrlKey && e.key === 'Enter') {
        generateStory();
    }
});

// Add some fun interactions
function addFunInteractions() {
    // Add click effects to buttons
    const buttons = document.querySelectorAll('button');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Create ripple effect
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.cssText = `
                position: absolute;
                width: ${size}px;
                height: ${size}px;
                left: ${x}px;
                top: ${y}px;
                background: rgba(255,255,255,0.3);
                border-radius: 50%;
                transform: scale(0);
                animation: ripple 0.6s ease-out;
                pointer-events: none;
            `;
            
            this.style.position = 'relative';
            this.style.overflow = 'hidden';
            this.appendChild(ripple);
            
            setTimeout(() => ripple.remove(), 600);
        });
    });
    
    // Add ripple animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes ripple {
            to {
                transform: scale(2);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
}

// Initialize fun interactions
document.addEventListener('DOMContentLoaded', addFunInteractions);
