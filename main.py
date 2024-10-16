import os
import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw
import asyncio
from playwright.async_api import async_playwright
import time

# Define the Website Analyzer Agent


class WebsiteAnalyzerAgent:
    def __init__(self):
        self.role = "Website Analyzer"
        self.goal = "Analyze website structure and content to identify areas for improvement."

    def fetch_website_content(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad responses
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching website content: {e}")
            return None

    def analyze_structure(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        navigation = soup.find('nav')  # Example: find navigation
        headings = soup.find_all(['h1', 'h2', 'h3'])  # Example: find headings
        return {
            "navigation": navigation is not None,
            "headings": len(headings) > 0
        }

    def identify_improvement_areas(self, analysis):
        areas = []
        if not analysis["navigation"]:
            areas.append("Improve navigation structure.")
        if not analysis["headings"]:
            areas.append("Add headings for better content organization.")
        return areas

# Define the Content Improvement Agent
class ContentImprovementAgent:
    def __init__(self):
        self.role = "Content Improvement"
        self.goal = "Suggest improvements for website content clarity and engagement."

    def assess_content_clarity(self, content):
        # Analyze content and provide a dynamic assessment
        if len(content) < 500:
            return "Content is too short; consider adding more information."
        elif "complex" in content:
            return "Content contains complex language; consider simplifying it."
        return "Content is clear but could be more engaging."

    def generate_content_suggestions(self, content):
        suggestions = []
        if len(content) < 500:
            suggestions.append("Add more content to provide value to users.")
        if "complex" in content:
            suggestions.append("Use simpler language.")
        if "<img" not in content:
            suggestions.append("Add more visuals to support the text.")
        return suggestions

    def generate_seo_recommendations(self):
        # Define SEO recommendations
        return [
            "Include relevant keywords in headings.",
            "Optimize meta descriptions for search engines.",
            "Ensure all images have alt text for accessibility.",
            "Use header tags (H1, H2, H3) appropriately for better SEO."
        ]


# Define the Design and UX Agent
class DesignUXAgent:
    def __init__(self):
        self.role = "Design and UX"
        self.goal = "Evaluate visual design and user experience of the website."

    def assess_visual_design(self, html_content):
        # Analyze the design and provide dynamic suggestions
        soup = BeautifulSoup(html_content, 'html.parser')
        suggestions = []

        # Example checks for design issues
        if soup.find('button') is None:
            suggestions.append("Add buttons for better navigation.")
        if "light" in html_content:  # Example condition
            suggestions.append("Consider using a darker color scheme for better contrast.")

        return {
            "color_scheme": suggestions,
            "typography": "Good, but could be improved for readability."
        }

    def generate_ux_improvement_suggestions(self, html_content):
        suggestions = []
        soup = BeautifulSoup(html_content, 'html.parser')
        buttons = soup.find_all('button')

        if len(buttons) < 3:
            suggestions.append("Add more buttons for better navigation.")
        return suggestions

# Define the Visual Representation Agent using Playwright


class VisualRepresentationAgent:
    def __init__(self):
        self.role = "Visual Representation"
        self.goal = "Create visual outputs based on suggestions."

    async def capture_screenshot(self, url):
        async with async_playwright() as p:
            # Launch headless browser
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()  # Open a new page
            await page.goto(url)  # Navigate to the URL

            # Introduce a slight delay before taking the screenshot
            await asyncio.sleep(2)  # Delay for 2 seconds

            screenshot_path = "screenshot.png"
            await page.screenshot(path=screenshot_path)  # Take a screenshot
            await browser.close()  # Close the browser
            print(f"Screenshot saved to {screenshot_path}")
            return screenshot_path

    def annotate_changes(self, screenshot_path, suggestions, url):
        if not os.path.exists(screenshot_path):
            print(f"Screenshot file not found: {screenshot_path}")
            return None

        # Create a unique text file name based on the URL
        domain = url.split("//")[-1].split("/")[0]  # Extract domain from URL
        suggestions_file_path = f"suggestions_{domain}.txt"  # Unique filename

        with open(suggestions_file_path, 'w') as f:
            f.write("Suggestions for Improvement:\n")
            for suggestion in suggestions:
                f.write(f"- {suggestion}\n")

        print(f"Suggestions saved to {suggestions_file_path}")

        return suggestions_file_path


# Define the Reporting Agent
class ReportingAgent:
    def __init__(self):
        self.role = "Reporting"
        self.goal = "Compile and format the report with findings."

    def compile_findings(self, findings):
        return findings

    def format_report(self, findings):
        report_content = "Website Improvement Report\n\n"
        for agent, suggestions in findings.items():
            report_content += f"{agent} Suggestions:\n"
            for suggestion in suggestions:
                report_content += f"- {suggestion}\n"
            report_content += "\n"
        return report_content

# Main execution flow
# Main execution flow
async def main():
    url = input("Enter the website URL: ")

    # Create agents
    analyzer = WebsiteAnalyzerAgent()
    content_improver = ContentImprovementAgent()
    design_ux_agent = DesignUXAgent()
    visual_rep_agent = VisualRepresentationAgent()
    reporter = ReportingAgent()

    # Fetch and analyze website content
    html_content = analyzer.fetch_website_content(url)
    if html_content:
        structure_analysis = analyzer.analyze_structure(html_content)
        improvement_areas = analyzer.identify_improvement_areas(structure_analysis)

        # Assess content clarity and generate suggestions
        content_suggestions = content_improver.generate_content_suggestions(html_content)
        seo_recommendations = content_improver.generate_seo_recommendations()  # Ensure this line is present

        # Assess visual design and generate suggestions
        visual_design = design_ux_agent.assess_visual_design(html_content)
        ux_suggestions = design_ux_agent.generate_ux_improvement_suggestions(html_content)

        # Capture screenshot and annotate changes
        screenshot_path = await visual_rep_agent.capture_screenshot(url)
        if screenshot_path:
            suggestions = improvement_areas + content_suggestions + ux_suggestions
            annotated_image_path = visual_rep_agent.annotate_changes(screenshot_path, suggestions, url)

            # Compile findings
            findings = {
                "Website Analyzer": improvement_areas,
                "Content Improvement": content_suggestions + seo_recommendations,
                "Design and UX": ux_suggestions + [visual_design["color_scheme"], visual_design["typography"]],
            }
            report_content = reporter.format_report(findings)

            print("Website analysis complete.")
            print(f"Annotated image saved as '{screenshot_path}'.")
            print(f"Suggestions saved to '{annotated_image_path}'.")
        else:
            print("Failed to capture screenshot.")
    else:
        print("Failed to fetch website content.")
        
if __name__ == "__main__":
    asyncio.run(main())
