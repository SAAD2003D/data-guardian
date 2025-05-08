from jinja2 import Environment, FileSystemLoader, select_autoescape
import os
from datetime import datetime

class HTMLReporter:
    def __init__(self, dataset_profile):
        self.profile = dataset_profile
        
        # Correct path to the templates directory
        # __file__ is data_guardian/reporting/html_reporter.py
        # os.path.dirname(__file__) is data_guardian/reporting
        # So templates_dir is data_guardian/reporting/templates
        templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
        
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )

    def _group_issues_by_type(self):
        issues_by_type = {}
        if self.profile.issues_found:
            for issue in self.profile.issues_found:
                issues_by_type.setdefault(issue.issue_type, []).append(issue)
        return issues_by_type

    def generate_html(self, template_name="report_template.html"):
        """
        Generates the HTML content as a string.
        """
        if self.profile.raw_data is None:
            return "<p>Error: Dataset not loaded. Cannot generate HTML report.</p>"

        template = self.env.get_template(template_name)
        
        issues_by_type = self._group_issues_by_type()
        
        html_content = template.render(
            profile=self.profile,
            issues_by_type=issues_by_type,
            current_year=datetime.now().year
            # Add other variables for the template here, e.g., visualizations
        )
        return html_content

    def save_html_report(self, output_path="data_quality_report.html", template_name="report_template.html"):
        """
        Generates and saves the HTML report to a file.
        """
        html_output = self.generate_html(template_name)
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_output)
            print(f"HTML report successfully saved to: {output_path}")
            return True
        except IOError as e:
            print(f"Error saving HTML report to {output_path}: {e}")
            return False