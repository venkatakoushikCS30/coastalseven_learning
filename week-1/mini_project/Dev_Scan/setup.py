from setuptools import setup

setup(
    name="devscan",
    version="1.0",
    description="Local Codebase Health Analyser CLI with AI refactoring suggestions.",
    author="Solo Developer",
    # Replaced packages with py_modules to support flat files
    py_modules=["cli", "models", "scanner", "analyser", "reporter", "ai_summary"],
    install_requires=[
        "rich>=13.0",
        "requests>=2.31",
        "python-dotenv>=1.0"
    ],
    entry_points={
        "console_scripts": [
            "devscan=cli:main", 
        ],
    },
    python_requires=">=3.11",
)