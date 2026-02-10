import tkinter as tk # Tkinter to display the GUI
from tkinter import messagebox as msgbox # message box display. Only needed for testing.
from types import SimpleNamespace # Need this to create a dummy event (1 off thing)
from itertools import islice # Need this to crop out characters from a string (1 off thing)
import math

# Global Variables
after_id = None # id of the next generator call (to use to force stop it)

pi_counter = 0 # pi counter
progress_numerator = 0 # progress counter
progress_denominator_increment = 0 # used to track how far
pi_counter_offset = 0

btn_disabled_colour = "#f0f0f0"

####################################################################################################
# Functions
def ent_validation(event):
    entry = event.widget
    entry_text = entry.get()
    cursor_position = entry.index(tk.INSERT)  # Get current cursor position

    # Handle Backspace and Delete keys
    if event.keysym == "BackSpace":
        if cursor_position > 0:  # Ensure the cursor is not at the start
            if entry in (memory_entries[0], memory_entries[1], memory_entries[3]):  # Only resize the 1st & 2nd entry
                new_length = len(entry_text) - 1
                entry.config(width=max(new_length, 1))
        return  # Allow the key press

    if event.keysym == "Delete":
        if cursor_position < len(entry_text):  # Ensure the cursor is not at the end
            if entry in (memory_entries[0], memory_entries[1], memory_entries[3]):  # Only resize the 1st & 2nd entry
                new_length = len(entry_text) - 1
                entry.config(width=max(new_length, 1))
        return  # Allow the key press

    # Handle Left and Right keys
    if event.keysym == "Left":
        if cursor_position > 0:  # Move cursor left if possible
            entry.icursor(cursor_position - 1)
        return 'break'  # Prevent further input

    if event.keysym == "Right":
        if cursor_position < len(entry_text):  # Move cursor right if possible
            entry.icursor(cursor_position + 1)
        return 'break'  # Prevent further input

    # Handle Up and Down keys
    if event.keysym == "Up":
        if entry == memory_entries[0]:
            memory_entries[4].focus_set()  # Move focus to entry 5
        elif entry == memory_entries[1]:
            memory_entries[0].focus_set()  # Move focus to entry 1
        elif entry == memory_entries[2]:
            memory_entries[1].focus_set()  # Move focus to entry 2
        elif entry == memory_entries[3]:
            memory_entries[2].focus_set()  # Move focus to entry 3
        elif entry == memory_entries[4]:
            memory_entries[3].focus_set()  # Move focus to entry 3
        return 'break'  # Prevent further input

    if event.keysym == "Down":
        if entry == memory_entries[0]:
            memory_entries[1].focus_set()  # Move focus to entry 2
        elif entry == memory_entries[1]:
            memory_entries[2].focus_set()  # Move focus to entry 3
        elif entry == memory_entries[2]:
            memory_entries[3].focus_set()  # Move focus to entry 4
        elif entry == memory_entries[3]:
            memory_entries[4].focus_set()  # Move focus to entry 5
        elif entry == memory_entries[4]:
            memory_entries[0].focus_set()  # Move focus to entry 1
        return 'break'  # Prevent further input

    # Allow only numeric input
    if not event.char.isdigit():
        return 'break'  # Prevent non-numeric input

    # Check if the entry is one of the first two
    if entry in (memory_entries[0], memory_entries[1], memory_entries[3]):
        new_length = len(entry_text) + 1
        entry.config(width=new_length)

        '''# Update the corresponding label
        index = memory_entries.index(entry)  # get the index of this entry
        if index == 0:
            memory_labels[0].config(text=f"Skip first {entry.get()} digits: ")
        else: # index == 1:
            memory_labels[1].config(text=f"Start {entry.get()} digits in: ")''' # dynamically changing the 'X' in the labels as the entry's text
    else:
        # Replace existing digit with new one
        entry.delete(0, tk.END)
        entry.master.focus()  # Remove focus after input
        return 'true'

def validate_on_focus_out(event):
    entry = event.widget
    entry_text = entry.get().lstrip('0')  # Remove leading zeros
    if entry in [memory_entries[2], memory_entries[4]]:
        if entry_text == "" or entry_text == "0":
            entry.delete(0, tk.END)
            entry.insert(0, "1")
            entry.config(width=1)
    elif entry == memory_entries[0]:
        if entry_text == "":
            entry_text = "0"
        entry.delete(0, tk.END)
        entry.insert(0, entry_text)
        entry.config(width=len(entry_text))  # Adjust width to match content
    elif entry == memory_entries[1]:
        if entry_text == "" or int(entry_text) < 3:
            entry_text = "3"
        entry.delete(0, tk.END)
        entry.insert(0, entry_text)
        entry.config(width=len(entry_text))  # Adjust width to match content
    elif entry == memory_entries[3]:
        if entry_text == "" or entry_text == "0":
            entry_text = "1"
        if int(entry_text) > 99:
            entry_text = "99"
        entry.delete(0, tk.END)
        entry.insert(0, entry_text)
        entry.config(width=len(entry_text))  # Adjust width to match content

