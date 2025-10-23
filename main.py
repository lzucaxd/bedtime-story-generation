import os
import json
import logging
from typing import Dict, Any, List
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

"""
Multi-Stage Bedtime Story Generator - Advanced System
A sophisticated 6-stage pipeline with comprehensive quality assurance and efficiency optimizations.

KEY FEATURES:
1. MULTI-PLAN SELECTION: Generate 3 plans, judge them, pick best (saves ~60% tokens)
2. STRUCTURED CRITIQUE: Actionable feedback with specific locations and fixes
3. ADAPTIVE MODES: Fast/Balanced/Best quality paths for different needs
4. NAME TRACKING: Prevents repetitive character names across sessions

Architecture:
User Request → Categorization → Name Generation → [Multi-Plan → Plan Judge] → Story Generator → [LLM Judge → Refinement] → Final Story
"""

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize OpenAI client
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    print("OPENAI_API_KEY environment variable not set!")
    print("Please set your API key: export OPENAI_API_KEY='your-api-key-here'")
    print("The system will not work without a valid API key.\n")
    client = None
else:
    client = OpenAI(api_key=api_key)
MODEL = "gpt-3.5-turbo"

# Global name tracking to prevent repetition across sessions
USED_NAMES = set()

def reset_name_tracking():
    """Reset the global name tracking to start fresh."""
    global USED_NAMES
    USED_NAMES.clear()
    logger.info("Name tracking reset, all names available again")

# ============= CORE COMPONENTS =============

def generate_unique_character_names(request: str, category_info: Dict[str, Any], num_names: int = 3) -> List[str]:
    """
    Generate unique character names based on story context.
    
    Args:
        request: User's story request
        category_info: Category information from categorizer
        num_names: Number of names to generate
        
    Returns:
        List of unique character names
    """
    logger.info(f"🎭 Generating {num_names} unique character names...")
    
    category = category_info["category"]
    themes = ", ".join(category_info["themes"])
    
    # Add used names to the prompt to avoid repetition
    used_names_str = ", ".join(list(USED_NAMES)[:10]) if USED_NAMES else "None yet"
    
    prompt = f"""
You are a creative children's book author who specializes in memorable character names.

Story Request: "{request}"
Category: {category}
Themes: {themes}

NAMES ALREADY USED (avoid these): {used_names_str}

Generate {num_names} unique, memorable character names for this story. Consider:

NAMING GUIDELINES:
- Age-appropriate for children 5-10
- Easy to pronounce and remember
- Culturally diverse and inclusive
- Match the story theme/category
- Avoid common overused names (like "Max", "Luna", "Bella", "Charlie") 
- Make them distinctive and memorable
- DO NOT use any names from the "NAMES ALREADY USED" list above

For {category} stories with themes like {themes}, create names that:
- Fit the story's world and setting
- Are unique but not too unusual
- Sound pleasant when read aloud
- Are easy for children to remember

Respond with ONLY the names, one per line, no numbers or explanations.
"""

    try:
        if not client:
            # Fallback names if API not available
            fallback_names = {
                "animal": ["Zara", "Koda", "Nina"],
                "adventure": ["Aria", "Finn", "Maya"],
                "friendship": ["Leo", "Sage", "Ivy"],
                "fantasy": ["Orion", "Luna", "Kai"],
                "bedtime": ["Nova", "River", "Skye"],
                "learning": ["Phoenix", "Willow", "Sage"],
                "family": ["Ember", "Forest", "Rain"],
                "magic": ["Stella", "Cosmo", "Aurora"]
            }
            final_names = fallback_names.get(category, ["Zara", "Koda", "Nina"])[:num_names]
            USED_NAMES.update(final_names)
            return final_names
        
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=100
        )
        
        names_text = response.choices[0].message.content.strip()
        names = []
        for line in names_text.split('\n'):
            name = line.strip()
            # Remove numbers and dots from the beginning
            if name:
                # Remove leading numbers, dots, and spaces
                clean_name = name.lstrip('0123456789. ')
                if clean_name:
                    names.append(clean_name)
        
        # Ensure we have enough names
        while len(names) < num_names:
            names.append(f"Character{len(names) + 1}")
        
        # Track the names to avoid repetition in future generations
        final_names = names[:num_names]
        USED_NAMES.update(final_names)
        
        logger.info(f"Generated names: {final_names}")
        logger.info(f"Total names used so far: {len(USED_NAMES)}")
        return final_names
        
    except Exception as e:
        logger.error(f"Error generating names: {e}")
        # Fallback names
        fallback_names = ["Zara", "Koda", "Nina", "Aria", "Finn"]
        final_names = fallback_names[:num_names]
        USED_NAMES.update(final_names)
        return final_names

