import tkinter as tk
import math

class IOSCalculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("iOS Style Calculator")
        self.config(bg="black")
        self.resizable(False, False) 
        
        self.expression = "" 
        self.last_was_calculation = False 

        self.display = tk.Entry(
            self, font=("Helvetica", 36), bg="black", fg="white",
            bd=0, justify="right", insertbackground="white", 
            readonlybackground="black"
        )
        self.display.insert(0, "0")
        self.display.grid(row=0, column=0, columnspan=4, pady=(20, 10), padx=10, sticky="nsew")

        self.create_buttons()

    def create_buttons(self):
        btn_style = {
            "font": ("Helvetica", 22, "bold"),
            "bd": 0,
            "relief": "flat",
            "height": 2,
            "activebackground": "#666666", 
            "activeforeground": "white"
        }

        buttons = [
            ("AC", 1, 0, "#a5a5a5", "black", lambda: self.clear()),
            ("⌫", 1, 1, "#a5a5a5", "black", lambda: self.backspace()), 
            ("+/-", 1, 2, "#a5a5a5", "black", lambda: self.change_sign()), 
            ("÷", 1, 3, "#ff9f0a", "white", lambda: self.append_operator("/")),

            ("7", 2, 0, "#333333", "white", lambda: self.append_digit("7")),
            ("8", 2, 1, "#333333", "white", lambda: self.append_digit("8")),
            ("9", 2, 2, "#333333", "white", lambda: self.append_digit("9")),
            ("×", 2, 3, "#ff9f0a", "white", lambda: self.append_operator("*")),

            ("4", 3, 0, "#333333", "white", lambda: self.append_digit("4")),
            ("5", 3, 1, "#333333", "white", lambda: self.append_digit("5")),
            ("6", 3, 2, "#333333", "white", lambda: self.append_digit("6")),
            ("−", 3, 3, "#ff9f0a", "white", lambda: self.append_operator("-")),

            ("1", 4, 0, "#333333", "white", lambda: self.append_digit("1")),
            ("2", 4, 1, "#333333", "white", lambda: self.append_digit("2")),
            ("3", 4, 2, "#333333", "white", lambda: self.append_digit("3")),
            ("+", 4, 3, "#ff9f0a", "white", lambda: self.append_operator("+")),

            ("0", 5, 0, "#333333", "white", lambda: self.append_digit("0")),
            (".", 5, 2, "#333333", "white", lambda: self.append_digit(".")),
            ("=", 5, 3, "#ff9f0a", "white", lambda: self.calculate())
        ]

        for (text, row, col, bg, fg, cmd) in buttons:
            if text == "0":
                btn = tk.Button(self, text=text, bg=bg, fg=fg, command=cmd, **btn_style, width=10)
                btn.grid(row=row, column=0, columnspan=2, padx=(5, 5), pady=5, sticky="nsew")
            else:
                btn = tk.Button(self, text=text, bg=bg, fg=fg, command=cmd, **btn_style)
                btn.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

        
        for i in range(6):
            self.rowconfigure(i, weight=1)
        for j in range(4):
            self.columnconfigure(j, weight=1)

    def append_digit(self, value):
        current_text = self.display.get()
        
        if self.last_was_calculation or "Error" in current_text:
            self.clear()
            current_text = "0"
            self.last_was_calculation = False
            
        if current_text == "0" and value != ".":
            self.display.delete(0, tk.END)
            self.display.insert(0, value)
            return
        
        if value == '.':
            operators = ['+', '−', '*', '/']
            segment = current_text
            for op in operators:
                if op in segment:
                    segment = segment.split(op)[-1]
                    
            if '.' in segment:
                return 

        self.display.insert(tk.END, value)
        
    def append_operator(self, value):
        if self.last_was_calculation:
            self.last_was_calculation = False
            
        current_text = self.display.get()
        
        if current_text == "0" or "Error" in current_text:
            return
            
        last_char = current_text[-1] if current_text else ''
        if last_char in ['+', '-', '*', '/']:
            self.display.delete(len(current_text) - 1, tk.END)

        self.display.insert(tk.END, value)


    def clear(self):
        self.display.delete(0, tk.END)
        self.display.insert(0, "0")
        self.last_was_calculation = False

    def backspace(self):
        text = self.display.get()
        if len(text) > 1 and not self.last_was_calculation:
            self.display.delete(len(text) - 1)
        elif self.last_was_calculation:
             self.clear()
        else:
            self.display.delete(0, tk.END)
            self.display.insert(0, "0")
            
        self.last_was_calculation = False
            
    def change_sign(self):
        current_text = self.display.get()
        self.last_was_calculation = False

        try:
            if all(op not in current_text for op in ['+', '−', '×', '÷']) and current_text != "0":
                if current_text[0] != '-':
                    self.display.delete(0, tk.END)
                    self.display.insert(0, '-' + current_text)
                elif current_text[0] == '-':
                    self.display.delete(0, tk.END)
                    self.display.insert(0, current_text[1:])
        except Exception:
            pass 

    def calculate(self):
        current_expression = self.display.get()
        
        if "Error" in current_expression or self.last_was_calculation:
            return

        try:
            expression = current_expression.replace("×", "*").replace("÷", "/").replace("−", "-")
            
            result = eval(expression, {"__builtins__": None}, {})
            
            if isinstance(result, (int, float)) and abs(result - round(result)) < 1e-9: 
                result = int(round(result))
            
            result_str = str(result)
            
            if len(result_str) > 15 and isinstance(result, float):
                 result_str = f"{result:.10e}" 

            self.display.delete(0, tk.END)
            self.display.insert(0, result_str)
            
            self.last_was_calculation = True

        except ZeroDivisionError:
            self.display.delete(0, tk.END)
            self.display.insert(0, "Error: Divide by Zero")
            self.last_was_calculation = False
        except (TypeError, SyntaxError):
            self.display.delete(0, tk.END)
            self.display.insert(0, "Error: Invalid Expression")
            self.last_was_calculation = False
        except Exception:
            self.display.delete(0, tk.END)
            self.display.insert(0, "Error")
            self.last_was_calculation = False


if __name__ == "__main__":
    app = IOSCalculator()
    app.mainloop()