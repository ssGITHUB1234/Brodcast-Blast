from openai import OpenAI
from config.settings import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

def generate_broadcast_template(topic=None, tone='professional', target_audience=None):
    """Generate broadcast template using AI"""
    if not client:
        return None
    
    try:
        prompt = f"Generate a compelling broadcast message template"
        if topic:
            prompt += f" about {topic}"
        if target_audience:
            prompt += f" for {target_audience} audience"
        prompt += f". Tone should be {tone}. Keep it under 200 words and engaging."
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a creative copywriter specializing in broadcast messages and marketing content."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"AI service error: {e}")
        return None

def optimize_broadcast_message(message):
    """Optimize a broadcast message for better engagement"""
    if not client:
        return None
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert at optimizing marketing messages for engagement."},
                {"role": "user", "content": f"Optimize this broadcast message for better engagement while keeping the core message: {message}"}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"AI optimization error: {e}")
        return None
