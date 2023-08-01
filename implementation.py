from collections import defaultdict, deque
import tkinter as tk
from tkinter import filedialog

output_gui = []
output_head_list = []
turn_num = 0
curr_head = 0
branch_num = 0
branch_counter = 0
is_last_branch = False
machine_definition = "% HEADER\n" \
                  "q0 q1 # 1\n" \
                  "% TRANSITIONS\n" \
                  "q0,1,q0,1 R\n" \
                  "q0,0,q0,# R\n" \
                  "q0,#,q1,# S\n\n\n"\
                  "% <current state>,<current input>,<new state>,<write symbol> <direction>"


class Tape:
    # Constructor. Sets the blank symbol, the
    # string to load and the position of the tape head
    def __init__(self, blank, string='', head=0):
        global curr_head
        self.blank = blank
        self.loadString(string, head)

        # Loads a new string and sets the tape head

    def loadString(self, string, head):
        global branch_num

        self.symbols = list(string)
        self.head = head

        if self.symbols != []:
            output_gui.append([])
            output_head_list.append([])

            branch_num += 1

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
        global curr_head, new_branch
        curr_head = self.head
        new_branch = True
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
        global curr_head, branch_counter
        self.state, moves = trans


        output_tape = str(self)
        output_tape = output_tape.replace('[', '')
        output_tape = output_tape.replace(']', '')
        output_tape = output_tape.replace("'", '')
        output_tape = output_tape.replace(',', '')

        output_tape = output_tape.replace('\n', '')
        output_tape = output_tape.replace(' ', '')
        head_num = (len(self.state) + 1) + curr_head
        output_head = output_tape[0:head_num] + 'V' + output_tape[head_num + 1:]

        for idx, let in enumerate(output_head):
            if let != 'V':
                let = ' '
                output_head = output_head[0:idx] + let + output_head[idx + 1: ]

        if branch_counter < branch_num:

            output_gui[branch_counter].append(output_tape)
            output_head_list[branch_counter].append(output_head)
            branch_counter += 1


            if branch_counter == branch_num:
                branch_counter = 0

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
        global branch_counter, is_last_branch
        num_of_branches = 0
        list_len = 0

        num_inp = input_text.get("1.0",'end-1c')


        tm = NDTM.parse(machine_definition)
        acc_tm = tm.accepts(num_inp)

        if acc_tm:
            branch_counter = 0
            steps_btn['state'] = tk.NORMAL
            reset_btn['state'] = tk.NORMAL
            compute_btn['state'] = tk.DISABLED

            for item in output_gui:
                if item != []:
                    num_of_branches += 1

            for item in output_gui[num_of_branches-1]:
                list_len += 1

            label.config(text="Final String and State = "+ output_gui[num_of_branches-1][list_len-1]+ " (ACCEPTED)", fg="#008000")
            if branch_num > 1:
                next_branch_btn['state'] = tk.NORMAL
                accepted_branch_btn['state'] = tk.NORMAL
            else:
                is_last_branch = True
        else:
            label.config(
                text="REJECTED",
                fg="#FF0000")
            reset_btn['state'] = tk.NORMAL
            compute_btn['state'] = tk.DISABLED



def display_steps():
        global turn_num, branch_counter
        list_len = 0

        head_label.config(text=output_head_list[branch_counter][turn_num])
        label.config(text=output_gui[branch_counter][turn_num], fg="#000000")
        turn_num += 1

        for item in output_gui[branch_counter]:
            list_len += 1

        if turn_num == list_len:
            if is_last_branch == True:
                label.config(text=output_gui[branch_counter][turn_num-1], fg="#008000")

            steps_btn['state'] = tk.DISABLED
            turn_num = 0




def reset():
    global turn_num, output_gui, output_head_list, curr_head, branch_counter,branch_num, is_last_branch
    turn_num = 0
    branch_counter = 0
    branch_num = 0
    output_gui = []
    output_head_list = []
    curr_head = 0
    is_last_branch = False
    label.config(text="", fg="#000000")
    head_label.config(text="", fg="#000000")
    steps_btn['state'] = tk.DISABLED
    reset_btn['state'] = tk.DISABLED
    compute_btn['state'] = tk.NORMAL
    next_branch_btn['state'] = tk.DISABLED
    accepted_branch_btn['state'] = tk.DISABLED

def next_branch():
    global branch_counter, turn_num, is_last_branch
    num_of_branches = 0

    branch_counter += 1
    turn_num = 0
    steps_btn['state'] = tk.NORMAL

    head_label.config(text=output_head_list[branch_counter][turn_num])
    label.config(text=output_gui[branch_counter][turn_num])

    for item in output_gui:
        if item != []:
            num_of_branches += 1

    if branch_counter == num_of_branches - 1:
        next_branch_btn['state'] = tk.DISABLED
        accepted_branch_btn['state'] = tk.DISABLED
        is_last_branch = True

