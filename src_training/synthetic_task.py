import top_down_task_synthesis


class SyntheticTask:

    def __init__(self, program_task, specifications):
        self.program = program_task
        self.specifications = specifications
        sub_program_set = set()
        program_task.get_sub_programs(sub_program_set)
        self.subprograms = sub_program_set
        positive_training_data = []
        sub_program_outputs = set()
        for sub_program in sub_program_set:
            program_outputs = []
            positive_data_point = top_down_task_synthesis.generate_datapoint(self.program, sub_program,
                                                                             specifications[4], specifications[0],
                                                                             specifications[2])
            if positive_data_point is not None:
                positive_data_point['label'] = 1
                positive_training_data.append(positive_data_point)
            for input_output_example in specifications[4]:
                program_outputs.append(sub_program.interpret(input_output_example))
            sub_program_outputs.add(tuple(program_outputs))

        self.positive_training_data = positive_training_data
        self.sub_program_outputs = sub_program_outputs

    def get_program(self):
        return self.program

    def get_sub_programs(self):
        return self.subprograms

    def get_specifications(self):
        return self.specifications

    def get_positive_training_data(self):
        return self.positive_training_data

    def get_sub_program_outputs(self):
        return self.sub_program_outputs
