from BIO465 import Assignment
import pandas


class Homework(Assignment):
    def __init__(self, title: str, body: str, instructions: str, number: int):
        """
        :type title, body, instructions, number
        """
        super().__init__(title, body, instructions, number)
        self.dataframes = []

    """gets the dataframe file and returns a string of its contents"""
    def get_dataframe_file(self, file_path: str) -> str:  # TODO get the dataframe file path
        pass

    """parses the dataframe file and puts it into a pandas dataframe"""
    def parse_dataframe_file(self, file_string: str) -> pandas.array:  # TODO parse the dataframe string contents
        pass

    """To string method for Homework object"""
    def __str__(self) -> str:
        return f"Type: Homework\n{super.__str__()}"

    """How Homework will represent itself"""
    def __repr__(self) -> str:
        return self.__str__()