def toggle_buttons(enabled: bool):
    state = tk.NORMAL if enabled else tk.DISABLED
    bg_color = 'white' if enabled else btn_disabled_colour  # buttons turn (btn_disabled_colour) when disabled
    for btn in arr_digits.values():
        btn.config(state=state, bg=bg_color, activebackground=bg_color)

def run_with_delays(generator):
    global after_id
    try:
        delay = next(generator)  # Get the next delay from the generator
        after_id = root.after(delay, lambda: run_with_delays(generator))  # Schedule next step
    except StopIteration:
        after_id = None
        pass  # Generator is finished

def generator_finished_cleanup():
    toggle_buttons(False)
    for btn in arr_digits.values():
        btn.config(bg=btn_disabled_colour)

####################################################################################################
# Click events
def btn_memory_click():
    btn_memory.config(bg='#FFD700')
    btn_speedrun.config(bg='white')
    frm_settings_memory.grid(row=1, column=0, sticky="nsew")
    frm_settings_memory.tkraise()

def btn_speedrun_click():
    btn_memory.config(bg='white')
    btn_speedrun.config(bg='#FFD700')
    frm_settings_speedrun.grid(row=1, column=0, sticky="nsew")
    frm_settings_speedrun.tkraise()

def btn_reset_click():
    memory_entries[0].delete(0,tk.END)
    memory_entries[0].insert(0, "0")
    memory_entries[0].config(width=1)
    memory_entries[1].delete(0,tk.END)
    memory_entries[1].insert(0, "3")
    memory_entries[1].config(width=1)
    memory_entries[2].delete(0,tk.END)
    memory_entries[2].insert(0, "1")
    memory_entries[3].delete(0,tk.END)
    memory_entries[3].insert(0, "1")
    memory_entries[3].config(width=1)
    memory_entries[4].delete(0,tk.END)
    memory_entries[4].insert(0, "1")

def btn_start_click():
    root.focus_set()
    for entry in memory_entries:
        dummy_event = SimpleNamespace(widget=entry) # converts to "event" parameter before calling function
        validate_on_focus_out(dummy_event)
    frm_numbers.tkraise()
    frm_control_stop.grid(row=2, column=0, sticky="sew")
    frm_control_stop.tkraise()
    run_with_delays(display_pi(True))
    lbl_title.pack_forget()
    lbl_pi.grid(row=0, column=0, sticky="e")

def btn_stop_click():
    global after_id
    if after_id is not None: # cancel the next generator call
        root.after_cancel(after_id)
        after_id = None
    root.focus_set()
    frm_settings.tkraise()
    frm_control_start.grid(row=2, column=0, sticky="sew")
    frm_control_start.tkraise()
    generator_finished_cleanup()
    lbl_pi.grid_forget()
    lbl_title.pack()

####################################################################################################
# Pi sequence section
#   Display sequence
def display_pi(is_called_from_start: bool):    
    global progress_denominator_increment, pi_counter, progress_numerator
    lbl_pi.config(text="", fg='black')
    if is_called_from_start:
        progress_denominator_increment = 0
    count = 0
    new_digit_colour = "#9EDAFF"
    yield_amount = 1000 / int(memory_entries[3].get()) # Delay in display sequence for old repeated digits
    if int(memory_entries[0].get()) == 0:
        sliced_pi = Pi
    else:
        sliced_pi = "".join(islice((d for d in Pi if d.isdigit()), int(memory_entries[0].get()), None)) # Slice the first X amount of digits
    progress_denominator = int(memory_entries[1].get()) + int(memory_entries[2].get()) + progress_denominator_increment
    lbl_progress.config(text="Progress: " + str(count) + "/" + str(progress_denominator))
    yield int(1000 * math.sqrt(yield_amount/1000)) # small delay before starting

    toggle_buttons(False)
    for digit in sliced_pi:
        if count >= progress_denominator - int(memory_entries[2].get()):
            yield_amount = 1000 / int(memory_entries[4].get())
            new_digit_colour = "#fff459" # Now set to yellow for new digits
        if digit.isdigit():  # Only numbers (Makes sure "." doesn't increase the counter)
            if count >= progress_denominator:  
                break  
            count += 1  # Increment AFTER checking limit
        index = arr_btn_texts.index(digit)
        lbl_pi.config(text=lbl_pi.cget("text") + str(arr_digits[index].cget("text")))
        arr_digits[index].config(bg=new_digit_colour)
        lbl_progress.config(text="Progress: " + str(count) + "/" + str(progress_denominator))
        yield int((yield_amount*0.9)) # delay between showing next one
        arr_digits[index].config(bg=btn_disabled_colour)  # Reset the color
        yield int((yield_amount*0.1)) # little delay before next cycle
    toggle_buttons(True)
    lbl_progress.config(text="Progress: 0/" + str(progress_denominator))
    pi_counter = 0
    progress_numerator = 0

