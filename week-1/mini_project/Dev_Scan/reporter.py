# reporter.py
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from models import FileStat, ProjectSummary

logger = logging.getLogger(__name__)

class Reporter:
    def __init__(self, format_mode: str, output_filepath: str):
        self.format_mode = format_mode
        self.output_filepath = output_filepath
        self.console = Console()

    def _finalize_summary(self, summary: ProjectSummary) -> ProjectSummary:
        """Adds the final timestamp to the summary data."""
        summary['scan_timestamp'] = datetime.now(timezone.utc).isoformat()
        return summary

    def render_terminal(self, file_stats: Dict[str, FileStat], summary: ProjectSummary):
        """Renders the health metrics as a formatted terminal table (FR-24, FR-25, FR-26)."""
        table = Table(title="DevScan Codebase Health Report", show_header=True, header_style="bold magenta")
        
        table.add_column("File", style="cyan", no_wrap=True)
        table.add_column("Functions", justify="right")
        table.add_column("TODOs", justify="right")
        table.add_column("Max Complexity", justify="right")
        table.add_column("Health", justify="center")

        # Sort files alphabetically for consistent output (NFR-06)
        for path in sorted(file_stats.keys()):
            stat = file_stats[path]
            
            # Color-code the health indicator
            health_color = stat['health'].lower()
            health_display = f"[{health_color}]{stat['health']}[/{health_color}]"
            
            table.add_row(
                path,
                str(len(stat['functions'])),
                str(stat['todos']),
                str(stat['max_complexity']),
                health_display
            )

        self.console.print(table)
        self.console.print("\n")

        # Project-wide summary panel (FR-26)
        summary_text = (
            f"Total Files Scanned: [bold]{summary['total_files']}[/bold]\n"
            f"Total Functions Found: [bold]{summary['total_functions']}[/bold]\n"
            f"Total TODO/FIXMEs: [bold]{summary['total_todos']}[/bold]\n"
            f"Dead Functions: [bold red]{len(summary['dead_functions'])}[/bold red]\n"
            f"Duplicate Functions: [bold yellow]{len(summary['duplicate_functions'])}[/bold yellow]"
        )
        
        self.console.print(Panel(summary_text, title="Project Summary", border_style="blue"))

    def export_json(self, file_stats: Dict[str, FileStat], summary: ProjectSummary):
        """Exports the data to a JSON file matching the schema in Section 6.4 (FR-27)."""
        output_data = {
            "meta": {
                "devscan_version": "1.0",
                "scan_timestamp": summary['scan_timestamp'],
            },
            "project": summary,
            "files": file_stats
        }

        try:
            output_path = Path(self.output_filepath)
            # Ensure the directory exists before writing
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=4)
            
            logger.info(f"JSON report exported successfully to {self.output_filepath}")
        except Exception as e:
            logger.error(f"Failed to write JSON report: {e}")
            self.console.print(f"[bold red]Error:[/bold red] Could not write JSON file to {self.output_filepath}")

    def report(self, file_stats: Dict[str, FileStat], summary: ProjectSummary):
        """Main entry point to route the data to the correct output format."""
        final_summary = self._finalize_summary(summary)

        if self.format_mode == "terminal":
            self.render_terminal(file_stats, final_summary)
        elif self.format_mode == "json":
            self.export_json(file_stats, final_summary)
        
        # FR-28: Always print a human-readable one-line status at the end
        print(f"\nScan complete. {final_summary['total_files']} files analysed.")