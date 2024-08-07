from opperai import Opper, trace
from opperai.types import CacheConfiguration
import sqlite3
import argparse
from typing import List, Tuple
from pydantic import BaseModel
from typing import Literal
import readline

opper = Opper()

"""
This code is a simple SQLite database query assistant that uses Opper to generate SQL queries and create responses.
It utilizes the Opper framework to handle the conversation, generate SQL queries, and create responses.
The assistant is designed to be simple and easy to understand, making it a good example for beginners to learn from.
It implements a retry mechanism to catch runtime issues and poor results and iterate on the query until it is successful.
We make use of tracing to track all steps of the program. We add metrics to catch user feedback which gets added to
the relevant part of the trace. Use the Opper portal to view the traces and feedback.
"""

class DatabaseManager:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    @trace
    def get_db_structure(self) -> str:
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = self.cursor.fetchall()
        
        description = []
        for table in tables:
            table_name = table[0]
            description.append(f"\nTable: {table_name}")

            # Collect the structure of the table
            self.cursor.execute(f"PRAGMA table_info({table_name});")
            columns_info = self.cursor.fetchall()
            description.append("Columns:")
            for column in columns_info:
                description.append(f"  {column[1]} (Type: {column[2]}, Not Null: {column[3]}, Default Value: {column[4]}, Primary Key: {column[5]})")

            # Collect a sample row from the table
            self.cursor.execute(f"SELECT * FROM {table_name} LIMIT 1;")
            sample_row = self.cursor.fetchone()
            description.append(f"Sample row: {sample_row}")

        return "\n".join(description)
    
    @trace
    def run_sql_query(self, sql_query: str):
        try:
            self.cursor.execute(sql_query)
            return self.cursor.fetchall()
        except sqlite3.OperationalError as e:
            return str(e)

    def close(self):
        self.conn.close()

class Query(BaseModel):
    thoughts: str
    plan: str
    sql_query: str

class Reflection(BaseModel):
    thoughts: str
    success: bool

def describe_database(db_structure: str) -> str:
    return opper.call(
        "describe_database",
        instructions="Given a database structure, provide a simple overview of what the database is about",
        input={
            "db_structure": db_structure,
        },
        output_type=str
    )

def generate_sql_query(conversation: str, db_structure: str, comment: str = "None") -> Query:
    return opper.call(
        "generate_sql_query",
        instructions="Given a conversation and a database structure and comments on previous attempts, generate an sql query to answer the question",
        input={
            "conversation": conversation,
            "db_structure": db_structure,
            "comment": comment
        },
        output_type=Query,
    )

def create_response(conversation: str, db_structure: str, query_result: str) -> str:
    return opper.call(
        "create_response",
        instructions="Given a conversation, a database structure and a query result, construct an appropriate response to the question",
        input={
            "conversation": conversation,
            "db_structure": db_structure,
            "query_result": query_result
        },
        output_type=str
    )

def reflect_on_result(conversation: str, db_structure: str, query: str, query_result: str) -> Reflection:
    return opper.call(
        "reflect_on_result",
        instructions="Given a conversation, a database structure, a query and a query result, reflect and decide if you are satisfied with the query or want to improve it",
        input={
            "conversation": conversation,
            "db_structure": db_structure,
            "query": query,
            "query_result": query_result
        },
        output_type=Reflection
    )

def suggest_question(conversation: str, db_structure: str) -> str:
    return opper.call(
        "suggest_question",
        instructions="Given a conversation and a database structure, suggest a likely question that the user might ask next",
        input={
            "conversation": conversation,
            "db_structure": db_structure,
        },
        output_type=str
    )

def main():
    parser = argparse.ArgumentParser(description="Database Query Assistant")
    parser.add_argument("-d", "--database", default="data/chinook.db", help="Path to the SQLite database file (default: data/chinook.db)")
    parser.add_argument("-v", "--verbose", action="store_true", default=False, help="Show SQL query and detailed results")
    args = parser.parse_args()

    db_manager = DatabaseManager(args.database)

    print("\nWelcome to the Database Query Assistant.")
    print("Type 'describe' to get a description of the database.")
    print("Type 'rate' to rate the last response.")
    print("Type 'suggest' if you feel lucky.")
    print("Type 'exit' to quit.")

    conversation = ""
    
    with opper.traces.start("session") as span_session:

        db_structure = db_manager.get_db_structure()

        while True:

            user_question = input("\nQuestion: ")

            if not conversation:
                span_session.update(input=user_question)
            
            if user_question.lower() == 'exit':
                break
            
            elif user_question.lower() == 'describe':
                db_description, response = describe_database(db_structure)
                print("\nAssistant:", db_description)
                continue
            
            elif user_question.lower() == 'rate':
                rating = input("How was the response? (1-5): ")
                comment = input("Comment: ")
                previous_span_cycle.save_metric("user_rating", rating, comment=comment)
                continue
            
            elif user_question.lower() == 'suggest':
                suggestion, response = suggest_question(conversation, db_structure)
                print(suggestion)
                user_question = suggestion

            # We start a new sub trace for each cycle of question and response
            with opper.traces.start("cycle") as span_cycle:

                # We add the user question to the cycle span
                span_cycle.update(input=user_question)
                conversation += f"Question: {user_question}\n"
                
                # We set the number of attempts to 3
                attempts = 3
                
                # We set the debug text color
                debug_text_color = "\033[90m"
                color_reset = "\033[0m"
                runtime_feedback = ""

                for attempt in range(attempts):

                    # Generate SQL query
                    result, obj = generate_sql_query(conversation, db_structure, comment=runtime_feedback)
                    
                    if args.verbose:
                        print(f"{debug_text_color}\nThoughts: {result.thoughts}{color_reset}")
                        print(f"{debug_text_color}Plan: {result.plan}{color_reset}")
                        print(f"{debug_text_color}Query: {result.sql_query}{color_reset}")
    
                    # Execute SQL query
                    query_result = db_manager.run_sql_query(result.sql_query)
           
                    if args.verbose:
                        print(f"{debug_text_color}Results: {query_result}{color_reset}")
                    
                    # Reflect on the result
                    reflection, response = reflect_on_result(conversation, db_structure, result, query_result)
                    
                    # Reflect and repeat if not successful
                    if not reflection.success:
                        if args.verbose:
                            print(f"{debug_text_color}Reflection: {reflection}{color_reset}")
                        runtime_feedback = reflection.thoughts                    
                    else:
                        if args.verbose:
                            print(f"{debug_text_color}Reflection: Success{color_reset}")
                        break
                else:
                    print("Assistant: Failed to generate a valid query after 3 attempts. Please rephrase your question.")
                    continue

                # Create response
                result, obj = create_response(conversation, db_structure, query_result)
                print("\nAssistant:", result)

                conversation += f"Response: {result}\n\n"

                # We update the cycle span with the final response
                span_cycle.update(output=result)

                # We store this span so we can add user feedback to it later
                previous_span_cycle = span_cycle

            # We update the root span with the final response
            span_session.update(output=result)

    db_manager.close()
    print("\nThank you for using the Database Query Assistant. Goodbye!\n")

if __name__ == "__main__":
    main()