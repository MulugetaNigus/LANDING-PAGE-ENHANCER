from crewai import Agent, Task, Crew
from langchain.tools import Tool
from langchain_community.utilities import GoogleSearchAPIWrapper
from bs4 import BeautifulSoup
import requests
import asyncio
import os
from playwright.async_api import async_playwright
import time

# Set environment variables
os.environ["OPENAI_API_BASE"] = "https://api.groq.com/openai/v1"
os.environ["OPENAI_MODEL_NAME"] = "llama3-70b-8192"
# os.environ["OPENAI_MODEL_NAME"] = "llama-3.1-70b-versatile"
os.environ["OPENAI_API_KEY"] = "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"
os.environ["SERPER_API_KEY"] = "f671ff767248922b587a1ee4526255909c29207f"

# Tool for web scraping


def scrape_website(url):
    response = requests.get(url)
    return BeautifulSoup(response.content, 'html.parser').get_text()

# Tool for capturing screenshot
async def capture_screenshot(url, delay=5, full_page=True, max_pages=1):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        await asyncio.sleep(delay)

        screenshots = []
        for i in range(max_pages):
            if i > 0:
                # Try to find and click a "next page" link
                next_page = await page.query_selector("a:has-text('Next')")
                if next_page:
                    await next_page.click()
                    await page.wait_for_load_state('networkidle')
                else:
                    break  # No more pages to capture

            screenshot_path = f"screenshot_page_{i+1}.png"
            if full_page:
                await page.screenshot(path=screenshot_path, full_page=True)
            else:
                await page.screenshot(path=screenshot_path)
            screenshots.append(screenshot_path)

        await browser.close()
        return screenshots

# Define Agents
website_analyzer = Agent(
    role='Website Analyzer',
    goal='Analyze website structure and content to identify areas for improvement',
    backstory='You are an expert in web design and user experience, with years of experience in analyzing websites.',
    verbose=True,
    allow_delegation=False
)

content_improver = Agent(
    role='Content Improvement Specialist',
    goal='Suggest improvements for website content clarity and engagement',
    backstory='You are a skilled content strategist with a keen eye for engaging and effective web content.',
    verbose=True,
    allow_delegation=False
)

design_ux_expert = Agent(
    role='Design and UX Expert',
    goal='Evaluate visual design and user experience of the website',
    backstory='You are a seasoned designer with expertise in creating intuitive and visually appealing web interfaces.',
    verbose=True,
    allow_delegation=False
)

# Define Tasks
analyze_website_task = Task(
    description='Analyze the website structure and content. Identify areas for improvement.',
    agent=website_analyzer,
    expected_output="A detailed analysis of the website structure and content, with specific areas identified for improvement."
)

improve_content_task = Task(
    description='Review the website content and suggest improvements for clarity and engagement.',
    agent=content_improver,
    expected_output="A list of specific suggestions to improve the website's content for better clarity and engagement."
)

evaluate_design_task = Task(
    description='Assess the visual design and user experience of the website. Provide suggestions for improvement.',
    agent=design_ux_expert,
    expected_output="An evaluation of the website's visual design and user experience, with concrete suggestions for improvement."
)

# Create Crew
website_enhancement_crew = Crew(
    agents=[website_analyzer, content_improver, design_ux_expert],
    tasks=[analyze_website_task, improve_content_task, evaluate_design_task],
    verbose=True
)

# Main execution
async def main():
    url = input("Enter the website URL: ")

    # Scrape website content
    content = scrape_website(url)

    # Capture screenshots
    screenshots = await capture_screenshot(url, delay=5, full_page=True, max_pages=3)

    # Execute crew tasks
    result = website_enhancement_crew.kickoff()

    # Save results to a file
    with open('website_analysis_report.txt', 'w') as f:
        f.write(f"Website Analysis Report for {url}\n\n")
        f.write(str(result))
        f.write("\n\nScreenshots saved as:\n")
        for screenshot in screenshots:
            f.write(f"- {screenshot}\n")

    print("Analysis complete. Results saved in 'website_analysis_report.txt'")
    print("Screenshots saved:")
    for screenshot in screenshots:
        print(f"- {screenshot}")

    print("Analysis complete. Results saved in 'website_analysis_report.txt'")

if __name__ == "__main__":
    asyncio.run(main())


# from crewai import Agent, Task, Crew
# from bs4 import BeautifulSoup
# import requests
# import asyncio
# from playwright.async_api import async_playwright
# from PIL import Image, ImageDraw, ImageFont
# import textwrap
# import time
# import os

# # Set environment variables
# os.environ["OPENAI_API_BASE"] = "https://api.groq.com/openai/v1"
# os.environ["OPENAI_MODEL_NAME"] = "llama3-70b-8192"
# # os.environ["OPENAI_MODEL_NAME"] = "llama-3.1-70b-versatile"
# os.environ["OPENAI_API_KEY"] = "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"
# os.environ["SERPER_API_KEY"] = "f671ff767248922b587a1ee4526255909c29207f"

# # Tool for web scraping


# def scrape_website(url):
#     response = requests.get(url)
#     return BeautifulSoup(response.content, 'html.parser').get_text()


