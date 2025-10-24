# generator.py
import os
import json
from openai import OpenAI
from .prompts import build_landing_page_prompt, build_section_regenerate_prompt
from app.crawler import WebCrawler
import logging

logger = logging.getLogger(__name__)

# Initialize OpenAI client
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

client = OpenAI(api_key=OPENAI_API_KEY)

crawler = WebCrawler()

def generate_page_spec(user_input: dict, crawled_context: str = None) -> dict:
    """
    Generate a complete landing page spec using OpenAI
    
    Args:
        user_input: dict with industry, offer, target_audience, brand_tone, and optional url
    
    Returns:
        dict: page specification JSON
    """
    try:
        # Extract URL if provided
        website_url = user_input.get("url")
        crawled_context = None
        
        print(f"\n[GENERATOR] user_input keys: {user_input.keys()}", flush=True)
        print(f"[GENERATOR] website_url: {website_url}", flush=True)
        
        # Crawl website if URL provided
        if website_url:
            print(f"[GENERATOR] Starting crawl of: {website_url}", flush=True)
            logger.info(f"Crawling website: {website_url}")
            crawled_context = crawler.crawl_website(website_url)
            print(f"[GENERATOR] Crawl result: {crawled_context is not None}", flush=True)
            if crawled_context:
                print(f"[GENERATOR] Crawled context length: {len(crawled_context)}", flush=True)
                logger.info("✓ Website crawled successfully")
            else:
                print(f"[GENERATOR] Crawl returned None", flush=True)
                logger.warning("Website crawl failed, proceeding without brand context")
        else:
            print(f"[GENERATOR] No URL provided", flush=True)
            logger.info("No URL provided, generating without brand context")
        
        # Log whether context was provided
        logger.info(f"Generating page spec with crawled context: {crawled_context is not None}")
        if crawled_context:
            logger.info(f"Crawled context length: {len(crawled_context)} characters")
            logger.debug(f"First 500 chars of context: {crawled_context[:500]}")
        
        prompt = build_landing_page_prompt(user_input, crawled_context)
        
        # Log the actual prompt being sent
        logger.debug(f"Full prompt length: {len(prompt)} characters")
        logger.debug(f"Prompt contains 'BRAND CONTEXT': {'BRAND CONTEXT' in prompt}")
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert landing page designer and conversion copywriter. "
                        "You create compelling marketing copy that drives action, matches brand voice, "
                        "and resonates with target audiences. You have deep knowledge of persuasive writing, "
                        "user psychology, and marketing best practices. "
                        "You always return your work as valid JSON with no markdown formatting."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=2500
        )
        
        # Extract response text
        response_text = response.choices[0].message.content
        
        # Parse JSON
        page_spec = json.loads(response_text)
        return page_spec
            
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse LLM response as JSON: {e}")
    except Exception as e:
        raise Exception(f"Error generating page spec: {str(e)}")


def regenerate_section(section: dict, prompt: str) -> dict:
    """
    Regenerate a single section with new prompt
    
    Args:
        section: the section object to regenerate
        prompt: the full prompt to send to LLM
    
    Returns:
        dict: updated section
    """
    try:
        # Extract and crawl URL if provided
        website_url = prompt.get("url")
        crawled_context = None
        
        if website_url:
            logger.info(f"Crawling website for section regeneration: {website_url}")
            crawled_context = crawler.crawl_website(website_url)
        
        prompt = build_section_regenerate_prompt(section, prompt, crawled_context)
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert landing page designer and conversion copywriter. "
                        "You create compelling marketing copy that drives action, matches brand voice, "
                        "and resonates with target audiences. You have deep knowledge of persuasive writing, "
                        "user psychology, and marketing best practices. "
                        "You always return your work as valid JSON with no markdown formatting."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        # Extract response text
        response_text = response.choices[0].message.content
        
        # Parse JSON
        updated_section = json.loads(response_text)
        return updated_section
            
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse LLM response as JSON: {e}")
    except Exception as e:
        raise Exception(f"Error regenerating section: {str(e)}")