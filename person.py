class Person:
    def __init__(self, client, address):
        self.address = address
        self.client = client
        self.name = None

    def set_name(self, name):
        self.name = name

    def __repr__(self):
        return f"Person({self.address}, {self.name})"
