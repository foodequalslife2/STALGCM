from collections import defaultdict, deque
import tkinter as tk
from tkinter import scrolledtext

output_gui = []
output_head_list = []
turn_num = 0
curr_head = 0
tree_num = 0
tree_counter = 0
is_last_tree = False


class Tape:
    # Constructor. Sets the blank symbol, the
    # string to load and the position of the tape head
    def __init__(self, blank, string='', head=0):
        global curr_head
        self.blank = blank
        self.loadString(string, head)

        # Loads a new string and sets the tape head

    def loadString(self, string, head):
        global tree_num

        self.symbols = list(string)
        self.head = head

        if self.symbols != []:
            output_gui.append([])
            output_head_list.append([])

            tree_num += 1

        # Returns the symbol on the current cell, or the blank

    # if the head is on the start of the infinite blanks
    def readSymbol(self):

        if self.head < len(self.symbols):
            return self.symbols[self.head]
        else:
            return self.blank

            # Writes a symbol in the current cell, extending

    # the list if necessary
    def writeSymbol(self, symbol):

        if self.head < len(self.symbols):
            self.symbols[self.head] = symbol

        else:
            self.symbols.append(symbol)

            # Moves the head left (-1), stay (0) or right (1)

    def moveHead(self, direction):
        global curr_head
        if direction == 'L':
            inc = -1
        elif direction == 'R':
            inc = 1
        else:
            inc = 0
        self.head += inc
        curr_head = self.head



        # Creates a new tape with the same attributes than this

    def clone(self):
        global curr_head, new_tree
        curr_head = self.head
        new_tree = True
        return Tape(self.blank, self.symbols, self.head)

        # String representation of the tape

    def __str__(self):
        global curr_head
        curr_head = self.head
        return str(self.symbols[:self.head]) + \
               str(self.symbols[self.head:])


class NDTM:
    # Constructor. Sets the start and final states and
    # inits the TM tapes
    def __init__(self, start, final, blank='#', ntapes=1):
        self.start = self.state = start
        self.final = final
        self.tapes = [Tape(blank) for _ in range(ntapes)]
        self.trans = defaultdict(list)

        # Puts the TM in the start state and loads an input

    # string into the first tape
    def restart(self, string):
        self.state = self.start
        self.tapes[0].loadString(string, 0)
        for tape in self.tapes[1:]:
            tape.loadString('', 0)

            # Returns a tuple with the current symbols read

    def readSymbols(self):
        return tuple(tape.readSymbol() for tape in self.tapes)

        # Add an entry to the transaction table

    def addTrans(self, state, read_sym, new_state, moves):
        self.trans[(state, read_sym)].append((new_state, moves))

        # Returns the transaction that corresponds to the

    # current state & read symbols, or None if there is not
    def getTrans(self):
        key = (self.state, self.readSymbols())
        return self.trans[key] if key in self.trans else None

    # Executes a transaction updating the state and the
    # tapes. Returns the TM object to allow chaining
    def execTrans(self, trans):
        global curr_head, tree_counter
        self.state, moves = trans


        output_tape = str(self)
        output_tape = output_tape.replace('[', '')
        output_tape = output_tape.replace(']', '')
        output_tape = output_tape.replace("'", '')
        output_tape = output_tape.replace(',', '')

        output_tape = output_tape.replace('\n', '')
        output_tape = output_tape.replace(' ', '')
        output_tape = output_tape.replace('#', ' ')
        head_num = (len(self.state) + 1) + curr_head
        output_head = output_tape[0:head_num] + 'V' + output_tape[head_num + 1:]

        for idx, let in enumerate(output_head):
            if let != 'V':
                let = ' '
                output_head = output_head[0:idx] + let + output_head[idx + 1: ]

        if tree_counter < tree_num:

            output_gui[tree_counter].append(output_tape)
            output_head_list[tree_counter].append(output_head)
            tree_counter += 1


            if tree_counter == tree_num:
                tree_counter = 0

        for tape, move in zip(self.tapes, moves):
            symbol, direction = move
            tape.writeSymbol(symbol)
            tape.moveHead(direction)

        return self

    # Returns a copy of the current TM
    def clone(self):
        tm = NDTM(self.start, self.final)
        tm.state = self.state
        tm.tapes = [tape.clone() for tape in self.tapes]
        tm.trans = self.trans  # shallow copy
        return tm

        # Simulates the TM computation. Returns the TM that

    # accepted the input string if any, or None.
    def accepts(self, string):
        self.restart(string)
        queue = deque([self])
        while len(queue) > 0:
            tm = queue.popleft()
            transitions = tm.getTrans()
            if transitions is None:
                # there are not transactions. Exit
                # if the TM is in the final state
                if tm.state == tm.final: return tm
            else:
                # If the transaction is not deterministic
                # add replicas of the TM to the queue
                for trans in transitions[1:]:
                    queue.append(tm.clone().execTrans(trans))

                    # execute the current transition
                queue.append(tm.execTrans(transitions[0]))

        return None

    def __str__(self):
        out = ''
        for tape in self.tapes:
            out += self.state + ': ' + str(tape) + '\n'


        return out

        # Simple parser that builds a TM from a text file

    @staticmethod
    def parse(input):
        tm = None
        for line in input.split('\n'):

                spec = line.strip()
                if len(spec) == 0 or spec[0] == '%': continue
                if tm is None:

                    start, final, blank, ntapes = spec.split()
                    ntapes = int(ntapes)
                    tm = NDTM(start, final, blank, ntapes)

                else:
                    fields = line.split(',')
                    state = fields[0]
                    symbols = tuple(fields[1].split(', '))
                    new_st = fields[2]
                    moves2 = [x.strip('\n') for x in fields[3:] if x!='\n']
                    moves = tuple(tuple(m.split(' '))
                                  for m in moves2)
                    tm.addTrans(state, symbols, new_st, moves)

        return tm

