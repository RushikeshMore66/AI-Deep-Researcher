import sys
import logging
from core.orchestrator import ResearchOrchestrator
from modules.report_generator import render_markdown

def main():
    # Set logging to a cleaner level for CLI output if desired
    # logging.getLogger().setLevel(logging.WARNING)
    
    query = "NVDA"
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    
    print(f"\n--- Initializing Deep Research: {query} ---\n")
    
    try:
        orchestrator = ResearchOrchestrator(query)
        report = orchestrator.run()
        rendered = render_markdown(report)
        
        # Safe print for Windows terminal encoding
        try:
            print("\n" + rendered)
        except UnicodeEncodeError:
            print("\n" + rendered.encode('ascii', 'replace').decode('ascii'))
            
        print("\n--- Research Pipeline Complete ---")
        
    except Exception as e:
        print(f"\nCritical Pipeline Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
