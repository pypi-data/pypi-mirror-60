from abc import ABC, abstractmethod


class Assignment:
    """
    The Assignment class is a parent class for labs and homework, it is to give them their attributes
    and given them common methods
    """
    def __init__(self, title: str, body: str, instructions: str, number: int):
        self.title = title
        self.body = body
        self.instructions = instructions
        self.number = number

    def get_title(self) -> str:
        return self.title

    def get_body(self) -> str:
        return self.body

    def get_instructions(self) -> str:
        return self.instructions

    def get_number(self) -> int:
        return self.number

    def __str__(self) -> str:
        return f"Title:{self.title}\nBody:{self.body}\nInstructions:{self.instructions}\nNumber:{self.number}"