#   User press
def digit_click(num):
    if str(arr_digits[num]['state']) == tk.DISABLED: # Exit immediately if the button is disabled
        return
    
    global pi_counter, progress_numerator, progress_denominator_increment, pi_counter_offset
    if int(memory_entries[0].get()) == 0:
        pi_counter_offset = 0
    else:
        pi_counter_offset = int(memory_entries[0].get()) + 1
    if pi_counter == 0:
        lbl_pi.config(text="") # Reset the lbl_pi
    correct_digit = Pi[pi_counter + pi_counter_offset] # correct digit of pi that should be clicked
    progress_denominator = int(memory_entries[1].get()) + progress_denominator_increment + int(memory_entries[2].get())
    arr_digits[arr_btn_texts.index(Pi[pi_counter+pi_counter_offset-1])].config(bg='white') # Change previous button back to white
    lbl_pi.config(text=lbl_pi.cget("text") + str(arr_btn_texts[num]))
    if correct_digit == arr_btn_texts[num]: # Clicked the correct digit
        arr_digits[num].config(bg='lime')
        if correct_digit != ".":
            progress_numerator += 1
        pi_counter += 1
        lbl_progress.config(text="Progress: " + str(progress_numerator) + "/" + str(progress_denominator))
        if progress_numerator == progress_denominator: # End reached
            for btn in (v for k, v in arr_digits.items() if k != num):
                btn.config(state=tk.DISABLED, bg=btn_disabled_colour)
            arr_digits[num].config(state=tk.DISABLED)
            progress_denominator_increment += int(memory_entries[2].get())
            pi_counter = 0
            progress_numerator = 0
            run_with_delays(display_pi(False))
    else: # Clicked the wrong digit        
        lbl_pi.config(fg='red')
        toggle_buttons(False)
        arr_digits[arr_btn_texts.index(correct_digit)].config(bg='#76f597')
        arr_digits[num].config(bg='red')
        for i in range(2):
            yield 1000
            arr_digits[num].config(bg=btn_disabled_colour)
            yield 400
            arr_digits[num].config(bg='red')
        progress_numerator = 0
        progress_denominator_increment = 0
        pi_counter = 0

####################################################################################################
# GUI CREATION
# Create the main window
root = tk.Tk()
root.title("v1.0.2")
root.state('zoomed')
bg_colour = "#f0f0f0" #Can change this around to change all background colours of all GUI
root.config(bg=bg_colour)

# Frames
frm_title = tk.Frame(root, bg=bg_colour)
frm_title.grid(row=0, column=0, sticky="new")
frm_title.columnconfigure(0, weight=1)
frm_numbers = tk.Frame(root, bg=bg_colour)
frm_numbers.grid(row=1, column=0, sticky="nsew")
frm_control_start = tk.Frame(root, bg=bg_colour)
frm_control_start.grid(row=2, column=0, sticky="sew")
frm_control_start.grid_columnconfigure(0, weight=1, uniform="control_start")
frm_control_stop = tk.Frame(root, bg=bg_colour)
#   Settings frames
frm_settings = tk.Frame(root, bg=bg_colour)
frm_settings.grid(row=1, column=0, sticky="nsew")
frm_settings.grid_columnconfigure(0, weight=1)
frm_settings_main = tk.Frame(frm_settings, bg=bg_colour)
frm_settings_main.grid(row=0, column=0, sticky="ew")
frm_settings_memory = tk.Frame(frm_settings, bg=bg_colour)
frm_settings_speedrun = tk.Frame(frm_settings, bg=bg_colour) 
for i in range(2):
    frm_settings_main.grid_columnconfigure(i, weight=1, uniform="main")
    frm_settings_memory.grid_columnconfigure(i, weight=1, uniform="memory_column")
    frm_settings_memory.grid_rowconfigure(i, weight=1, uniform="memory_row")
    frm_settings_speedrun.grid_columnconfigure(i, weight=1, uniform="speedrun_column")
    frm_settings_speedrun.grid_rowconfigure(i, weight=1, uniform="speedrun_row")
    frm_control_stop.grid_columnconfigure(i, weight=1, uniform="control_stop")

# Title Label
lbl_title = tk.Label(frm_title, text="Pi Memory Game", font=("Arial", 35), bg=bg_colour)
lbl_title.pack()

# Pi displayer
lbl_pi = tk.Label(frm_title, font=("Arial", 35), bg=bg_colour, anchor="e")