def categorize_story_request(request: str) -> Dict[str, Any]:
    """
    Stage 1: Categorizer
    Analyzes the user's story request to determine category, themes, and tone.
    
    Args:
        request: User's story request
        
    Returns:
        Dictionary with category, themes list, and tone
    """
    logger.info("Stage 1: Categorizing story request...")
    
    prompt = f"""
You are a children's story expert and best selling author specializing in bedtime stories for ages 5-10. 
Analyze the following story request and categorize it with themes and tone.

Story Request: "{request}"

Provide a JSON response with:
- "category": One of [adventure, friendship, fantasy, bedtime, learning, family, animal, magic]
- "themes": List of 2-4 themes (e.g., ["courage", "friendship", "kindness"])
- "tone": One of [gentle, playful, adventurous, magical, cozy, educational]

Guidelines:
- Choose the most appropriate category based on the request
- Identify positive themes suitable for children
- Select a tone that matches the request and is appropriate for bedtime
- Be consistent and objective in your categorization

Respond ONLY with valid JSON, no additional text.
"""

    try:
        if not client:
            raise Exception("OpenAI client not initialized. Please set OPENAI_API_KEY environment variable.")
        
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=200
        )
        
        category_info = json.loads(response.choices[0].message.content)
        logger.info(f"Categorized as: {category_info['category']} - {category_info['tone']} tone")
        return category_info
        
    except Exception as e:
        logger.error(f"Error in categorization: {e}")
        # Fallback categorization
        return {"category": "bedtime", "themes": ["friendship", "kindness"], "tone": "gentle"}

# ============= MULTI-PLAN SELECTION =============

def create_multiple_plans(request: str, category_info: Dict[str, Any], num_plans: int = 3) -> List[Dict]:
    """
    Generate multiple story plan variants.
    
    This catches structural problems BEFORE expensive story generation.
    Better to evaluate 3 short plans than generate 3 full stories.
    
    Args:
        request: Original user request
        category_info: Output from categorizer
        num_plans: Number of plans to generate (default 3)
        
    Returns:
        List of plan objects with different approaches:
        [
            {"plan_text": "...", "approach": "emotional"},
            {"plan_text": "...", "approach": "action"},
            {"plan_text": "...", "approach": "discovery"}
        ]
        
    API Calls: 1
    Temperature: 0.7 (creative variety)
    """
    logger.info(f"Generating {num_plans} different story plans...")
    
    category = category_info["category"]
    themes = ", ".join(category_info["themes"])
    tone = category_info["tone"]
    
    prompt = f"""
You are a creative story planner. Generate {num_plans} DIFFERENT story approaches for the same request. 
Make each approach unique and compelling:

Approach 1 (Emotional): Focus on character feelings, relationships, personal growth
Approach 2 (Action): Focus on adventure, challenges, exciting events  
Approach 3 (Discovery): Focus on learning, exploration, problem-solving

For each approach, create a brief plan (4-6 sentences) with:
- Setup: Character and setting
- Conflict: What problem arises?
- Journey: How do they address it?
- Resolution: How does it end positively?

Request: "{request}"
Category: {category}
Themes: {themes}
Tone: {tone}

Return JSON array with {num_plans} plans:
[
    {{"plan_text": "SETUP: ... CONFLICT: ... JOURNEY: ... RESOLUTION: ...", "approach": "emotional"}},
    {{"plan_text": "SETUP: ... CONFLICT: ... JOURNEY: ... RESOLUTION: ...", "approach": "action"}},
    {{"plan_text": "SETUP: ... CONFLICT: ... JOURNEY: ... RESOLUTION: ...", "approach": "discovery"}}
]
"""

    try:
        if not client:
            raise Exception("OpenAI client not initialized. Please set OPENAI_API_KEY environment variable.")
        
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=800
        )
        
        plans = json.loads(response.choices[0].message.content)
        logger.info(f"✅ Generated {len(plans)} different story plans")
        for i, plan in enumerate(plans):
            logger.info(f"   Plan {i+1} ({plan['approach']}): {plan['plan_text'][:100]}...")
        return plans
        
    except Exception as e:
        logger.error(f"❌ Error generating multiple plans: {e}")
        # Fallback single plan
        return [{"plan_text": "A gentle bedtime story with a positive message and happy ending.", "approach": "emotional"}]

