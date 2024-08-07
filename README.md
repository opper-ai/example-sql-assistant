# Database Query Assistant

This project is a simple general purpose SQLite database query assistant that uses Opper to generate SQL queries and create responses. It's designed to be an easy-to-understand example for beginners learning about building end to end LLM based features that includes calling models with structured prompting, implementing reflection, chain of thought reasoning, feedback collection and tracing to facilitate human in the loop.

Sign up for Opper at https://opper.ai/

## Features

- Supports any SQLlite database (bundled with "https://github.com/lerocha/chinook-database.db")
- Conversational query interface (LLM)
- Automatic SQL query generation with CoT and Structured Prompting (LLM)
- Query execution and result presentation (LLM)
- Suggestion of follow-up questions (LLM)
- User feedback collection and Metrics
- Tracing of Session, LLM calls and other Operations

## Ideas

* Implement Caching of LLM functions to improve latency
* Use Examples and run calls with a small and fast model
* Implement Agentic loop with tool usage
* Serve as an API
  
## Installation

1. Clone this repository:

```
git clone https://github.com/opper-ai/example-database-assistant.git
cd example-database-assistant
```

2. Install the required dependencies:
```
pip install -r requirements.txt
```

3. Set your Opper API key:

```
export OPPER_API_KEY=your_api_key
```

## Usage

Run the assistant with:

```
python src/main.py

Optional arguments:
- `-d`, `--database`: Specify the path to the SQLite database file (default: `data/chinook.db`)
- `-v`, `--verbose`: Show SQL query and detailed results
```

Note that the project will default to using the `chinook.db` database file in the `data/` directory.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
