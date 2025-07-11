import html2text
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

BASE_DIR = Path(__file__).resolve().parent.parent
templates_dir = BASE_DIR / "templates/files"
jinja_env = Environment(
    loader=FileSystemLoader(str(templates_dir)),
    autoescape=select_autoescape(["html", "xml"]),
)


class Templater:
    @staticmethod
    def render_template(template_name: str, context: dict) -> tuple[str, str]:
        template = jinja_env.get_template(template_name)
        html_content = template.render(context)
        plain_content = html2text.html2text(html_content)
        return html_content, plain_content