def judge_plans(plans: List[Dict], request: str, category_info: Dict[str, Any]) -> Dict:
    """
    Evaluate all plans and select the best one.
    
    ONE API call evaluates all plans together, saving tokens compared to
    generating multiple full stories.
    
    Args:
        plans: List of plan objects from create_multiple_plans
        request: Original user request
        category_info: Output from categorizer
        
    Returns:
        {
            "plans": [...],  # Each with scores and analysis
            "best_plan_index": 1,
            "best_plan": {...},
            "reasoning": "..."
        }
        
    API Calls: 1
    Temperature: 0.2 (analytical)
    """
    logger.info("Judging all story plans to select the best...")
    
    category = category_info["category"]
    themes = ", ".join(category_info["themes"])
    
    # Format plans for evaluation
    plans_text = ""
    for i, plan in enumerate(plans):
        plans_text += f"\nPlan {i+1} ({plan['approach']}):\n{plan['plan_text']}\n"
    
    prompt = f"""
You are a story editor evaluating {len(plans)} different story approaches. 
Score each plan on these criteria (1-10 each):

1. ORIGINALITY: Is it creative and unique, or generic?
2. NARRATIVE_POTENTIAL: Will this make a compelling, engaging story?
3. ALIGNMENT: Does it match the user's specific request?
4. CHILD_APPEAL: Will kids ages 5-10 find this interesting and age-appropriate?
5. BEDTIME_SUITABILITY: Is it appropriate for bedtime?
6. EDUCATIONAL_VALUE: Is it educational and teaches a lesson?
7. POSITIVE_MESSAGE: Does it have a positive message or lesson?
8. COZY_ATMOSPHERE: Does it have a cozy atmosphere?
9. CLEAR_CHARACTER_DEVELOPMENT: Does it have clear character development?
10. CLEAR_PLOT: Does it have a clear plot?
11. CLEAR_RESOLUTION: Does it have a clear resolution?










Original request: "{request}"
Target category: {category}
Target themes: {themes}

Plans to evaluate:
{plans_text}

For each plan, provide:
- Scores for each criterion (1-10)
- Total score
- Key strengths
- Key weaknesses

Then select the BEST plan and explain why.

Return JSON:
{{
    "plans": [
        {{
            "index": 0,
            "scores": {{"originality": 8, "narrative_potential": 7, "alignment": 9, "child_appeal": 8}},
            "total": 32,
            "strengths": ["Clear character motivation", "Age-appropriate conflict"],
            "weaknesses": ["Generic resolution", "Limited emotional depth"]
        }},
        ...
    ],
    "best_plan_index": 1,
    "best_plan": {{"plan_text": "...", "approach": "..."}},
    "reasoning": "Plan 2 has the strongest emotional arc and clearest resolution..."
}}
"""

    try:
        if not client:
            raise Exception("OpenAI client not initialized. Please set OPENAI_API_KEY environment variable.")
        
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=1000
        )
        
        judge_result = json.loads(response.choices[0].message.content)
        best_index = judge_result["best_plan_index"]
        logger.info(f"✅ Plan evaluation complete. Best plan: #{best_index + 1} ({plans[best_index]['approach']})")
        logger.info(f"   Reasoning: {judge_result['reasoning'][:100]}...")
        return judge_result
        
    except Exception as e:
        logger.error(f"❌ Error judging plans: {e}")
        # Fallback to first plan
        return {
            "plans": [{"index": 0, "total": 30, "strengths": ["Simple structure"], "weaknesses": ["Generic"]}],
            "best_plan_index": 0,
            "best_plan": plans[0],
            "reasoning": "Fallback selection due to error"
        }

