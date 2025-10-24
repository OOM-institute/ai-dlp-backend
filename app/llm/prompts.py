# prompts.py
import json
import uuid

def build_landing_page_prompt(user_input: dict, crawled_context: str = None) -> str:
    """Build the main prompt for landing page generation"""

    unique_page_id = f"landing-{uuid.uuid4().hex[:8]}"
    
    # Base context from user input
    industry = user_input.get('industry', 'general business')
    offer = user_input.get('offer', '')
    target_audience = user_input.get('target_audience', '')
    brand_tone = user_input.get('brand_tone', 'professional')
    
    # Build brand context section
    brand_context_section = ""
    tone_instruction = ""
    
    if crawled_context:
        brand_context_section = f"""
## BRAND CONTEXT (Crawled from Website)
{crawled_context}

"""
        tone_instruction = """
CRITICAL: Use the above brand context as your PRIMARY reference for:
- Tone of voice and writing style
- Language patterns and vocabulary
- Brand personality and messaging approach
- Visual aesthetic (colors, imagery style)
- Value propositions and positioning

The generated landing page should feel like a natural extension of the existing brand website.
Match the sophistication level, formality, and emotional tone you observe in the crawled content.
"""
    else:
        tone_instruction = f"""
Use a {brand_tone} tone throughout all copy.
"""
    
    prompt = f"""You are an expert landing page designer and copywriter. Generate a landing page JSON specification that converts visitors into customers.

## USER REQUIREMENTS
- Industry: {industry}
- Offer/Product: {offer}
- Target Audience: {target_audience}
- Brand Tone: {brand_tone}

{brand_context_section}{tone_instruction}

## CONTENT GUIDELINES

**If brand context is provided above:**
1. **Tone Matching**: Carefully analyze the writing style, vocabulary, and sentence structure in the brand context. Mirror this style precisely.
2. **Voice Consistency**: If the brand is casual and conversational, be casual. If formal and authoritative, match that.
3. **Vocabulary**: Use similar terminology, industry jargon, and word choices as seen in the context.
4. **Messaging Alignment**: Echo the value propositions and benefits mentioned in the brand context.
5. **Visual Alignment**: If the context mentions colors or aesthetic preferences, respect those.

**General Guidelines:**
- Headlines should be compelling and benefit-driven (5-8 words)
- Subheadlines should expand on the value proposition (1-2 sentences)
- Features should focus on benefits, not just features
- Testimonials should feel authentic and specific
- FAQs should address real objections and concerns
- CTAs should be action-oriented and clear

## TECHNICAL REQUIREMENTS

Return ONLY valid JSON. No markdown code blocks (```json), no explanatory text, just raw JSON.

Use this exact structure: 

{{
  "pageId": "{unique_page_id}",
  "version": 1,
  "sections": [
    {{
      "id": "hero-1",
      "type": "hero",
      "order": 0,
      "data": {{
        "headline": "string - powerful main headline (5-8 words, benefit-focused)",
        "subheadline": "string - supporting headline that expands the value prop (1-2 sentences)",
        "ctaText": "string - action button text (3-5 words, e.g., 'Start Free Trial', 'Get Started Now')",
        "backgroundImage": "https://images.unsplash.com/photo-... - relevant unsplash image URL",
        "textColor": "#FFFFFF",
        "backgroundColor": "#1a1a1a"
      }}
    }},
    {{
      "id": "features-1",
      "type": "features",
      "order": 1,
      "data": {{
        "title": "string - section headline",
        "description": "string - optional section description (1-2 sentences)",
        "items": [
          {{
            "id": "f1",
            "title": "string - feature name (2-4 words)",
            "description": "string - benefit-focused description (1 sentence, focus on what the customer gains)",
            "icon": "emoji - single relevant emoji"
          }},
          {{
            "id": "f2",
            "title": "string",
            "description": "string",
            "icon": "emoji"
          }},
          {{
            "id": "f3",
            "title": "string",
            "description": "string",
            "icon": "emoji"
          }}
        ]
      }}
    }},
    {{
      "id": "testimonials-1",
      "type": "testimonials",
      "order": 2,
      "data": {{
        "title": "string - section title (e.g., 'What Our Customers Say', 'Trusted By Thousands')",
        "items": [
          {{
            "id": "t1",
            "quote": "string - authentic testimonial (1-2 sentences, focus on specific results or benefits)",
            "author": "string - realistic first and last name",
            "role": "string - job title",
            "company": "string - company name (can be real or realistic-sounding)",
            "rating": 5
          }},
          {{
            "id": "t2",
            "quote": "string",
            "author": "string",
            "role": "string",
            "company": "string",
            "rating": 5
          }}
        ]
      }}
    }},
    {{
      "id": "faq-1",
      "type": "faq",
      "order": 3,
      "data": {{
        "title": "Frequently Asked Questions",
        "items": [
          {{
            "id": "q1",
            "question": "string - common objection or question (conversational style)",
            "answer": "string - clear, concise answer (1-2 sentences)"
          }},
          {{
            "id": "q2",
            "question": "string",
            "answer": "string"
          }},
          {{
            "id": "q3",
            "question": "string",
            "answer": "string"
          }}
        ]
      }}
    }},
    {{
      "id": "contact-1",
      "type": "contact",
      "order": 4,
      "data": {{
        "title": "string - compelling CTA headline (e.g., 'Ready to Transform Your Business?')",
        "description": "string - supporting text that creates urgency or reinforces value (1-2 sentences)",
        "fields": [
          {{"name": "email", "label": "Email Address", "type": "email", "required": true}},
          {{"name": "company", "label": "Company Name", "type": "text", "required": false}},
          {{"name": "message", "label": "How can we help?", "type": "textarea", "required": true}}
        ],
        "submitText": "string - button text (e.g., 'Get Started', 'Request Demo')",
        "backgroundColor": "#f9fafb"
      }}
    }},
    {{
      "id": "footer-1",
      "type": "footer",
      "order": 5,
      "data": {{
        "links": [
          {{"label": "Privacy Policy", "url": "/privacy"}},
          {{"label": "Terms of Service", "url": "/terms"}},
          {{"label": "Contact", "url": "/contact"}}
        ],
        "socialLinks": [
          {{"platform": "Twitter", "url": "https://twitter.com"}},
          {{"platform": "LinkedIn", "url": "https://linkedin.com"}}
        ],
        "copyright": "© 2025 {offer if offer else 'Company'}. All rights reserved."
      }}
    }}
  ]
}}

Generate the complete landing page JSON now:"""
    
    return prompt


