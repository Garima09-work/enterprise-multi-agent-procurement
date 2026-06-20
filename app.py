import os
import sys
import asyncio
from google.adk import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types

# Simple ANSI colors for premium terminal styling
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

async def main():
    # Print beautiful header
    print(f"{Colors.HEADER}{Colors.BOLD}======================================================={Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}  Google ADK Multi-Agent System: IT & Finance Audit     {Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}======================================================={Colors.ENDC}")
    
    # Check for API Key
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print(f"{Colors.WARNING}Warning: GOOGLE_API_KEY environment variable is not set.{Colors.ENDC}")
        print("Please set it in your environment. Example:")
        print("PowerShell: $env:GOOGLE_API_KEY=\"your_api_key\"")
        print("CMD:        set GOOGLE_API_KEY=your_api_key")
        print("Bash:       export GOOGLE_API_KEY=\"your_api_key\"\n")
    
    print(f"{Colors.BLUE}[*] Initializing agents...{Colors.ENDC}")
    
    # 1. Define the secondary agent: Financial Auditor
    financial_auditor = Agent(
        name="Financial_Auditor",
        model="gemini-2.5-flash",
        instruction=(
            "You are a Financial Auditor. Your job is to calculate and analyze the budget impacts of requested hardware/software. "
            "Specifically:\n"
            "1. Calculate the total cost (one-time and recurring costs) based on standard pricing if not specified.\n"
            "2. Evaluate the budget impact and determine if it represents a high, medium, or low financial impact.\n"
            "3. Assess if the request fits logical budgetary constraints and flag any excessive expenses.\n"
            "Keep your response structured, professional, and quantitative."
        )
    )
    
    # 2. Define the primary agent: IT Procurement Analyst
    it_procurement_analyst = Agent(
        name="IT_Procurement_Analyst",
        model="gemini-2.5-flash",
        instruction=(
            "You are an IT Procurement Analyst. Your job is to check software/hardware tech requests. "
            "Specifically:\n"
            "1. Check if the request is technically logical and matches standard business needs.\n"
            "2. Identify the hardware or software requested, validation requirements, and standard IT options.\n"
            "3. Delegate the request to the Financial_Auditor to calculate the budget impact, estimate costs, and analyze financial feasibility.\n"
            "4. Combine the technical recommendation with the Financial Auditor's budget assessment into a final procurement report.\n"
            "Make sure to explicitly transfer/delegate to the Financial_Auditor to get the budget analysis."
        ),
        sub_agents=[financial_auditor]
    )
    
    # 3. Setup the InMemoryRunner
    print(f"{Colors.BLUE}[*] Setting up InMemoryRunner...{Colors.ENDC}")
    runner = InMemoryRunner(agent=it_procurement_analyst, app_name="it_procurement_app")
    runner.auto_create_session = True
    
    print(f"{Colors.GREEN}[+] System ready!{Colors.ENDC}")
    print(f"Type your tech procurement request below. Type {Colors.BOLD}exit{Colors.ENDC} or {Colors.BOLD}quit{Colors.ENDC} to exit.\n")
    
    user_id = "user_1"
    session_id = "session_1"
    
    while True:
        try:
            user_input = input(f"{Colors.CYAN}{Colors.BOLD}Request > {Colors.ENDC}").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n{Colors.BLUE}[*] Exiting system. Goodbye!{Colors.ENDC}")
            break
            
        if not user_input:
            continue
            
        if user_input.lower() in ("exit", "quit"):
            print(f"{Colors.BLUE}[*] Exiting system. Goodbye!{Colors.ENDC}")
            break
            
        # Wrap message in Google GenAI Content type to prevent Pydantic validation errors
        new_message = types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_input)]
        )
        
        print(f"\n{Colors.BLUE}[*] Processing request...{Colors.ENDC}")
        
        current_author = None
        try:
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=new_message
            ):
                # Print agent transitions
                if event.author and event.author != current_author:
                    current_author = event.author
                    author_color = Colors.GREEN if current_author == "IT_Procurement_Analyst" else Colors.WARNING
                    print(f"\n{author_color}{Colors.BOLD}[{current_author}]{Colors.ENDC} ", end="", flush=True)
                
                # Stream the content parts
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if getattr(part, "text", None):
                            print(part.text, end="", flush=True)
            print("\n")
        except Exception as e:
            print(f"\n{Colors.FAIL}{Colors.BOLD}[Error]{Colors.ENDC} An error occurred: {e}\n")

if __name__ == "__main__":
    # Ensure event loop policy supports subprocess/asyncio on Windows
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