# ============= STRUCTURED CRITIQUE =============

def judge_story_v2(story: str, request: str, category_info: Dict[str, Any]) -> Dict:
    """
    Judge story with structured, actionable feedback.
    
    Instead of vague suggestions like "improve engagement", this provides
    specific issues with locations, problems, and concrete fixes.
    
    Args:
        story: Generated story text
        request: Original user request
        category_info: Output from categorizer
        
    Returns:
        {
            "scores": {...},
            "overall_score": 7.8,
            "verdict": "ACCEPT" | "REVISE",
            "strengths": ["...", "..."],
            "issues": [
                {
                    "location": "paragraph 2",
                    "problem": "Dragon's fear is stated but never explained",
                    "fix": "Add one sentence showing WHY dragon fears dark",
                    "severity": "moderate"
                }
            ]
        }
        
    API Calls: 1
    Temperature: 0.2 (analytical)
    """
    logger.info("🔍 TIER 2: Structured critique of story...")
    
    category = category_info["category"]
    themes = ", ".join(category_info["themes"])
    
    prompt = f"""
You are an expert children's literature editor. Evaluate this story with SPECIFIC, ACTIONABLE feedback.

Story to evaluate:
{story}

Original request: "{request}"
Target category: {category}
Target themes: {themes}

Provide scores (1-10) for:
- age_appropriateness: Vocabulary and content suitable for ages 5-10
- engagement: How interesting and captivating the story is
- structure: Clear beginning, middle, end with good flow
- educational_value: Positive lessons or values taught
- bedtime_suitability: Calming and appropriate for bedtime

For any score below 8, identify SPECIFIC issues:
- WHERE in the story (which paragraph/section: "opening", "middle section", "paragraph 2", "ending")
- WHAT is the problem (be concrete and specific)
- HOW to fix it (actionable suggestion with example)
- SEVERITY (critical/moderate/minor)

Also list the story's strengths to preserve during revision.

Return JSON(example shown below):
{{
    "scores": {{
        "age_appropriateness": 8,
        "engagement": 7,
        "structure": 9,
        "educational_value": 8,
        "bedtime_suitability": 7
    }},
    "overall_score": 7.8,
    "verdict": "ACCEPT",
    "strengths": [
        "Clear narrative arc with satisfying resolution",
        "Age-appropriate vocabulary throughout"
    ],
    "issues": [
        {{
            "location": "opening paragraph",
            "problem": "Character introduction is rushed - we don't know what dragon looks like",
            "fix": "Add 1-2 sentences describing dragon's appearance and personality",
            "severity": "moderate"
        }},
        {{
            "location": "middle section", 
            "problem": "Transition between scenes is abrupt",
            "fix": "Add transitional sentence like 'The next evening, Dragon decided to try again.'",
            "severity": "minor"
        }}
    ]
}}

Acceptance criteria: Overall score >= 7.5 = "ACCEPT", < 7.5 = "REVISE"
"""

    try:
        if not client:
            raise Exception("OpenAI client not initialized. Please set OPENAI_API_KEY environment variable.")
        
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=800
        )
        
        judge_result = json.loads(response.choices[0].message.content)
        verdict = judge_result["verdict"]
        score = judge_result["overall_score"]
        issues_count = len(judge_result.get("issues", []))
        
        logger.info(f"✅ Structured critique complete. Verdict: {verdict} (Score: {score:.1f})")
        if issues_count > 0:
            logger.info(f"   Issues found: {issues_count}")
            for issue in judge_result.get("issues", []):
                logger.info(f"   - [{issue['severity']}] {issue['location']}: {issue['problem']}")
        
        return judge_result
        
    except Exception as e:
        logger.error(f"Error in structured story evaluation: {e}")
        # Fallback judgment
        return {
            "scores": {"age_appropriateness": 8, "engagement": 7, "structure": 8, "educational_value": 7, "bedtime_suitability": 8},
            "overall_score": 7.6,
            "verdict": "ACCEPT",
            "strengths": ["Age-appropriate content", "Good structure"],
            "issues": []
        }