def build_section_regenerate_prompt(section: dict, user_context: dict, crawled_context: str = None) -> str:
    """Build prompt for regenerating a single section with new, unique content"""
    
    section_type = section.get("type")
    current_data = section.get('data', {})
    
    crawl_info = ""
    if crawled_context:
        crawl_info = f"\n\nBRAND CONTEXT FROM WEBSITE:\n{crawled_context}\n"
    
    # Build section-specific regeneration instructions
    section_instructions = {
        "hero": """For HERO section, regenerate with:
- NEW headline (5-8 words, powerful, unique angle)
- NEW subheadline (1-2 sentences, different messaging)
- Same CTA button text OR new CTA if makes sense
- NEW background image URL from Unsplash that fits the new angle
- Keep same text and background colors""",
        
        "features": """For FEATURES section, regenerate with:
- NEW section title and description
- 3 NEW features (different benefits/angles from current)
- Keep emoji icons
- Different wording, same structure
- Focus on different value propositions""",
        
        "testimonials": """For TESTIMONIALS section, regenerate with:
- NEW section title
- 2 NEW testimonials (different quotes, different personas)
- NEW customer names, roles, companies
- Keep 5-star ratings
- Different benefits highlighted vs current version""",
        
        "faq": """For FAQ section, regenerate with:
- NEW section title (if different angle needed)
- 3 NEW FAQ questions and answers
- Different common questions than current
- 1-2 sentence answers
- Address different concerns/use cases""",
        
        "contact": """For CONTACT section, regenerate with:
- NEW CTA headline
- NEW description copy
- Keep same form fields (email, company, message)
- NEW submit button text if appropriate
- Keep background color""",
        
        "footer": """For FOOTER section, regenerate with:
- Same link structure and URLs
- Same social links
- NEW copyright notice or company tagline if applicable"""
    }
    
    instructions = section_instructions.get(section_type, "Regenerate this section with new, unique content while keeping the same structure.")
    
    prompt = f"""You are an expert landing page designer. Regenerate a single landing page section.

ORIGINAL USER CONTEXT:
- Industry: {user_context.get('industry', '')}
- Offer: {user_context.get('offer', '')}
- Target Audience: {user_context.get('target_audience', '')}
- Brand Tone: {user_context.get('brand_tone', '')}{crawl_info}

CURRENT {section_type.upper()} SECTION TO REPLACE:
{str(current_data)}

REGENERATION INSTRUCTIONS:
{instructions}

KEY RULES:
1. Create completely NEW content (different headlines, copy, etc.) - NOT a slight variation
2. Keep the same JSON structure and field names
3. Maintain the brand tone and industry context
4. Keep appealing to the target audience
5. Don't use the exact same words/phrases as the current version
6. All data should be realistic and specific to the industry

Return ONLY valid JSON, no markdown, no code blocks. Ensure valid JSON format:

{{
  "id": "{section.get('id')}",
  "type": "{section_type}",
  "order": {section.get('order', 0)},
  "data": {{
    // Your new content here - match the structure of current data
  }}
}}

Generate completely NEW and UNIQUE content now:"""
    
    return prompt