def display_text():
        global tree_counter, is_last_tree

        inp = entry.get("1.0",'end-1c')
        num_inp = input_text.get("1.0",'end-1c')


        tm = NDTM.parse(inp)
        acc_tm = tm.accepts(num_inp)
        label.config(text="Final String and State = ")
        tree_counter = 0
        steps_btn['state'] = tk.NORMAL
        reset_btn['state'] = tk.NORMAL
        compute_btn['state'] = tk.DISABLED

        if tree_num > 1:
            next_tree_btn['state'] = tk.NORMAL
            accepted_tree_btn['state'] = tk.NORMAL
        else:
            is_last_tree = True



def display_steps():
        global turn_num, tree_counter
        list_len = 0

        head_label.config(text=output_head_list[tree_counter][turn_num])
        label.config(text=output_gui[tree_counter][turn_num])
        turn_num += 1

        for item in output_gui[tree_counter]:
            list_len += 1

        if turn_num == list_len:
            if is_last_tree == True:
                label.config(text=output_gui[tree_counter][turn_num-1], fg="#008000")

            steps_btn['state'] = tk.DISABLED
            turn_num = 0




def reset():
    global turn_num, output_gui, output_head_list, curr_head, tree_counter,tree_num, is_last_tree
    turn_num = 0
    tree_counter = 0
    tree_num = 0
    output_gui = []
    output_head_list = []
    curr_head = 0
    is_last_tree = False
    label.config(text="", fg="#000000")
    head_label.config(text="", fg="#000000")
    steps_btn['state'] = tk.DISABLED
    reset_btn['state'] = tk.DISABLED
    compute_btn['state'] = tk.NORMAL
    next_tree_btn['state'] = tk.DISABLED
    accepted_tree_btn['state'] = tk.DISABLED

def next_tree():
    global tree_counter, turn_num, is_last_tree
    num_of_trees = 0

    tree_counter += 1
    turn_num = 0
    steps_btn['state'] = tk.NORMAL

    head_label.config(text=output_head_list[tree_counter][turn_num])
    label.config(text=output_gui[tree_counter][turn_num])

    for item in output_gui:
        if item != []:
            num_of_trees += 1

    if tree_counter == num_of_trees - 1:
        next_tree_btn['state'] = tk.DISABLED
        is_last_tree = True

def accepted_tree():
    global tree_counter, turn_num, is_last_tree
    num_of_trees = 0
    is_last_tree = True

    for item in output_gui:
        if item != []:
            num_of_trees += 1

    tree_counter = num_of_trees -1
    turn_num = 0
    steps_btn['state'] = tk.NORMAL
    next_tree_btn['state'] = tk.DISABLED
    accepted_tree_btn['state'] = tk.DISABLED

    head_label.config(text=output_head_list[tree_counter][turn_num])
    label.config(text=output_gui[tree_counter][turn_num])


if __name__ == '__main__':
    # Example TM that performs unary complement
    window = tk.Tk()
    window.geometry("1200x1000")

    # Initialize a Label to display the User Input
    head_label = tk.Label(window, text="", font=("Courier 22 bold"))
    head_label.pack()
    label = tk.Label(window, text="", font=("Courier 22 bold"))
    label.pack()

    sample_text = "% HEADER\n" \
                  "q0 q1 # 1\n" \
                  "% TRANSITIONS\n" \
                  "q0,1,q0,1 R\n" \
                  "q0,0,q0,# R\n" \
                  "q0,#,q1,# S\n\n\n"\
                  "% <current state>,<current input>,<new state>,<write symbol> <direction>"

    sample_input = "11011101"

    # Create an Entry widget to accept User Input
    input_text_label = tk.Label(text="Input", font=("Courier 13"))
    input_text = tk.Text(window, width=40, height=3, font=("Courier 13"))
    input_text.insert(tk.END, sample_input)

    machine_definition_label = tk.Label(text="Machine Definition", font=("Courier 13"))
    entry = tk.Text(window, width=40, font=("Courier 13"))
    entry.focus_set()

    entry.insert(tk.END, sample_text)

    input_text_label.pack(padx=30)
    input_text.pack(expand=False, fill = "x",padx=30)
    machine_definition_label.pack(padx=30)
    entry.pack(expand=True, fill = tk.BOTH, padx=30, pady=10)

    # Create a Button to validate Entry Widget
    compute_btn = tk.Button(window, text="Compute", width=20, command=display_text)
    compute_btn.pack(pady=20, padx=40, side=tk.LEFT)

    steps_btn = tk.Button(window, text="Next", width=20, command=display_steps, state= tk.DISABLED)

    steps_btn.pack(pady=20, padx=40, side= tk.LEFT)
    reset_btn = tk.Button(window, text="Reset", width=20, command=reset, state= tk.DISABLED)
    reset_btn.pack(pady=20, padx=40, side=tk.RIGHT)


    next_tree_btn = tk.Button(window, text="Next Tree", width=20, command=next_tree, state= tk.DISABLED)
    next_tree_btn.pack(pady=20, padx=40, side=tk.LEFT)
    accepted_tree_btn = tk.Button(window, text="Accepted Tree", width=20, command=accepted_tree, state=tk.DISABLED)
    accepted_tree_btn.pack(pady=20, padx=40, side=tk.LEFT)

    window.mainloop()