def refine_story_v2(story: str, judge_feedback: Dict, request: str) -> str:
    """
    Refine story by addressing specific issues.
    
    Makes surgical fixes based on structured feedback instead of rewriting everything.
    This preserves good parts while fixing only what needs fixing.
    
    Args:
        story: Current story text
        judge_feedback: Output from judge_story_v2
        request: Original user request
        
    Returns:
        Refined story text
        
    API Calls: 1
    Temperature: 0.6 (balanced refinement)
    """
    logger.info("🔧 TIER 2: Targeted refinement based on structured feedback...")
    
    issues = judge_feedback.get("issues", [])
    strengths = judge_feedback.get("strengths", [])
    
    if not issues:
        logger.info("✅ No issues to fix - story is already good!")
        return story
    
    # Format issues for the prompt
    issues_text = format_issues_list(issues)
    
    prompt = f"""
You are a best selling children's story author and editor making targeted revisions. Address each specific issue while preserving the story's strengths. You are writing for ages 5-10.

Original story:
{story}

Specific issues to fix:
{issues_text}

Story strengths to preserve:
{', '.join(strengths)}

Instructions:
1. Address each issue exactly as specified
2. Make MINIMAL changes - only what's needed for each fix
3. Preserve all strengths and good parts
4. Keep the overall structure, tone, and flow
5. Do not rewrite sections that aren't mentioned in issues
6. Maintain the same story length (300-500 words)

Return the revised story with targeted improvements.
"""

    try:
        if not client:
            raise Exception("OpenAI client not initialized. Please set OPENAI_API_KEY environment variable.")
        
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=800
        )
        
        refined_story = response.choices[0].message.content.strip()
        logger.info(f"Story refined ({len(refined_story)} characters)")
        logger.info(f"Fixed {len(issues)} specific issues")
        return refined_story
        
    except Exception as e:
        logger.error(f"Error refining story: {e}")
        return story  # Return original if refinement fails

# ============= STORY GENERATION =============

def generate_story(request: str, plan: Dict, category_info: Dict[str, Any]) -> str:
    """
    Generate complete story from the best plan.
    
    Args:
        request: Original user request
        plan: Best plan selected by judge_plans
        category_info: Output from categorizer
        
    Returns:
        Complete bedtime story (300-500 words)
        
    API Calls: 1
    Temperature: 0.8 (creative)
    """
    logger.info("Generating complete story from best plan...")
    
    category = category_info["category"]
    themes = ", ".join(category_info["themes"])
    tone = category_info["tone"]
    approach = plan["approach"]
    plan_text = plan["plan_text"]
    
    # Generate unique character names
    character_names = generate_unique_character_names(request, category_info, 3)
    names_list = ", ".join(character_names)
    
    prompt = f"""
You are a beloved children's bedtime story author writing for ages 5-10.
Write a complete bedtime story based on the provided plan.

User Request: "{request}"
Story Plan: "{plan_text}"
Approach: {approach}
Category: {category}
Themes: {themes}
Tone: {tone}

CHARACTER NAMES TO USE: {names_list}
Use these unique character names in your story. Do not use any other names.

Write a complete story (300-500 words) with:

CONTENT REQUIREMENTS:
- Age-appropriate vocabulary and concepts
- Engaging but calming narrative perfect for bedtime
- Positive message or gentle lesson
- Clear beginning, middle, and end
- No scary elements, violence, or intense conflict

WRITING STYLE:
- Use simple, clear sentences
- Include some dialogue to make it engaging
- Use descriptive but not overly complex language
- Create a warm, cozy atmosphere
- End with a peaceful, satisfying conclusion

STRUCTURE:
- Strong opening that hooks the child
- Gentle conflict that's easily resolved
- Positive resolution with lesson learned
- Cozy, peaceful ending

Respond with ONLY the story text, no additional commentary.
"""

    try:
        if not client:
            raise Exception("OpenAI client not initialized. Please set OPENAI_API_KEY environment variable.")
        
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=800
        )
        
        story = response.choices[0].message.content.strip()
        logger.info(f"Story generated ({len(story)} characters)")
        return story
        
    except Exception as e:
        logger.error(f"Error generating story: {e}")
        return "I'm sorry, I couldn't generate the story right now. Please try again."

