class BustlePCFG:
    __instance = None

    @staticmethod
    def get_instance():
        if BustlePCFG.__instance is None:
            raise Exception("Need to initialize the grammar first")

        return BustlePCFG.__instance

    @staticmethod
    def initialize(program_list):
        BustlePCFG(program_list)

    def __init__(self, program_list):
        self.program_list = program_list
        self.program_id = 0
        BustlePCFG.__instance = self

    def get_program_id(self):
        self.program_id += 1
        return self.program_id

    def generate_program(self, return_type, height):
        return self.program_list.generate_program(return_type, height)
