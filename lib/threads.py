import threading
import queue
import time
import json
from pathlib import Path
from abc import ABC, abstractmethod
import concurrent.futures

import pandas as pd

from . import logger, path, tools

log = logger.getLogger(__name__)

def _str_strip(df_or_s, to_strip=None):
    """
    Strip whitespaces from a DataFrame and its column names or Series and from
    the Series name if name is stored in class.

    This is assuming we ALWAYS want to strip any leading and trailing
    whitespaces (because who really needs those).

    >>> _str_strip(df_or_s)
    >>> _str_strip(df_or_s, to_strip='##')

    :param df_or_s: DataFrame or Series
    :param to_strip: Strings to strip. If None, strips whitespace.
    :return: DataFrame or Series
    """

    # Copy object
    df_or_s_copy = df_or_s.copy()

    if isinstance(df_or_s_copy, pd.DataFrame):
        # Strip whitespaces from the columns
        df_or_s_copy.columns = df_or_s_copy.columns.str.strip()

        # Strip whitespaces from the Series if they are of type object
        for col in df_or_s_copy.select_dtypes(include=['object']).columns:
            df_or_s_copy[col] = df_or_s_copy[col].str.strip(to_strip)
    else:
        # Strip whitespaces from the Series
        df_or_s_copy = df_or_s_copy.str.strip(to_strip)

        # Strip whitespaces from the column name
        if df_or_s_copy.name:
            df_or_s_copy.name = df_or_s_copy.name.strip()

    return df_or_s_copy

class LoaderBase(threading.Thread):
    def __init__(self, path):
        super().__init__()
        self.path = path
        self.data = None  # Variable to store the loaded JSON data

    @abstractmethod
    def run(self, *args, **kwargs):
        pass

class DataLoader(LoaderBase):
    def __init__(self, p, fn=pd.read_csv, encoding=None,
                 strip_whitespaces = True, *args, ** kwargs):
        super().__init__(p)
        self.fn = fn
        self.encoding = encoding
        self.strip_whitespaces = strip_whitespaces
        self.args = args
        self.kwargs = kwargs

    def run(self):
        self.data = tools.read_data(self.path,
                                    fn=self.fn,
                                    encoding=self.encoding,
                                    strip_whitespaces=self.strip_whitespaces,
                                    *self.args,
                                    **self.kwargs)

class JsonNormalizeLoader(LoaderBase):

    def run(self):
        try:
            self.data = tools.read_json(self.path)
        except FileNotFoundError:
            print(f"Error: File not found at {self.path}")
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from {self.path}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


def read_json(p):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(tools.read_json, p)

        print("Main thread is doing other work...")
        # Simulate other work in the main thread
        for i in range(5):
            print(f"Main thread working... {i+1}")
            time.sleep(0.5)

        # Check if the background task is done and retrieve the result
        if future.done():
            file_content = future.result()
            print(f"\nFile content retrieved: '{file_content}'")
        else:
            print("\nFile loading still in progress. Waiting for result...")
            file_content = future.result() # This will block until the result is ready
            print(f"File content retrieved after waiting: '{file_content}'")

    print("Main thread finished.")


# Example usage:
if __name__ == "__main__":
    json_file_path = "example.json" # Replace with your JSON file path

    # Create a dummy JSON file for demonstration
    with open(json_file_path, 'w') as f:
        json.dump({"name": "Alice", "age": 30, "city": "New York"}, f)

    loader_thread = JsonNormalizeLoader(json_file_path)
    loader_thread.start() # Start the thread
    loader_thread.join()  # Wait for the thread to complete

    loaded_data = loader_thread.data

    if loaded_data:
        print("JSON data loaded successfully:")
        print(loaded_data)
    else:
        print("Failed to load JSON data.")