def accepted_branch():
    global branch_counter, turn_num, is_last_branch
    num_of_branches = 0
    is_last_branch = True

    for item in output_gui:
        if item != []:
            num_of_branches += 1


    branch_counter = num_of_branches - 1
    turn_num = 0
    steps_btn['state'] = tk.NORMAL
    next_branch_btn['state'] = tk.DISABLED
    accepted_branch_btn['state'] = tk.DISABLED

    head_label.config(text=output_head_list[branch_counter][turn_num])
    label.config(text=output_gui[branch_counter][turn_num])


def browseFiles():
    global machine_definition
    filename = filedialog.askopenfilename(initialdir="/",
                                          title="Select a File",
                                          filetypes=(("Text files",
                                                      "*.txt*"),
                                                     ("TM files",
                                                      "*.tm*")))
    tf = open(filename)  # or tf = open(tf, 'r')
    machine_definition = tf.read()
    tf.close()

    file_label.config(text="File Opened: "+filename)


if __name__ == '__main__':
    # Example TM that performs unary complement
    window = tk.Tk()
    window.geometry("1200x1000")

    # Initialize a Label to display the User Input
    head_label = tk.Label(window, text="", font=("Courier 22 bold"))
    head_label.pack()
    label = tk.Label(window, text="", font=("Courier 22 bold"))
    label.pack()

    sample_input = "11011101"

    # Create an Entry widget to accept User Input
    input_text_label = tk.Label(text="Input", font=("Courier 13"))
    input_text = tk.Text(window, width=40, height=3, font=("Courier 13"))
    input_text.insert(tk.END, sample_input)

    machine_definition_label = tk.Label(text="Machine Definition", font=("Courier 13"))

    input_text_label.pack(padx=30)
    input_text.pack(expand=False, fill = "x",padx=30)
    machine_definition_label.pack(padx=30)

    file_label = tk.Label(window,
                                text="File Explorer using Tkinter",
                                width=100, height=4,
                                fg="blue")

    file_label.pack()
    file_btn = tk.Button(window,
                        text = "Browse Files",
                        command = browseFiles)

    file_btn.pack()

    instructions_text = tk.Label(text="INSTRUCTIONS\n\n"
                                      "<Compute> - Computes your designated input with the machine file you submitted\n"
                                      "<Next> - Proceeds to the next step of the current configuration branch\n"
                                      "<Next Branch> - Proceeds to the next computed branch (for nondeterministic machines only)\n"
                                      "<Accepted Branch> - Skips to the accepted branch (for nondeterministic machines only)\n"
                                      "<Reset> - Resets the program (Must be pressed first before computing for another machine and/or input)\n\n\n"
                                      "NOTE: Due to the nondeterministic nature of the machine, there may be multiple accepted branches.\n"
                                      "This program computes all the branches of the same level in the tree, simultaneously,\n"
                                      "and stops when a branch/branches in a level have reached an accepting state.\n"
                                      "It is completely possible to have multiple accepted branches, but for the purpose of this program,\n"
                                      "only the last branch will turn green.\n\n"
                                      "It is also important to note that the 'Accepted Branch' may only contain a portion of the steps\n"
                                      "computed to get to the accepted state. This is because it is possible that the 'Accepted Branch'\n"
                                      "is a sub-branch of another branch, and has diverged from the list of branches of the program,\n"
                                      "generating a different set of branches, which exludes the previous steps computed.\n\n"
                                      "You can test out the program right away by computing without changing the input and\n"
                                      "without adding a file. There is currently a sample machine stored that removes all 0's\n"
                                      "of an input string of the language - (0 U 1)*",
                                 font=("Courier 12"), fg="#6F6F6F")

    instructions_text.pack(pady=20)

    compute_btn = tk.Button(window, text="Compute", width=20, command=display_text)
    compute_btn.pack(pady=20, padx=40, side=tk.LEFT)

    steps_btn = tk.Button(window, text="Next", width=20, command=display_steps, state= tk.DISABLED)

    steps_btn.pack(pady=20, padx=40, side= tk.LEFT)
    reset_btn = tk.Button(window, text="Reset", width=20, command=reset, state= tk.DISABLED)
    reset_btn.pack(pady=20, padx=40, side=tk.RIGHT)


    next_branch_btn = tk.Button(window, text="Next Branch", width=20, command=next_branch, state= tk.DISABLED)
    next_branch_btn.pack(pady=20, padx=40, side=tk.LEFT)
    accepted_branch_btn = tk.Button(window, text="Accepted Branch", width=20, command=accepted_branch, state=tk.DISABLED)
    accepted_branch_btn.pack(pady=20, padx=40, side=tk.LEFT)

    window.mainloop()