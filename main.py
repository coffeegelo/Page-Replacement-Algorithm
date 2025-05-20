import tkinter as tk
from tkmacosx import Button
import random

def generate_pages():
    global page_reference
    page_reference = [str(random.randint(0, 9)) for _ in range(20)]
    display_reference_startup(page_reference)
    btn_continue.config(state="normal")
    lbl_status.config(text="")

def set_capacity(value):
    entry_capacity.config(state="normal")
    entry_capacity.delete(0, tk.END)
    entry_capacity.insert(0, str(value))
    entry_capacity.config(state="readonly")
    update_button_states(value)

def update_button_states(value):
    if value <= 3:
        btn_down.config(state="disabled")
    else:
        btn_down.config(state="normal")

    if value >= 10:
        btn_up.config(state="disabled")
    else:
        btn_up.config(state="normal")

def increase_capacity():
    current = int(entry_capacity.get())
    if current < 10:
        set_capacity(current + 1)

def decrease_capacity():
    current = int(entry_capacity.get())
    if current > 3:
        set_capacity(current - 1)

def open_simulation():
    global sim_window, frame_steps, lbl_pages, btn_fifo, btn_lru, btn_optimal, window_height, window_width
    startup.withdraw()


    step_width = 35
    frame_height = 40
    base_width = 300
    header_height = 200 

    num_steps = len(page_reference)

     # space for labels and buttons
    window_width = base_width + step_width * (num_steps + 1)
    window_height = header_height + frame_height * 10

    sim_window = tk.Toplevel()
    sim_window.title("Page Replacement Simulator")
    screen_width = sim_window.winfo_screenwidth()
    screen_height = sim_window.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    sim_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # Page Reference Title
    tk.Label(sim_window, text="Page Reference String:", font=("poppins", 16, "bold"), fg="#2c3085").pack(pady=5)

    frame_sim_circles = tk.Frame(sim_window)
    frame_sim_circles.pack()

    for page in page_reference:
        c = tk.Canvas(frame_sim_circles, width=30, height=30, highlightthickness=0)
        c.create_oval(2, 2, 28, 28, fill="#aab1cc", outline="#aab1cc")
        c.create_text(15, 15, text=page, fill="white", font=("poppins", 10, "bold"))
        c.pack(side="left", padx=2)


    # Add FIFO, LRU, Optimal buttons to the simulation window
    frame_buttons = tk.Frame(sim_window,)
    frame_buttons.pack(pady=5)

    btn_fifo = Button(frame_buttons, text="Simulate FIFO", command=lambda: simulate("FIFO", btn_fifo), bg="#2c3085", fg="#f3f4fe", font="poppins")
    btn_lru = Button(frame_buttons, text="Simulate LRU", command=lambda: simulate("LRU", btn_lru), bg="#2c3085", fg="#f3f4fe", font="poppins")
    btn_optimal = Button(frame_buttons, text="Simulate Optimal", command=lambda: simulate("Optimal", btn_optimal),  bg="#2c3085", fg="#f3f4fe", font="poppins")

    btn_fifo.grid(row=0, column=0, padx=5)
    btn_lru.grid(row=0, column=1, padx=5)
    btn_optimal.grid(row=0, column=2, padx=5)

    # Add visualization area for simulation results
    canvas = tk.Canvas(sim_window,)
    scrollbar = tk.Scrollbar(sim_window, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    frame_steps = tk.Frame(canvas,)
    canvas.create_window((0, 0), window=frame_steps, anchor="nw")
    frame_steps.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    # Back button
    btn_back = tk.Button(sim_window, text="← Back", command=go_back)
    btn_back.place(x=10, y=10)
    

    simulate("FIFO", btn_fifo)

def go_back():
    sim_window.destroy()
    startup.deiconify()
    display_reference_startup(page_reference)

def fifo(pages, capacity):
    memory = []
    faults = 0
    steps = []
    index = 0
    for page in pages:
        if page not in memory:
            if len(memory) < capacity:
                memory.append(page)
            else:
                memory[index] = page
                index = (index + 1) % capacity
            faults += 1
        steps.append(list(memory))
    return faults, steps

def lru(pages, capacity):
    memory = []
    faults = 0
    steps = []
    recent = []
    for page in pages:
        if page not in memory:
            if len(memory) < capacity:
                memory.append(page)
            else:
                lru_index = memory.index(recent[0])
                memory[lru_index] = page
                recent.pop(0)
            faults += 1
        else:
            recent.remove(page)
        recent.append(page)
        steps.append(list(memory))
    return faults, steps

def optimal(pages, capacity):
    memory = []
    faults = 0
    steps = []
    for i in range(len(pages)):
        page = pages[i]
        if page not in memory:
            if len(memory) < capacity:
                memory.append(page)
            else:
                future = pages[i+1:]
                index_to_replace = -1
                farthest = -1
                for j in range(len(memory)):
                    if memory[j] not in future:
                        index_to_replace = j
                        break
                    else:
                        next_use = future.index(memory[j])
                        if next_use > farthest:
                            farthest = next_use
                            index_to_replace = j
                memory[index_to_replace] = page
            faults += 1
        steps.append(list(memory))
    return faults, steps

def display_steps(algorithm, faults, steps, capacity):
    for widget in frame_steps.winfo_children():
        widget.destroy()

    tk.Label(frame_steps, text=f"{algorithm} - Page Faults: {faults}", font=("Poppins", 24, "bold"), fg="#2c3085").grid(row=0, column=0, columnspan=len(steps)+1, pady=10)

    for i in range(len(steps)):
        tk.Label(frame_steps, text=f"S{i+1:2}", width=6, anchor="center", font=("poppins", 9, "bold"), fg="#2c3085").grid(row=1, column=i+1, padx=2)

    previous_memory = []
    for j in range(10):
        tk.Label(frame_steps, text=f"Frame {j+1}", width=10, anchor="w", font=("poppins", 9, "bold"), fg="#2c3085").grid(row=j+2, column=0, padx=5)

    for i, mem in enumerate(steps):
        fault = mem != previous_memory
        changed_frames = []
        if i > 0:
            prev_mem = steps[i-1]
            for j in range(capacity):
                old_val = prev_mem[j] if j < len(prev_mem) else None
                new_val = mem[j] if j < len(mem) else None
                changed_frames.append(new_val != old_val)
        else:
            changed_frames = [True] * capacity if fault else [False] * capacity

        previous_memory = mem.copy()

        for j in range(10):
            val = mem[j] if j < len(mem) else ""
            canvas = tk.Canvas(frame_steps, width=30, height=30, highlightthickness=0,)
            canvas.grid(row=j+2, column=i+1, padx=2, pady=2)

            if j >= capacity:
                canvas.create_oval(2, 2, 28, 28, fill="#81869d", outline="#81869d", width=1)
            elif val == "":
                canvas.create_oval(2, 2, 28, 28, fill="#f3f4fe", outline="#f3f4fe", width=1)
               
            elif fault and changed_frames[j]:
                canvas.create_oval(2, 2, 28, 28, fill="#2c3085", width=1, outline="#2c3085")
                canvas.create_text(15, 15, text=val, fill="#f8f9fc", font=("poppins", 10, "bold"))
            elif fault:
                canvas.create_oval(2, 2, 28, 28, fill="#f3f4fe", outline="#f3f4fe", width=1)
                canvas.create_text(15, 15, text=val, fill="#2c3085", font=("poppins", 10, "bold"))
            else:
                canvas.create_oval(2, 2, 28, 28, fill="#aab1cc", outline="#aab1cc", width=1)
                canvas.create_text(15, 15, text=val, fill="#f8f9fc", font=("poppins", 10))

    tk.Label(frame_steps, text="Page Fault?", font=("poppins", 9, "bold"), fg="#2c3085").grid(row=10+2, column=0, padx=5, pady=5)
    previous_memory = []
    for i, mem in enumerate(steps):
        fault = mem != previous_memory
        symbol = "O" if fault else "X"
        color = "#2c3085" if fault else "#aab1cc"
        tk.Label(frame_steps, text=symbol, fg=color, font=("poppins", 12, "bold")).grid(row=10+2, column=i+1)
        previous_memory = mem.copy()

def simulate(algorithm, clicked_button):
    capacity = int(entry_capacity.get())

    if algorithm == "FIFO":
        faults, steps = fifo(page_reference, capacity)
    elif algorithm == "LRU":
        faults, steps = lru(page_reference, capacity)
    else:
        faults, steps = optimal(page_reference, capacity)

    for btn in [btn_fifo, btn_lru, btn_optimal]:
        btn.config(state="normal")
    clicked_button.config(state="disabled")
    display_steps(algorithm, faults, steps, capacity)

def display_reference_startup(pages):
    for widget in frame_page_circles.winfo_children():
        widget.destroy()

    total_width = len(pages) * 34  # 30px circle + 4px padding
    canvas_container.config(width=total_width)

    for page in pages:
        c = tk.Canvas(frame_page_circles, width=30, height=30, highlightthickness=0)
        c.create_oval(2, 2, 28, 28, fill="#aab1cc", outline="#aab1cc")
        c.create_text(15, 15, text=page, fill="white", font=("poppins", 10, "bold"))
        c.pack(side="left", padx=2)


# ---- Startup Window ----
startup = tk.Tk()
startup.title("Startup")
screen_width = startup.winfo_screenwidth()
screen_height = startup.winfo_screenheight()
window_width = 700
window_height = 350
x = (screen_width // 2) - (window_width // 2)
y = (screen_height // 2) - (window_height // 2)
startup.geometry(f"{window_width}x{window_height}+{x}+{y}")
startup.geometry("700x350")


tk.Label(startup, text="Page Fault Simulator", font=("Poppins", 20, "bold"), fg="#2c3085").pack(pady=10)
tk.Label(startup, text="Number of Frames (3–10):", font="poppins", fg="#2c3085").pack(pady=5)

frame_control = tk.Frame(startup,)
frame_control.pack()


entry_capacity = tk.Entry(frame_control, width=5, justify="center")
entry_capacity.insert(0, "3")
entry_capacity.config(state="readonly")
entry_capacity.grid(row=0, column=1)

btn_up = Button(frame_control, text="▲", command=increase_capacity, bg="#aab1cc",fg="#2c3085")
btn_up.grid(row=0, column=2, padx=2)

btn_down = Button(frame_control, text="▼", command=decrease_capacity, bg="#aab1cc",fg="#2c3085")
btn_down.grid(row=0, column=0, padx=2)

update_button_states(3)

lbl_status = tk.Label(startup, text="", fg="red",)
lbl_status.pack()

# Reference String Display  
frame_page_reference = tk.Frame(startup)
frame_page_reference.pack(pady=5, fill="x")

tk.Label(frame_page_reference, text="Page Reference String:", font="poppins", fg="#2c3085").pack()

btn_generate = Button(startup, text="Randomize", command=generate_pages, bg="#aab1cc",fg="#2c3085", font="poppins")
btn_generate.pack(pady=10)

canvas_container = tk.Canvas(frame_page_reference, highlightthickness=0, height=40)
canvas_container.pack(fill="x", padx=10)

frame_page_circles = tk.Frame(canvas_container)
canvas_container.create_window((0, 0), window=frame_page_circles, anchor="nw")

btn_continue = Button(startup, text="Continue", command=open_simulation, bg="#2c3085", fg="white", font="poppins")
btn_continue.pack(pady=5)

# 🔁 Generate reference on launch
generate_pages()

startup.mainloop()