# async def capture_screenshot(url, delay=5):
#     async with async_playwright() as p:
#         browser = await p.chromium.launch()
#         page = await browser.new_page()
#         await page.goto(url)
#         await asyncio.sleep(delay)
#         screenshot_path = "original_screenshot.png"
#         await page.screenshot(path=screenshot_path)
#         await browser.close()
#         return screenshot_path


# def apply_enhancements(original_path, suggestions):
#     # Open the original screenshot
#     img = Image.open(original_path)
#     draw = ImageDraw.Draw(img)

#     # Try to use a default font, or use a fallback method if font loading fails
#     try:
#         # Try to use a system font
#         font = ImageFont.load_default()
#     except IOError:
#         print("Default font not found. Using simple text drawing.")
#         font = None

#     # Apply some basic enhancements based on suggestions
#     y_position = 10
#     for suggestion in suggestions:
#         if "bold" in suggestion.lower():
#             # Simulate bold text by drawing a rectangle
#             draw.rectangle([10, y_position, 200, y_position + 30], fill="yellow")
#         elif "color" in suggestion.lower():
#             # Add a color swatch
#             draw.rectangle([10, y_position, 50, y_position + 30], fill="red")

#         # Write the suggestion text
#         wrapped_text = textwrap.wrap(suggestion, width=40)
#         for line in wrapped_text:
#             if font:
#                 draw.text((10, y_position), line, font=font, fill="black")
#             else:
#                 draw.text((10, y_position), line, fill="black")
#             y_position += 30

#     enhanced_path = "enhanced_screenshot.png"
#     img.save(enhanced_path)
#     return enhanced_path


# # # Define Agents
# website_analyzer = Agent(
#     role='Website Analyzer',
#     goal='Analyze website structure and content to identify areas for improvement',
#     backstory='You are an expert in web design and user experience, with years of experience in analyzing websites.',
#     verbose=True,
#     allow_delegation=False
# )

# content_improver = Agent(
#     role='Content Improvement Specialist',
#     goal='Suggest improvements for website content clarity and engagement',
#     backstory='You are a skilled content strategist with a keen eye for engaging and effective web content.',
#     verbose=True,
#     allow_delegation=False
# )

# design_ux_expert = Agent(
#     role='Design and UX Expert',
#     goal='Evaluate visual design and user experience of the website',
#     backstory='You are a seasoned designer with expertise in creating intuitive and visually appealing web interfaces.',
#     verbose=True,
#     allow_delegation=False
# )

# # Define Tasks
# analyze_website_task = Task(
#     description='Analyze the website structure and content. Identify areas for improvement.',
#     agent=website_analyzer,
#     expected_output="A detailed analysis of the website structure and content, with specific areas identified for improvement."
# )

# improve_content_task = Task(
#     description='Review the website content and suggest improvements for clarity and engagement.',
#     agent=content_improver,
#     expected_output="A list of specific suggestions to improve the website's content for better clarity and engagement."
# )

# evaluate_design_task = Task(
#     description='Assess the visual design and user experience of the website. Provide suggestions for improvement.',
#     agent=design_ux_expert,
#     expected_output="An evaluation of the website's visual design and user experience, with concrete suggestions for improvement."
# )

# # Create Crew
# website_enhancement_crew = Crew(
#     agents=[website_analyzer, content_improver, design_ux_expert],
#     tasks=[analyze_website_task, improve_content_task, evaluate_design_task],
#     verbose=True
# )


# # Main execution
# async def main():
#     url = input("Enter the website URL: ")

#     # Scrape website content
#     content = scrape_website(url)

#     # Capture original screenshot
#     original_screenshot_path = await capture_screenshot(url, delay=5)

#     # Execute crew tasks
#     crew_output = website_enhancement_crew.kickoff()

#     # Extract suggestions from the crew output
#     suggestions = []
#     full_report = f"Website Analysis Report for {url}\n\n"

#     # Print the crew output to inspect its structure
#     print(f"Crew Output: {crew_output}")

#     # Check if crew_output is a string or has a specific structure
#     if isinstance(crew_output, str):
#         full_report += crew_output
#         suggestions = crew_output.split('\n')
#     else:
#         # Assuming crew_output is iterable
#         for task_output in crew_output:
#             print(f"Task Output: {task_output}")

#             # Extract task result as a string
#             task_result = str(task_output)

#             suggestions.extend(task_result.split('\n'))
#             full_report += f"Task Result: {task_result}\n\n"

#     # Apply enhancements to the screenshot
#     enhanced_screenshot_path = apply_enhancements(
#         original_screenshot_path, suggestions)

#     # Save results to a file
#     with open('website_analysis_report.txt', 'w') as f:
#         f.write(full_report)
#         f.write(f"\nOriginal screenshot saved as: {original_screenshot_path}")
#         f.write(f"\nEnhanced screenshot saved as: {enhanced_screenshot_path}")

#     print("Analysis complete. Results saved in 'website_analysis_report.txt'")
#     print(f"Original screenshot: {original_screenshot_path}")
#     print(f"Enhanced screenshot: {enhanced_screenshot_path}")

# if __name__ == "__main__":
#     asyncio.run(main())
