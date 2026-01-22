"""
AI-powered content extraction from scraped HTML
Extracts key information, summary, and entities
"""
import json
from typing import Dict, List
from backend.ai.ai_provider import ai_provider

class ContentExtractor:
    """Extract structured content from raw HTML/text using AI"""
    
    def extract_content(self, text: str, url: str, title: str = None) -> Dict:
        """
        Extract structured content from scraped text
        Returns: {
            'summary': str,
            'key_points': List[str],
            'entities': Dict,
            'metadata': Dict
        }
        """
        
        # Truncate text if too long (to save tokens)
        max_length = 15000
        if len(text) > max_length:
            text = text[:max_length] + "\n\n[Content truncated...]"
        
        # Create extraction prompt
        system_prompt = """You are an expert content analyzer. Extract structured information from web content.
Your task is to analyze the provided text and extract:
1. A concise summary (2-3 sentences)
2. Key points (5-10 bullet points)
3. Important entities (people, organizations, locations, dates)
4. Main topics/categories

Return ONLY valid JSON in this exact format:
{
  "summary": "Brief 2-3 sentence summary",
  "key_points": ["Point 1", "Point 2", ...],
  "entities": {
    "people": ["Name 1", "Name 2"],
    "organizations": ["Org 1", "Org 2"],
    "locations": ["Location 1"],
    "dates": ["Date 1"]
  },
  "topics": ["Topic 1", "Topic 2"]
}"""
        
        user_prompt = f"""URL: {url}
Title: {title or 'N/A'}

Content:
{text}

Extract the structured information as JSON."""
        
        try:
            # Get AI response
            response = ai_provider.generate_completion(
                prompt=user_prompt,
                system_prompt=system_prompt,
                max_tokens=2000,
                temperature=0.3
            )
            
            # Parse JSON response
            # Try to extract JSON from response (in case there's extra text)
            response = response.strip()
            
            # Find JSON object
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                extracted_data = json.loads(json_str)
            else:
                # Fallback: try parsing entire response
                extracted_data = json.loads(response)
            
            # Validate structure
            result = {
                'summary': extracted_data.get('summary', 'No summary available'),
                'key_points': extracted_data.get('key_points', []),
                'entities': extracted_data.get('entities', {}),
                'topics': extracted_data.get('topics', []),
                'metadata': {
                    'url': url,
                    'title': title,
                    'ai_provider': ai_provider.get_active_provider()
                }
            }
            
            return result
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            print(f"Response: {response[:500]}")
            
            # Fallback: return basic structure
            return {
                'summary': 'Content extraction failed - unable to parse AI response',
                'key_points': [],
                'entities': {},
                'topics': [],
                'metadata': {
                    'url': url,
                    'title': title,
                    'error': str(e)
                }
            }
        except Exception as e:
            print(f"❌ Content extraction error: {e}")
            return {
                'summary': f'Content extraction failed: {str(e)}',
                'key_points': [],
                'entities': {},
                'topics': [],
                'metadata': {
                    'url': url,
                    'title': title,
                    'error': str(e)
                }
            }
    
    def generate_detailed_summary(self, text: str, max_length: int = 500) -> str:
        """Generate a more detailed summary"""
        
        # Truncate text if too long
        if len(text) > 15000:
            text = text[:15000] + "\n\n[Content truncated...]"
        
        prompt = f"""Provide a comprehensive summary of the following content in about {max_length} characters.
Focus on the main ideas, key information, and important details.

Content:
{text}

Summary:"""
        
        try:
            summary = ai_provider.generate_completion(
                prompt=prompt,
                max_tokens=max_length // 2,
                temperature=0.3
            )
            return summary.strip()
        except Exception as e:
            return f"Summary generation failed: {str(e)}"

# Global instance
content_extractor = ContentExtractor()
