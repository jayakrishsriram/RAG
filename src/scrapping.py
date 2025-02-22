from crewai import Agent, Task, Crew, LLM
from crewai_tools import ScrapeWebsiteTool
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

def save_to_file(content, filename=None):
    """
    Save the scraping results to a text file with timestamp
    
    Args:
        content (str): The content to save
        filename (str, optional): Custom filename. If None, generates timestamp-based name
    """
    try:
        # Generate default filename with timestamp if none provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"scraping_results_{timestamp}.txt"
        
        # Ensure the filename ends with .txt
        if not filename.endswith('.txt'):
            filename += '.txt'
            
        # Write content to file
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(str(content))
        print(f"Results successfully saved to {filename}")
        
    except Exception as e:
        print(f"Error saving results to file: {str(e)}")

def main():
    try:
        # Initialize Large Language Model (LLM)
        llm = LLM(model="groq/llama-3.3-70b-versatile",
                  api_key=os.getenv('GROQ_API_KEY'))

        # Create CrewAI agents
        scrapper = Agent(
            role='Documentation Scrapper',
            goal='Scrapping of technical documentation',
            backstory='Technical scrapper who excels at scrapping complex websites',
            llm=llm,
            verbose=True
        )

        # Initialize the ScrapeWebsiteTool
        scrape_tool = ScrapeWebsiteTool(website_url='https://python.langchain.com/docs/introduction/')

        # Create task
        scrapping_task = Task(
            description='Scrape the content from the specified website.',
            expected_output="A clear, concise data related to scraped content",
            agent=scrapper,
            tools=[scrape_tool]
        )

        # Create crew
        crew = Crew(
            agents=[scrapper],
            tasks=[scrapping_task],
            verbose=True
        )

        # Execute the crew
        result = crew.kickoff()
        
        # Save results to file
        save_to_file(result)
        
        return result

    except Exception as e:
        error_message = f"An error occurred during execution: {str(e)}"
        print(error_message)
        save_to_file(error_message, "error_log.txt")
        return None

if __name__ == "__main__":
    main()