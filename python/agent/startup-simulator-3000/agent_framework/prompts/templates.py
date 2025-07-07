from typing import Dict, Any, List
from pathlib import Path
import json
import jinja2

class PromptTemplate:
    """Template for generating prompts with variable substitution"""
    
    def __init__(self, template_path: str):
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(Path(__file__).parent / "templates"),
            trim_blocks=True,
            lstrip_blocks=True
        )
        self.template = self.env.get_template(template_path)
    
    def render(self, **kwargs: Any) -> str:
        """Render the template with given variables"""
        return self.template.render(**kwargs)

class PromptLibrary:
    """Central repository for prompt templates"""
    
    def __init__(self):
        self.templates: Dict[str, PromptTemplate] = {}
        self._load_templates()
    
    def _load_templates(self) -> None:
        """Load all templates from the templates directory"""
        template_dir = Path(__file__).parent / "templates"
        for template_file in template_dir.glob("*.j2"):
            template_name = template_file.stem
            self.templates[template_name] = PromptTemplate(template_file.name)
    
    def get_template(self, name: str) -> PromptTemplate:
        """Get a template by name"""
        if name not in self.templates:
            raise ValueError(f"Template {name} not found")
        return self.templates[name] 