from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
from .models import Consolidated

def render_report_html(consolidated: Consolidated, output_path: str) -> str:
    templates_dir = Path(__file__).parent / "templates"
    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=select_autoescape()
    )
    tmpl = env.get_template("report.html")
    html = tmpl.render(c=consolidated)
    Path(output_path).write_text(html, encoding="utf-8")
    return output_path
