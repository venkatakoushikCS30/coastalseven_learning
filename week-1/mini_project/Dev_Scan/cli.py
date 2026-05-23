# cli.py
import argparse
import logging
import sys
from pathlib import Path

def setup_logging(verbose: bool) -> None:
    """Configures logging based on user verbosity preference (SRS FR-36 to FR-39)"""
    level = logging.DEBUG if verbose else logging.WARNING
    handlers = [logging.StreamHandler(sys.stdout)]
    
    if verbose:
        handlers.append(logging.FileHandler("devscan.log"))
        
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(module)s - %(message)s",
        handlers=handlers
    )

def parse_args() -> argparse.Namespace:
    """Defines and parses the command-line arguments (SRS FR-01 to FR-07)"""
    parser = argparse.ArgumentParser(description="DevScan: Local Codebase Health Analyser CLI")
    
    parser.add_argument("path", help="Path to the target directory")
    parser.add_argument("--lang", choices=["python", "js", "all"], default="python", 
                        help="Restrict file types scanned (default: python)")
    parser.add_argument("--format", choices=["terminal", "json"], default="terminal", 
                        help="Control output mode (default: terminal)")
    parser.add_argument("--no-ai", action="store_true", 
                        help="Skip the AI summary step")
    parser.add_argument("--output", default="./report.json", 
                        help="Filepath for JSON report (default: ./report.json)")
    parser.add_argument("--verbose", action="store_true", 
                        help="Enable DEBUG logging")
    
    return parser.parse_args()

def main() -> None:
    args = parse_args()
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    target_dir = Path(args.path)
    
    if not target_dir.exists() or not target_dir.is_dir():
        logger.error("Target path does not exist or is not a directory.")
        print("Error: Please provide a valid directory path.", file=sys.stderr)
        sys.exit(1)

    try:
        logger.info(f"Starting scan on {args.path} for language: {args.lang}")
        
        # 1. Scan the directory
        from scanner import Scanner
        scanner = Scanner(args.lang)
        file_results = scanner.scan(target_dir)
        
        if not file_results:
            print("No valid source files found to analyse.")
            sys.exit(0)

        # 2. Analyse the code
        from analyser import Analyser
        analyser = Analyser()
        file_stats, summary = analyser.analyse(file_results)

        # 3. Report the findings
        from reporter import Reporter
        reporter = Reporter(args.format, args.output)
        reporter.report(file_stats, summary)

        # 4. Generate AI Summary and Start Chat (unless skipped)
        if not args.no_ai:
            from ai_summary import interactive_chat
            interactive_chat(summary, file_results, file_stats)
            
        sys.exit(0) 
        
    except Exception as e:
        logger.exception("An unrecoverable error occurred.")
        print(f"Error: Scan failed due to an unexpected issue. {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()