# Configure the grid layout in the button frame
arr_btn_texts = [
    "7", "8", "9",
    "4", "5", "6",
    "1", "2", "3",
    "0", "."
]
arr_digits = {}
for row in range(4):
    for col in range(3):
        index = row * 3 + col
        if index < len(arr_btn_texts):  # Only create buttons if within range
            btn = tk.Button(frm_numbers, text=arr_btn_texts[index], bg=btn_disabled_colour , font=("Arial", 80))
            btn.bind("<ButtonPress-1>", lambda e, num=index: run_with_delays(digit_click(num))) # fires when the button is PRESSED not when its RELEASED
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            btn.config(state=tk.DISABLED)
            arr_digits[index] = btn
for i in range(3): 
    frm_numbers.columnconfigure(i, weight=1, uniform="numbers")
for i in range(4): 
    frm_numbers.rowconfigure(i, weight=1, uniform="numbers")

# Settings configuration
#   Memory mode
btn_memory = tk.Button(frm_settings_main, text="Memory", font=("Arial", 60), command=btn_memory_click)
btn_memory.grid(row=0, column=0, sticky="ew")
btn_speedrun = tk.Button(frm_settings_main, text="Speedrun", font=("Arial", 60), command=btn_speedrun_click)
btn_speedrun.grid(row=0, column=1, sticky="ew")
#       Info for each entry
info = [
    {"text": "Skip first X digits: ", "initial_value": "0"},            # 1️⃣ Where to start in Pi
    {"text": "Start X digits in: ", "initial_value": "3"},              # 2️⃣ How many digits in the first cycle
    {"text": "Digits to increment: ", "initial_value": "1"},            # 3️⃣ How many new digits are added each round
    {"text": "Old digits speed (digits/sec): ", "initial_value": "1"},  # 4️⃣ Speed of repeated digits
    {"text": "New digits speed (digits/sec): ", "initial_value": "1"}   # 5️⃣ Speed of new added digits
]

memory_entries = []
memory_labels = []

for i, info in enumerate(info):
    label = tk.Label(frm_settings_memory, text=info["text"], font=("Calibri", 40), bg=bg_colour)
    label.grid(row=i, column=0, sticky="e")
    memory_labels.append(label)

    entry = tk.Entry(frm_settings_memory, width=1, bd=2, relief=tk.SUNKEN, font=("Calibri", 40), justify='center')
    entry.grid(row=i, column=1, sticky="w", ipadx=2)
    entry.insert(0, info["initial_value"])
    entry.bind("<Return>", lambda event: entry.master.focus())
    entry.bind("<Key>", ent_validation)
    entry.bind("<FocusOut>", validate_on_focus_out)  # Bind focus out event
    memory_entries.append(entry)

#   Speedrun mode
'''do something here for speedrun'''

#   Reset
frames = [frm_settings_memory, frm_settings_speedrun] # Frames to cycle through to create the buttons
for i, frame in enumerate(frames):
    reset = tk.Button(frame, text='Reset', font=("Arial", 30, "bold"), bg="red", command=btn_reset_click)
    reset.place(x=0, y=7)

# Control
#   Start frame
btn_start = tk.Button(frm_control_start, text="START", bg='#00ff66', font=("Calibri", 30), command=btn_start_click)
btn_start.grid(row=0, column=0, sticky="ew")
#   Stop frame
btn_stop = tk.Button(frm_control_stop, text="STOP", bg='#FF5722', font=("Calibri", 30), command=btn_stop_click)
btn_stop.grid(row=0, column=1, ipadx=55, sticky="e")
lbl_progress = tk.Label(frm_control_stop, font=("Calibri", 49), bg=bg_colour)
lbl_progress.grid(row=0, column=0, sticky="w")

# Expand the main window to fill the screen
root.columnconfigure(0, weight=1)
root.rowconfigure(1, weight=1)
btn_memory_click()

# Pi
pi_raw = """
3.
1415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679
8214808651328230664709384460955058223172535940812848111745028410270193852110555964462294895493038196
4428810975665933446128475648233786783165271201909145648566923460348610454326648213393607260249141273
7245870066063155881748815209209628292540917153643678925903600113305305488204665213841469519415116094
3305727036575959195309218611738193261179310511854807446237996274956735188575272489122793818301194912
9833673362440656643086021394946395224737190702179860943702770539217176293176752384674818467669405132
0005681271452635608277857713427577896091736371787214684409012249534301465495853710507922796892589235
4201995611212902196086403441815981362977477130996051870721134999999837297804995105973173281609631859
5024459455346908302642522308253344685035261931188171010003137838752886587533208381420617177669147303
5982534904287554687311595628638823537875937519577818577805321712268066130019278766111959092164201989""" # 1000 decimal digits of Pi
Pi = pi_raw.replace(" ", "").replace("\n", "")
root.mainloop()