def generate_story_with_strong_constraints(request: str, category_info: Dict[str, Any]) -> str:
    """
    Generate story with extra constraints for fast mode.
    
    Includes harder requirements to get it right first time without judging.
    This is used in FAST mode to skip the judging/refinement pipeline.
    
    Args:
        request: Original user request
        category_info: Output from categorizer
        
    Returns:
        Complete bedtime story (300-500 words)
        
    API Calls: 1
    Temperature: 0.7 (slightly more constrained)
    """
    logger.info("Generating story with strong constraints for fast mode...")
    
    category = category_info["category"]
    themes = ", ".join(category_info["themes"])
    
    # Generate unique character names
    character_names = generate_unique_character_names(request, category_info, 3)
    names_list = ", ".join(character_names)
    tone = category_info["tone"]
    
    prompt = f"""
You are a critically-acclaimed children's bedtime story author. Write a BEST-SELLING story on the first try.

User Request: "{request}"
Category: {category}
Themes: {themes}
Tone: {tone}

CHARACTER NAMES TO USE: {names_list}
Use these unique character names in your story. Do not use any other names.

Write a complete story (300-500 words) that MUST be:

QUALITY REQUIREMENTS (get it right the first time):
- Age-appropriate vocabulary and concepts for ages 5-10
- Engaging but calming narrative perfect for bedtime
- Clear beginning, middle, and end with smooth transitions
- Positive message or gentle lesson woven naturally
- No scary elements, violence, or intense conflict
- Perfect flow from setup through resolution

WRITING EXCELLENCE:
- Use simple, clear sentences
- Include engaging dialogue between characters
- Use descriptive but accessible language
- Create a warm, cozy atmosphere throughout
- End with a peaceful, satisfying conclusion
- Ensure smooth transitions between scenes
- Make characters relatable and sympathetic

STRUCTURE PERFECTION:
- Hook the child immediately in opening
- Present conflict that's age-appropriate and resolvable
- Show character growth or learning
- Resolve with positive lesson learned
- End with cozy, peaceful conclusion

This story will NOT be judged or refined, so it must be excellent on the first try.

Respond with ONLY the story text, no additional commentary.
"""

    try:
        if not client:
            raise Exception("OpenAI client not initialized. Please set OPENAI_API_KEY environment variable.")
        
        response = client.chat.completions.create(
            model=MODEL,
        messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=800
        )
        
        story = response.choices[0].message.content.strip()
        logger.info(f"✅ Fast-mode story generated ({len(story)} characters)")
        return story
        
    except Exception as e:
        logger.error(f"❌ Error generating fast-mode story: {e}")
        return "I'm sorry, I couldn't generate the story right now. Please try again."

# ============= ADAPTIVE MODES =============

def generate_bedtime_story_fast(request: str) -> Dict:
    """
    FAST MODE: Categorize → Generate with strong constraints → Done
    
    Perfect for:
    - Simple requests
    - Development testing
    - Free tier users
    - Quick iterations
    
    API calls: 2
    """
    logger.info("🚀 FAST MODE: Quick story generation with strong constraints")
    
    try:
        # Stage 1: Categorize
        category_info = categorize_story_request(request)
        
        # Stage 2: Generate with strong constraints (no judging needed)
        story = generate_story_with_strong_constraints(request, category_info)
        
        # Prepare result
        result = {
            "story": story,
            "category": category_info["category"],
            "themes": category_info["themes"],
            "tone": category_info["tone"],
            "mode": "fast",
            "final_score": "N/A (not evaluated)",
            "api_calls": 2,
            "iterations": 1,
            "estimated_quality": "7-8/10",
            "metadata": {
                "plan_used": "strong_constraints",
                "judging_skipped": True
            }
        }
        
        logger.info(f"🎉 Fast mode complete! API calls: {result['api_calls']}")
        return result
        
    except Exception as e:
        logger.error(f"Error in fast mode: {e}")
        return {
            "story": "I'm sorry, there was an error generating your story. Please try again.",
            "mode": "fast",
            "api_calls": 0,
            "iterations": 0,
            "metadata": {"error": str(e)}
        }

