"""
Form analyzer and filler using Playwright
Detects forms and attempts to fill them
"""
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from typing import Dict, List, Optional
import json

class FormAnalyzer:
    """Analyze and fill web forms"""
    
    def detect_forms(self, url: str, timeout: int = 30) -> Dict:
        """
        Detect all forms on a page
        Returns form structure with fields
        """
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                # Navigate to page
                page.goto(url, timeout=timeout * 1000, wait_until='networkidle')
                
                # Execute JavaScript to find all forms
                forms_data = page.evaluate("""
                    () => {
                        const forms = Array.from(document.querySelectorAll('form'));
                        return forms.map((form, formIndex) => {
                            const fields = [];
                            
                            // Get all input fields
                            form.querySelectorAll('input, textarea, select').forEach((field, fieldIndex) => {
                                const fieldData = {
                                    type: field.type || field.tagName.toLowerCase(),
                                    name: field.name || field.id || `field_${fieldIndex}`,
                                    id: field.id || '',
                                    placeholder: field.placeholder || '',
                                    required: field.required || false,
                                    value: field.value || ''
                                };
                                
                                // For select fields, get options
                                if (field.tagName.toLowerCase() === 'select') {
                                    fieldData.options = Array.from(field.options).map(opt => ({
                                        value: opt.value,
                                        text: opt.text
                                    }));
                                }
                                
                                fields.push(fieldData);
                            });
                            
                            return {
                                formIndex: formIndex,
                                action: form.action || '',
                                method: form.method || 'get',
                                fields: fields
                            };
                        });
                    }
                """)
                
                browser.close()
                
                return {
                    'success': True,
                    'forms': forms_data,
                    'total_forms': len(forms_data)
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"Form detection failed: {str(e)}",
                'forms': []
            }
    
    def fill_form(
        self, 
        url: str, 
        form_data: Dict[str, str],
        form_index: int = 0,
        submit: bool = False,
        timeout: int = 30
    ) -> Dict:
        """
        Fill a form with provided data
        
        Args:
            url: URL of the page with the form
            form_data: Dict mapping field names to values
            form_index: Index of the form to fill (if multiple forms)
            submit: Whether to submit the form
            timeout: Timeout in seconds
        
        Returns:
            Dict with success status and details
        """
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context()
                page = context.new_page()
                
                # Navigate to page
                page.goto(url, timeout=timeout * 1000, wait_until='networkidle')
                
                # Take screenshot before filling
                screenshot_before = page.screenshot()
                
                # Fill form fields
                filled_fields = []
                errors = []
                
                for field_name, field_value in form_data.items():
                    try:
                        # Try different selectors
                        selectors = [
                            f'input[name="{field_name}"]',
                            f'textarea[name="{field_name}"]',
                            f'select[name="{field_name}"]',
                            f'#{field_name}',
                            f'input[placeholder*="{field_name}" i]'
                        ]
                        
                        field_filled = False
                        for selector in selectors:
                            try:
                                if page.locator(selector).count() > 0:
                                    element = page.locator(selector).first
                                    
                                    # Check field type
                                    tag_name = element.evaluate('el => el.tagName.toLowerCase()')
                                    
                                    if tag_name == 'select':
                                        element.select_option(field_value)
                                    else:
                                        element.fill(field_value)
                                    
                                    filled_fields.append(field_name)
                                    field_filled = True
                                    break
                            except:
                                continue
                        
                        if not field_filled:
                            errors.append(f"Field '{field_name}' not found")
                    
                    except Exception as e:
                        errors.append(f"Error filling '{field_name}': {str(e)}")
                
                # Take screenshot after filling
                screenshot_after = page.screenshot()
                
                # Submit if requested
                submit_result = None
                if submit:
                    try:
                        # Try to find and click submit button
                        submit_selectors = [
                            'button[type="submit"]',
                            'input[type="submit"]',
                            'button:has-text("Submit")',
                            'button:has-text("Send")',
                            'button:has-text("Continue")'
                        ]
                        
                        for selector in submit_selectors:
                            if page.locator(selector).count() > 0:
                                page.locator(selector).first.click()
                                page.wait_for_load_state('networkidle', timeout=10000)
                                submit_result = "Form submitted successfully"
                                break
                        
                        if not submit_result:
                            submit_result = "Submit button not found"
                    
                    except Exception as e:
                        submit_result = f"Submit failed: {str(e)}"
                
                browser.close()
                
                return {
                    'success': True,
                    'filled_fields': filled_fields,
                    'errors': errors,
                    'submit_result': submit_result,
                    'message': f"Filled {len(filled_fields)} fields successfully"
                }
                
        except PlaywrightTimeout:
            return {
                'success': False,
                'error': f"Page load timeout after {timeout} seconds",
                'reason': "The page took too long to load"
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Form filling failed: {str(e)}",
                'reason': self._analyze_error(str(e))
            }
    
    def _analyze_error(self, error: str) -> str:
        """Analyze error and provide helpful reason"""
        error_lower = error.lower()
        
        if 'captcha' in error_lower:
            return "CAPTCHA protection detected - cannot fill automatically"
        elif 'timeout' in error_lower:
            return "Page loading timeout - website may be slow or unavailable"
        elif 'navigation' in error_lower:
            return "Navigation error - page may require authentication"
        elif 'selector' in error_lower or 'element' in error_lower:
            return "Form elements not found - page structure may be complex"
        else:
            return "Unknown error - form may have special protection or validation"

# Global instance
form_analyzer = FormAnalyzer()
