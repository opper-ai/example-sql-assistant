# Database Query Assistant

This project is a simple SQLite database query assistant that uses Opper to generate SQL queries and create responses. It's designed to be an easy-to-understand example for beginners learning about database interactions and AI-assisted query generation.

## Features

- Interactive command-line interface
- Automatic SQL query generation based on natural language input
- Database structure introspection
- Query execution and result presentation
- Suggestion of follow-up questions
- User feedback collection
- Tracing of calls an sessions
  
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