def generate_bedtime_story_balanced(request: str) -> Dict:
    """
    BALANCED MODE: Full pipeline with conditional refinement
    
    Perfect for:
    - Default mode for most users
    - Typical story requests
    - Good quality without excessive cost
    
    API calls: 5-6
    Time: 12-15 seconds
    Quality: 8-9/10
    """
    logger.info("⚖️ BALANCED MODE: Full pipeline with conditional refinement")
    
    try:
        # Stage 1: Categorize
        category_info = categorize_story_request(request)
        
        # Stage 2: Multi-plan selection
        plans = create_multiple_plans(request, category_info, num_plans=3)
        plan_judge_result = judge_plans(plans, request, category_info)
        best_plan = plan_judge_result["best_plan"]
        
        # Stage 3: Generate story
        story = generate_story(request, best_plan, category_info)
        
        # Stage 4: Judge and conditionally refine
        judge_result = judge_story_v2(story, request, category_info)
        
        iterations = 1
        if judge_result["verdict"] == "REVISE":
            logger.info("🔄 Story needs improvement - refining...")
            story = refine_story_v2(story, judge_result, request)
            judge_result = judge_story_v2(story, request, category_info)
            iterations = 2
        
        # Prepare result
        result = {
            "story": story,
            "category": category_info["category"],
            "themes": category_info["themes"],
            "tone": category_info["tone"],
            "mode": "balanced",
            "final_score": judge_result["overall_score"],
            "api_calls": 5 + (iterations - 1),  # Base 5 + refinement calls
            "iterations": iterations,
            "estimated_quality": "8-9/10",
            "metadata": {
                "plan_approach": best_plan["approach"],
                "plan_reasoning": plan_judge_result["reasoning"],
                "judge_verdict": judge_result["verdict"],
                "issues_fixed": len(judge_result.get("issues", []))
            }
        }
        
        logger.info(f"🎉 Balanced mode complete! Final score: {result['final_score']:.1f}, API calls: {result['api_calls']}")
        return result
        
    except Exception as e:
        logger.error(f"Error in balanced mode: {e}")
        return {
            "story": "I'm sorry, there was an error generating your story. Please try again.",
            "mode": "balanced",
            "api_calls": 0,
            "iterations": 0,
            "metadata": {"error": str(e)}
        }

def generate_bedtime_story_best(request: str) -> Dict:
    """
    BEST MODE: Full pipeline with guaranteed 2 refinements
    
    Perfect for:
    - Premium users
    - Special occasions
    - Published content
    - Complex requests
    
    API calls: 8-10
    """
    logger.info("BEST MODE: Full pipeline with guaranteed refinements")
    
    try:
        # Stage 1: Categorize
        category_info = categorize_story_request(request)
        
        # Stage 2: Multi-plan selection
        plans = create_multiple_plans(request, category_info, num_plans=3)
        plan_judge_result = judge_plans(plans, request, category_info)
        best_plan = plan_judge_result["best_plan"]
        
        # Stage 3: Generate story
        story = generate_story(request, best_plan, category_info)
        
        # Stage 4: Guaranteed 2 refinement cycles
        total_issues_fixed = 0
        
        for iteration in range(2):
            logger.info(f"🔄 Refinement cycle {iteration + 1}/2...")
            judge_result = judge_story_v2(story, request, category_info)
            
            if judge_result["verdict"] == "ACCEPT" and iteration > 0:
                logger.info("Story meets quality standards, stopping refinement")
                break
            
            issues = judge_result.get("issues", [])
            if issues:
                story = refine_story_v2(story, judge_result, request)
                total_issues_fixed += len(issues)
                logger.info(f"   Fixed {len(issues)} issues in cycle {iteration + 1}")
            else:
                logger.info(f"   No issues to fix in cycle {iteration + 1}")
        
        # Final evaluation
        final_judge = judge_story_v2(story, request, category_info)
        
        # Prepare result
        result = {
            "story": story,
            "category": category_info["category"],
            "themes": category_info["themes"],
            "tone": category_info["tone"],
            "mode": "best",
            "final_score": final_judge["overall_score"],
            "api_calls": 8,  # Base pipeline + 2 guaranteed refinements
            "iterations": 3,  # Generate + 2 refinements
            "estimated_quality": "9-10/10",
            "metadata": {
                "plan_approach": best_plan["approach"],
                "plan_reasoning": plan_judge_result["reasoning"],
                "total_issues_fixed": total_issues_fixed,
                "final_verdict": final_judge["verdict"]
            }
        }
        
        logger.info(f"🎉 Best mode complete! Final score: {result['final_score']:.1f}, Issues fixed: {total_issues_fixed}")
        return result
        
    except Exception as e:
        logger.error(f"Error in best mode: {e}")
        return {
            "story": "I'm sorry, there was an error generating your story. Please try again.",
            "mode": "best",
            "api_calls": 0,
            "iterations": 0,
            "metadata": {"error": str(e)}
        }

