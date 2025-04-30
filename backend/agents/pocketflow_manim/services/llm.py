from openai import OpenAI
import os
import dotenv
import logging
import yaml
import re

dotenv.load_dotenv()

logger = logging.getLogger("manim_agent")

class LLMParams:
    def __init__(self, prompt: str, model: str = "gemini-2.5-pro-preview-03-25",
                 temperature: float = 0.5,
                 max_tokens: int = 1024):
        self.prompt = prompt
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

class LLM:
    def __init__(self, model: str = "gemini-2.5-pro-preview-03-25"):
        # Configure the OpenAI client to use Google's OpenAI-compatible API
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("GEMINI_API_KEY environment variable is not set")
            api_key = "missing_api_key"
            
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        self.model = model

    def extract_yaml(self, text):
        """Extract YAML content from text, even if it's not properly formatted."""
        # First, try to find content between ```yaml and ``` markers
        yaml_pattern = r"```yaml\s*([\s\S]*?)\s*```"
        match = re.search(yaml_pattern, text)
        
        if match:
            yaml_content = match.group(1)
            try:
                return yaml.safe_load(yaml_content)
            except Exception as e:
                logger.error(f"Error parsing YAML: {str(e)}")
        
        # If we can't find or parse YAML properly, attempt to construct a basic structure
        # This is a fallback to prevent complete failures
        try:
            # Look for key patterns like "thinking:" or "code:"
            thinking_match = re.search(r"thinking:(?:\s*\|)?\s*([\s\S]*?)(?:\n\w+:|$)", text)
            code_match = re.search(r"code:(?:\s*\|)?\s*([\s\S]*?)(?:\n\w+:|$)", text)
            scenes_match = re.search(r"scenes:([\s\S]*?)(?:\n\w+:|$)", text)
            
            result = {}
            
            if thinking_match:
                result["thinking"] = thinking_match.group(1).strip()
            if code_match:
                result["code"] = code_match.group(1).strip()
            if scenes_match:
                # Simple parsing of scene items
                scene_text = scenes_match.group(1)
                scenes = []
                scene_items = re.findall(r"-\s*name:\s*(.*?)(?:\n\s*description:\s*(.*?))?(?:\n\s*-|\n\w+:|$)", scene_text, re.DOTALL)
                for name, desc in scene_items:
                    scenes.append({"name": name.strip(), "description": desc.strip()})
                result["scenes"] = scenes
            
            # If we found any content, return it
            if result:
                return result
        except Exception as e:
            logger.error(f"Error extracting YAML-like content: {str(e)}")
        
        # Last resort fallback
        return {
            "thinking": "Error processing response from LLM",
            "scenes": [{"name": "Error Scene", "description": "Default scene due to LLM response error"}],
            "next_step": "create_code"
        }

    def call(self, params: LLMParams) -> str:
        """Call the LLM with the given prompt."""
        try:
            # Modify the original prompt to specifically request YAML formatting
            system_message = "You MUST respond using the exact YAML format specified in the user's prompt. Never include any text outside the YAML structure. Start your response with ```yaml and end with ```."
            
            # Extract any existing YAML request from the prompt
            yaml_format_match = re.search(r"```yaml\s*([\s\S]*?)\s*```", params.prompt)
            if yaml_format_match:
                # Add a clear instruction about YAML format
                yaml_example = yaml_format_match.group(0)
                system_message = f"You MUST respond using the exact YAML format shown below. Your entire response should be valid YAML, starting with ```yaml and ending with ```.\n\nExample format: {yaml_example}"
            
            # Format the prompt as a user message
            response = self.client.chat.completions.create(
                model=params.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": params.prompt}
                ],
                temperature=params.temperature,
                max_tokens=params.max_tokens
            )
            
            # Extract the response text
            response_text = response.choices[0].message.content
            
            # Try to parse YAML from the response
            try:
                # If the response is already wrapped in ```yaml ... ```, extract it
                if "```yaml" in response_text and "```" in response_text.split("```yaml", 1)[1]:
                    yaml_str = response_text.split("```yaml", 1)[1].split("```", 1)[0].strip()
                    parsed_yaml = yaml.safe_load(yaml_str)
                    return f"```yaml\n{yaml_str}\n```"
                
                # If it's valid YAML but not wrapped, wrap it
                try:
                    parsed_yaml = yaml.safe_load(response_text)
                    if isinstance(parsed_yaml, dict):
                        return f"```yaml\n{response_text}\n```"
                except:
                    pass
                
                # If we get here, the response isn't properly formatted YAML
                logger.warning("Response wasn't properly formatted YAML. Attempting to extract YAML content...")
                parsed_yaml = self.extract_yaml(response_text)
                yaml_str = yaml.dump(parsed_yaml, default_flow_style=False)
                return f"```yaml\n{yaml_str}\n```"
                
            except Exception as yaml_err:
                logger.error(f"YAML parsing error: {str(yaml_err)}")
                
                # Create a fallback YAML response
                fallback_yaml = self.extract_yaml(response_text)
                yaml_str = yaml.dump(fallback_yaml, default_flow_style=False)
                return f"```yaml\n{yaml_str}\n```"
                
        except Exception as e:
            logger.error(f"Error calling LLM: {str(e)}")
            # Provide a fallback response to allow the agent to continue
            return f"""```yaml
thinking: |
    Error connecting to LLM: {str(e)}
    Providing a minimal fallback response to continue the process.
scenes:
    - name: Error Scene
      description: Default scene due to LLM connection error
next_step: "create_code"
```"""