POSITION = 0
IMMEDIATE = 1
RELATIVE = 2
ADD = 1
MULTIPLY = 2
READ = 3
WRITE = 4
JUMP_TRUE = 5
JUMP_FALSE = 6
LESS_THAN = 7
EQUAL = 8
JUMP_RP = 9
HALT = 99


class IntCodeComputer:
    class Instruction:
        def __init__(self):
            self.op = []
            self.modes = []
            self.length = 0

        def set_length(self):
            if self.op in [ADD, MULTIPLY, LESS_THAN, EQUAL]:
                self.length = 4
            elif self.op in [ JUMP_TRUE, JUMP_FALSE]:
                self.length = 3
            else:
                self.length = 2

        def set_op(self, memory, ip):
            self.op = int(str(memory[ip])[-2:])

        def set_param_modes(self, memory, ip):
            self.modes = list(map(int, list(str(memory[ip])[:-2])))
            self.modes.reverse()
            while len(self.modes) < self.length - 1:
                self.modes.append(0)

        def fetch_and_decode(self, memory, ip):
            self.set_op(memory, ip)
            self.set_length()
            self.set_param_modes(memory, ip)

    def __init__(self, memory, input_list, output_list):
        self.memory = memory.copy()
        self.memory.extend([0 for x in range(10000)])
        self.ip = 0
        self.ir = 0
        self.rp = 0
        self.params = []
        self.jump_flag = False
        self.halt_flag = False
        self.waiting = False
        self.input_list = input_list
        self.output_list = output_list

    def get_data(self, l):
        return self.memory[self.ip + 1:self.ip + l]

    def run_until(self):
        self.step()
        while not self.waiting and not self.halt_flag:
            self.step()

    def run(self):
        self.step()
        while not self.halt_flag and self.ip < len(self.memory):
            self.step()

    def check(self, n):
        if n[0] == RELATIVE:
            return self.memory[self.rp + n[1]]
        if n[0] == IMMEDIATE:
            return n[1]
        else:
            return self.memory[n[1]]

    def step(self):
        self.ir = self.Instruction()
        self.ir.fetch_and_decode(self.memory, self.ip)
        self.params = self.get_data(self.ir.length)
        self.jump_flag = False
        self.waiting = False

        if self.ir.op == HALT:
            self.halt_flag = True
        else:
            data = list(map(self.check, zip(self.ir.modes, self.params)))
            if self.ir.op == ADD:
                if self.ir.modes[2] == POSITION:
                    self.memory[self.params[-1]] = data[0] + data[1]
                else:
                    self.memory[self.params[-1] + self.rp] = data[0] + data[1]
            elif self.ir.op == MULTIPLY:
                if self.ir.modes[2] == POSITION:
                    self.memory[self.params[-1]] = data[0] * data[1]
                else:
                    self.memory[self.params[-1] + self.rp] = data[0] * data[1]
            elif self.ir.op == WRITE:
                self.output_list.append(data[0])
            elif self.ir.op == READ:
                if len(self.input_list) < 1:
                    self.waiting = True
                else:
                    in_data = self.input_list.pop(0)
                    if self.ir.modes[0] == POSITION:
                        self.memory[self.params[-1]] = in_data
                    else:
                        self.memory[self.params[-1] + self.rp] = in_data
            elif self.ir.op == JUMP_TRUE:
                if data[0] != 0:
                    self.ip = data[1]
                    self.jump_flag = True
                else:
                    self.jump_flag = False
            elif self.ir.op == JUMP_FALSE:
                if data[0] == 0:
                    self.ip = data[1]
                    self.jump_flag = True
                else:
                    self.jump_flag = False
            elif self.ir.op == LESS_THAN:
                x = 0
                if data[0] < data[1]:
                    x=1
                if self.ir.modes[2] == POSITION:
                    self.memory[self.params[-1]] = x
                else:
                    self.memory[self.params[-1] + self.rp] = x
            elif self.ir.op == EQUAL:
                x = 0
                if data[0] == data[1]:
                    x = 1
                if self.ir.modes[2] == POSITION:
                    self.memory[self.params[-1]] = x
                else:
                    self.memory[self.params[-1] + self.rp] = x
            elif self.ir.op == JUMP_RP:
                self.rp += data[0]
            else:
                print("NOOP")

        if not self.jump_flag and not self.waiting and not self.halt_flag:
            self.ip += self.ir.length