# ============= MAIN ENTRY POINT =============

def generate_bedtime_story(request: str, mode: str = "balanced") -> Dict:
    """
    Main entry point with mode selection.
    
    Args:
        request: User's story request
        mode: "fast" | "balanced" | "best"
        
    Returns:
        {
            "story": "...",
            "category": "...",
            "final_score": 8.5,
            "mode": "balanced",
            "api_calls": 6,
            "iterations": 1,
            "metadata": {...}
        }
    """
    print(f"\n{'='*60}")
    print(f"📖 BEDTIME STORY GENERATOR - {mode.upper()} MODE")
    print(f"{'='*60}\n")
    
    if mode == "fast":
        return generate_bedtime_story_fast(request)
    elif mode == "balanced":
        return generate_bedtime_story_balanced(request)
    elif mode == "best":
        return generate_bedtime_story_best(request)
    else:
        raise ValueError(f"Unknown mode: {mode}. Choose 'fast', 'balanced', or 'best'")

# ============= UTILITIES =============

def format_issues_list(issues: List[Dict]) -> str:
    """Format issues for refinement prompt."""
    formatted = []
    for i, issue in enumerate(issues, 1):
        formatted.append(f"""
Issue {i} [{issue['severity'].upper()}]:
  Location: {issue['location']}
  Problem: {issue['problem']}
  Fix: {issue['fix']}
        """)
    return "\n".join(formatted)

# ============= MAIN =============

def main():
    """Interactive CLI for story generation."""
    print("\n" + "="*60)
    print("BEDTIME STORY GENERATOR")
    print("="*60)
    
    # Example requests
    examples = [
        "A story about a little dragon who is afraid of the dark",
        "Tell me about a brave bunny who goes on an adventure", 
        "A story about making new friends at school",
        "An adventure where a shy turtle makes friends while searching for a magical shell"
    ]
    
    print("\nExample requests:")
    for i, ex in enumerate(examples, 1):
        print(f"{i}. {ex}")
    
    # Get request
    user_input = input("\nEnter your story request (or press Enter for example 1): ").strip()
    if not user_input:
        request = examples[0]
        print(f"Using example: {request}")
    else:
        request = user_input
    
    # Select mode
    print("\n" + "-"*60)
    print("Select quality mode:")
    print("1. Fast (5-8 sec, 2 API calls, good quality)")
    print("2. Balanced (12-15 sec, 5-6 API calls, great quality) [DEFAULT]")  
    print("3. Best (20-30 sec, 8-10 API calls, excellent quality)")
    
    mode_input = input("\nEnter mode (1/2/3) or press Enter for Balanced: ").strip()
    mode_map = {"1": "fast", "2": "balanced", "3": "best", "": "balanced"}
    mode = mode_map.get(mode_input, "balanced")
    
    # Generate story
    print(f"\n🎬 Starting generation in {mode.upper()} mode...\n")
    result = generate_bedtime_story(request, mode=mode)
    
    # Display results
    print("\n" + "="*60)
    print("📚 YOUR BEDTIME STORY")
    print("="*60 + "\n")
    print(result["story"])
    print("\n" + "="*60)
    print(f"Mode: {result['mode']}")
    print(f"Category: {result.get('category', 'N/A')}")
    print(f"Quality Score: {result.get('final_score', 'N/A')}")
    print(f"API Calls Used: {result.get('api_calls', 'N/A')}")
    print(f"Refinement Iterations: {result.get('iterations', 'N/A')}")
    
    # Show metadata if available
    metadata = result.get('metadata', {})
    if metadata:
        print("\nAdditional Info:")
        for key, value in metadata.items():
            print(f"  {key}: {value}")
    
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
