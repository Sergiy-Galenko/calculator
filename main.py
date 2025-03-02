import customtkinter as ctk
import tkinter as tk
import math
import fractions
import csv
import os
import json
import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

try:
    from fpdf import FPDF
except ImportError:
    FPDF = None

# Стандартні налаштування за замовчуванням
DEFAULT_SETTINGS = {
    "theme": "light",           # або "dark"
    "font_size": 18,
    "hotkeys": {
        "C": "Escape",
        "⌫": "BackSpace",
        "=": "Return"
    }
}

SETTINGS_FILE = "settings.json"

# Головний клас додатку
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Мульти-Функціональний Додаток")
        self.geometry("1100x750")
        self.settings = self.load_settings()
        
        container = ctk.CTkFrame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        self.frames = {}
        for F in (MainMenu, SimpleCalc, AdvancedCalc, Converter, GraphPlot):
            frame = F(container, self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame("MainMenu")
        self.bind_hotkeys()
    
    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()
        if hasattr(frame, "apply_settings"):
            frame.apply_settings(self.settings)
    
    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        return DEFAULT_SETTINGS.copy()
    
    def save_settings(self):
        with open(SETTINGS_FILE, "w") as f:
            json.dump(self.settings, f, indent=4)
    
    def update_settings(self, new_settings):
        self.settings.update(new_settings)
        self.save_settings()
        # Оновлюємо інтерфейс усіх фреймів, якщо підтримують apply_settings
        for frame in self.frames.values():
            if hasattr(frame, "apply_settings"):
                frame.apply_settings(self.settings)
        self.bind_hotkeys()
    
    def bind_hotkeys(self):
        # Прив'язка гарячих клавіш (stub‑варіант; розширити за потребою)
        for key, binding in self.settings.get("hotkeys", {}).items():
            self.bind(f"<{binding}>", lambda event, k=key: self.on_hotkey(k))
    
    def on_hotkey(self, key):
        # Пробуємо передати гарячу клавішу у поточний фрейм, якщо він підтримує on_hotkey
        current = self.focus_get()
        frame = self.frames.get(current)
        # stub: просто друкуємо натискання
        print(f"Hotkey {key} pressed.")

# Головне меню
class MainMenu(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        label = ctk.CTkLabel(self, text="Виберіть режим", font=("Helvetica", 24))
        label.pack(pady=20)
        
        btn_simple = ctk.CTkButton(self, text="Звичайний калькулятор", font=("Helvetica", 18),
                                   command=lambda: controller.show_frame("SimpleCalc"))
        btn_simple.pack(pady=10, padx=20, fill="x")
        
        btn_advanced = ctk.CTkButton(self, text="Складний калькулятор", font=("Helvetica", 18),
                                     command=lambda: controller.show_frame("AdvancedCalc"))
        btn_advanced.pack(pady=10, padx=20, fill="x")
        
        btn_converter = ctk.CTkButton(self, text="Конвертор", font=("Helvetica", 18),
                                      command=lambda: controller.show_frame("Converter"))
        btn_converter.pack(pady=10, padx=20, fill="x")
        
        btn_graph = ctk.CTkButton(self, text="Графіки функцій", font=("Helvetica", 18),
                                  command=lambda: controller.show_frame("GraphPlot"))
        btn_graph.pack(pady=10, padx=20, fill="x")
        
        btn_help = ctk.CTkButton(self, text="Довідка", font=("Helvetica", 18),
                                 command=self.open_help)
        btn_help.pack(pady=10, padx=20, fill="x")
        
        btn_settings = ctk.CTkButton(self, text="Налаштування інтерфейсу", font=("Helvetica", 18),
                                     command=self.open_settings)
        btn_settings.pack(pady=10, padx=20, fill="x")
    
    def open_help(self):
        HelpWindow(self)
    
    def open_settings(self):
        SettingsWindow(self.controller)

# Вікно налаштувань
class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller
        self.title("Налаштування інтерфейсу")
        self.geometry("500x400")
        
        # Варіанти теми
        theme_label = ctk.CTkLabel(self, text="Оберіть тему:", font=("Helvetica", 16))
        theme_label.pack(pady=(20,5))
        self.theme_var = tk.StringVar(value=self.controller.settings.get("theme", "light"))
        theme_menu = ctk.CTkOptionMenu(self, values=["light", "dark"], variable=self.theme_var)
        theme_menu.pack(pady=5)
        
        # Розмір шрифту
        font_label = ctk.CTkLabel(self, text="Розмір шрифту:", font=("Helvetica", 16))
        font_label.pack(pady=(20,5))
        self.font_size_slider = ctk.CTkSlider(self, from_=12, to=36, number_of_steps=24,
                                              command=self.slider_callback)
        self.font_size_slider.set(self.controller.settings.get("font_size", 18))
        self.font_size_slider.pack(pady=5)
        self.font_size_value = ctk.CTkLabel(self, text=f"{int(self.font_size_slider.get())}", font=("Helvetica", 16))
        self.font_size_value.pack(pady=5)
        
        # Гарячі клавіші (stub)
        hotkeys_label = ctk.CTkLabel(self, text="Гарячі клавіші (формат: Кнопка:Binding)", font=("Helvetica", 16))
        hotkeys_label.pack(pady=(20,5))
        self.hotkeys_entry = ctk.CTkEntry(self, width=400, font=("Helvetica", 16))
        # Відображаємо поточні налаштування у вигляді рядка
        hotkeys_str = ", ".join([f"{k}:{v}" for k, v in self.controller.settings.get("hotkeys", {}).items()])
        self.hotkeys_entry.insert(0, hotkeys_str)
        self.hotkeys_entry.pack(pady=5)
        
        save_btn = ctk.CTkButton(self, text="Зберегти", font=("Helvetica", 16), command=self.save_settings)
        save_btn.pack(pady=20)
    
    def slider_callback(self, value):
        self.font_size_value.configure(text=f"{int(float(value))}")
    
    def save_settings(self):
        new_settings = {
            "theme": self.theme_var.get(),
            "font_size": int(self.font_size_slider.get()),
            # Просте парсування гарячих клавіш; формат: "C:Escape, ⌫:BackSpace, =:Return"
            "hotkeys": {}
        }
        hotkeys_raw = self.hotkeys_entry.get()
        for pair in hotkeys_raw.split(","):
            if ":" in pair:
                key, binding = pair.split(":")
                new_settings["hotkeys"][key.strip()] = binding.strip()
        self.controller.update_settings(new_settings)
        self.destroy()

# Простий калькулятор
class SimpleCalc(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.expression = ""
        
        self.display_var = tk.StringVar()
        self.display_entry = ctk.CTkEntry(self, textvariable=self.display_var,
                                          font=("Helvetica", self.controller.settings.get("font_size", 18)),
                                          justify="right")
        self.display_entry.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky="ew")
        
        buttons = [
            ['C', '⌫', '', ''],
            ['7', '8', '9', '/'],
            ['4', '5', '6', '*'],
            ['1', '2', '3', '-'],
            ['0', '.', '=', '+']
        ]
        
        for i, row in enumerate(buttons, start=1):
            for j, text in enumerate(row):
                if text:
                    btn = ctk.CTkButton(self, text=text,
                                          font=("Helvetica", self.controller.settings.get("font_size", 18)),
                                          corner_radius=20,
                                          command=lambda t=text: self.on_button_click(t))
                    btn.grid(row=i, column=j, padx=5, pady=5, sticky="nsew")
                self.grid_columnconfigure(j, weight=1)
            self.grid_rowconfigure(i, weight=1)
        
        back_btn = ctk.CTkButton(self, text="Назад",
                                 font=("Helvetica", self.controller.settings.get("font_size", 18)),
                                 command=lambda: controller.show_frame("MainMenu"))
        back_btn.grid(row=len(buttons)+1, column=0, columnspan=4, pady=10, padx=10, sticky="ew")
    
    def on_button_click(self, text):
        try:
            if text == 'C':
                self.expression = ""
            elif text == '⌫':
                self.expression = self.expression[:-1]
            elif text == '=':
                self.expression = str(eval(self.expression))
            else:
                self.expression += text
            self.display_var.set(self.expression)
        except Exception as e:
            self.expression = ""
            self.display_var.set("Error")
    
    def apply_settings(self, settings):
        # Оновлення шрифту дисплея
        self.display_entry.configure(font=("Helvetica", settings.get("font_size", 18)))

# Складний калькулятор з розширеною історією
class AdvancedCalc(ctk.CTkFrame):
    HISTORY_FILE = "advanced_history.txt"
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.expression = ""
        self.last_result = ""
        self.memory = 0
        self.history_list = []  # буде зберігати кортежі: (timestamp, entry_text)
        self.history_sort_ascending = True
        self.load_history()
        
        # Розбиття на калькулятор і історію
        self.calc_frame = ctk.CTkFrame(self)
        self.calc_frame.grid(row=0, column=0, sticky="nsew", padx=(10,5), pady=10)
        self.history_frame = ctk.CTkFrame(self, width=300)
        self.history_frame.grid(row=0, column=1, sticky="nsew", padx=(5,10), pady=10)
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.display_var = tk.StringVar()
        self.display_entry = ctk.CTkEntry(self.calc_frame, textvariable=self.display_var,
                                          font=("Helvetica", self.controller.settings.get("font_size", 18)),
                                          justify="right")
        self.display_entry.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky="ew")
        
        buttons = [
            ['C', '⌫', 'MR', 'MC'],
            ['7', '8', '9', '/'],
            ['4', '5', '6', '*'],
            ['1', '2', '3', '-'],
            ['0', '.', '=', '+'],
            ['sin', 'cos', 'tan', '√'],
            ['log', 'ln', '^', 'π'],
            ['1/x', 'frac', '%', '('],
            [')', 'Ans', 'Copy', 'Save'],
            ['M+', 'M-', '', '']
        ]
        
        for i, row in enumerate(buttons, start=1):
            for j, text in enumerate(row):
                if text:
                    btn = ctk.CTkButton(self.calc_frame, text=text,
                                          font=("Helvetica", self.controller.settings.get("font_size", 18)),
                                          corner_radius=20,
                                          command=lambda t=text: self.on_button_click(t))
                    btn.grid(row=i, column=j, padx=5, pady=5, sticky="nsew")
                self.calc_frame.grid_columnconfigure(j, weight=1)
            self.calc_frame.grid_rowconfigure(i, weight=1)
        
        # Область історії з елементами керування
        top_history = ctk.CTkFrame(self.history_frame)
        top_history.pack(fill="x", padx=5, pady=5)
        
        self.search_var = tk.StringVar()
        search_entry = ctk.CTkEntry(top_history, textvariable=self.search_var,
                                    placeholder_text="Пошук", font=("Helvetica", 12))
        search_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        search_btn = ctk.CTkButton(top_history, text="Пошук", font=("Helvetica", 12),
                                   command=self.search_history)
        search_btn.grid(row=0, column=1, padx=5, pady=5)
        show_all_btn = ctk.CTkButton(top_history, text="Показати всі", font=("Helvetica", 12),
                                     command=self.show_all_history)
        show_all_btn.grid(row=0, column=2, padx=5, pady=5)
        top_history.grid_columnconfigure(0, weight=1)
        
        control_frame = ctk.CTkFrame(self.history_frame)
        control_frame.pack(fill="x", padx=5, pady=5)
        clear_btn = ctk.CTkButton(control_frame, text="Очистити", font=("Helvetica", 12),
                                  command=self.clear_history)
        clear_btn.pack(side="left", padx=5)
        export_csv_btn = ctk.CTkButton(control_frame, text="Експорт CSV", font=("Helvetica", 12),
                                       command=self.export_history_csv)
        export_csv_btn.pack(side="left", padx=5)
        export_pdf_btn = ctk.CTkButton(control_frame, text="Експорт PDF", font=("Helvetica", 12),
                                       command=self.export_history_pdf)
        export_pdf_btn.pack(side="left", padx=5)
        sort_btn = ctk.CTkButton(control_frame, text="Сортувати", font=("Helvetica", 12),
                                 command=self.sort_history)
        sort_btn.pack(side="left", padx=5)
        plot_history_btn = ctk.CTkButton(control_frame, text="Візуалізувати історію",
                                         font=("Helvetica", 12), command=self.plot_history)
        plot_history_btn.pack(side="left", padx=5)
        
        self.history_text = ctk.CTkTextbox(self.history_frame, font=("Helvetica", 12), wrap="word")
        self.history_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.update_history_text()
        
        back_btn = ctk.CTkButton(self, text="Назад",
                                 font=("Helvetica", self.controller.settings.get("font_size", 18)),
                                 command=lambda: self.controller.show_frame("MainMenu"))
        back_btn.grid(row=1, column=0, columnspan=2, pady=10, padx=10, sticky="ew")
    
    def on_button_click(self, text):
        try:
            if text == 'C':
                self.expression = ""
            elif text == '⌫':
                self.expression = self.expression[:-1]
            elif text == '=':
                result = str(eval(self.expression))
                self.last_result = result
                self.add_history(self.expression, result)
                self.expression = result
            elif text == 'sin':
                result = math.sin(math.radians(eval(self.expression)))
                self.last_result = result
                self.add_history(f"sin({self.expression})", result)
                self.expression = str(result)
            elif text == 'cos':
                result = math.cos(math.radians(eval(self.expression)))
                self.last_result = result
                self.add_history(f"cos({self.expression})", result)
                self.expression = str(result)
            elif text == 'tan':
                result = math.tan(math.radians(eval(self.expression)))
                self.last_result = result
                self.add_history(f"tan({self.expression})", result)
                self.expression = str(result)
            elif text == '√':
                result = math.sqrt(eval(self.expression))
                self.last_result = result
                self.add_history(f"√({self.expression})", result)
                self.expression = str(result)
            elif text == 'log':
                result = math.log10(eval(self.expression))
                self.last_result = result
                self.add_history(f"log({self.expression})", result)
                self.expression = str(result)
            elif text == 'ln':
                result = math.log(eval(self.expression))
                self.last_result = result
                self.add_history(f"ln({self.expression})", result)
                self.expression = str(result)
            elif text == '^':
                self.expression += "**"
            elif text == 'π':
                self.expression += str(math.pi)
            elif text == '1/x':
                result = 1 / eval(self.expression)
                self.last_result = result
                self.add_history(f"1/({self.expression})", result)
                self.expression = str(result)
            elif text == 'frac':
                result = fractions.Fraction(eval(self.expression)).limit_denominator()
                self.last_result = result
                self.add_history(f"frac({self.expression})", result)
                self.expression = str(result)
            elif text == '%':
                result = eval(self.expression) / 100
                self.last_result = result
                self.add_history(f"percent({self.expression})", result)
                self.expression = str(result)
            elif text in ('(', ')'):
                self.expression += text
            elif text == 'MR':
                self.expression = str(self.memory)
            elif text == 'MC':
                self.memory = 0
            elif text == 'M+':
                self.memory += eval(self.expression)
            elif text == 'M-':
                self.memory -= eval(self.expression)
            elif text == 'Ans':
                self.expression += str(self.last_result)
            elif text == 'Copy':
                self.controller.clipboard_clear()
                self.controller.clipboard_append(self.display_var.get())
            elif text == 'Save':
                with open("advanced_history_export.txt", "w") as f:
                    f.write("".join([entry for _, entry in self.history_list]))
            else:
                self.expression += text
            self.display_var.set(self.expression)
        except Exception as e:
            self.expression = ""
            self.display_var.set("Error")
    
    def add_history(self, expr, result):
        ts = datetime.datetime.now()
        ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")
        entry_text = f"{ts_str}: {expr} = {result}\n"
        self.history_list.append((ts, entry_text))
        self.append_history_to_file(entry_text)
        self.update_history_text()
    
    def update_history_text(self, filter_text=""):
        self.history_text.configure(state="normal")
        self.history_text.delete("1.0", "end")
        # Сортуємо історію відповідно до налаштування
        sorted_history = sorted(self.history_list, key=lambda x: x[0], reverse=not self.history_sort_ascending)
        for ts, entry_text in sorted_history:
            if filter_text.lower() in entry_text.lower():
                self.history_text.insert("end", entry_text)
        self.history_text.configure(state="disabled")
    
    def search_history(self):
        search_term = self.search_var.get()
        self.update_history_text(filter_text=search_term)
    
    def show_all_history(self):
        self.search_var.set("")
        self.update_history_text()
    
    def clear_history(self):
        self.history_list = []
        self.update_history_text()
        if os.path.exists(self.HISTORY_FILE):
            os.remove(self.HISTORY_FILE)
    
    def load_history(self):
        if os.path.exists(self.HISTORY_FILE):
            with open(self.HISTORY_FILE, "r") as f:
                for line in f:
                    try:
                        # Припускаємо, що кожен рядок починається з timestamp
                        ts_str, rest = line.split(":", 1)
                        ts = datetime.datetime.strptime(ts_str, "%Y-%m-%d %H%M%S")
                    except:
                        ts = datetime.datetime.now()
                    self.history_list.append((ts, line))
    
    def append_history_to_file(self, entry):
        with open(self.HISTORY_FILE, "a") as f:
            f.write(entry)
    
    def export_history_csv(self):
        with open("advanced_history.csv", "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Обчислення"])
            for _, entry in self.history_list:
                writer.writerow([entry.strip()])
    
    def export_history_pdf(self):
        if FPDF is None:
            print("Для PDF експорту встановіть fpdf (pip install fpdf)")
            return
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        for _, entry in self.history_list:
            pdf.cell(200, 10, txt=entry.strip(), ln=True)
        pdf.output("advanced_history.pdf")
    
    def sort_history(self):
        self.history_sort_ascending = not self.history_sort_ascending
        self.update_history_text()
    
    def plot_history(self):
        # Побудова діаграми: кількість обчислень за датою
        date_counts = {}
        for ts, _ in self.history_list:
            d = ts.date()
            date_counts[d] = date_counts.get(d, 0) + 1
        if not date_counts:
            return
        dates = sorted(date_counts.keys())
        counts = [date_counts[d] for d in dates]
        plt.figure(figsize=(8,4))
        plt.bar([d.strftime("%Y-%m-%d") for d in dates], counts)
        plt.xticks(rotation=45)
        plt.xlabel("Дата")
        plt.ylabel("Кількість обчислень")
        plt.title("Історія обчислень")
        plt.tight_layout()
        plt.show()
    
    def apply_settings(self, settings):
        # Оновлення шрифту дисплею та історії
        font = ("Helvetica", settings.get("font_size", 18))
        self.display_entry.configure(font=font)
        self.history_text.configure(font=("Helvetica", 12))

# Розширений конвертор
class Converter(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Категорії та одиниці (додано Валюта)
        self.categories = {
            "Довжина": {
                "Метри": 1,
                "Кілометри": 1000,
                "Сантиметри": 0.01,
                "Міліметри": 0.001,
                "Дюйми": 0.0254,
                "Фути": 0.3048
            },
            "Об'єм": {
                "Літри": 1,
                "Мілілітри": 0.001,
                "Кубічні метри": 1000,
                "Галони": 3.78541
            },
            "Температура": ["Цельсій", "Фаренгейт", "Кельвін"],
            "Вага": {
                "Кілограми": 1,
                "Грами": 0.001,
                "Фунти": 0.453592,
                "Унції": 0.0283495
            },
            "Швидкість": {
                "Км/год": 1,
                "Миль/год": 1.60934,
                "М/с": 3.6
            },
            "Енергія": {
                "Джоули": 1,
                "Кілоджоулі": 1000,
                "Калорії": 4.184
            },
            "Тиск": {
                "Па": 1,
                "кПа": 1000,
                "Атмосфери": 101325,
                "Бар": 100000
            },
            "Валюта": {
                "USD": 1,
                "EUR": 0.85,
                "UAH": 27,
                "GBP": 0.75
            }
        }
        
        self.selected_category = tk.StringVar(value="Довжина")
        self.input_value = tk.StringVar()
        self.result_value = tk.StringVar(value="Результат")
        
        cat_label = ctk.CTkLabel(self, text="Категорія:", font=("Helvetica", 16))
        cat_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.cat_menu = ctk.CTkOptionMenu(self, values=list(self.categories.keys()),
                                          variable=self.selected_category, command=self.update_units)
        self.cat_menu.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        from_label = ctk.CTkLabel(self, text="Від:", font=("Helvetica", 16))
        from_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.from_unit = tk.StringVar()
        self.from_menu = ctk.CTkOptionMenu(self, values=[], variable=self.from_unit)
        self.from_menu.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        
        to_label = ctk.CTkLabel(self, text="До:", font=("Helvetica", 16))
        to_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.to_unit = tk.StringVar()
        self.to_menu = ctk.CTkOptionMenu(self, values=[], variable=self.to_unit)
        self.to_menu.grid(row=2, column=1, padx=10, pady=10, sticky="ew")
        
        value_label = ctk.CTkLabel(self, text="Значення:", font=("Helvetica", 16))
        value_label.grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.value_entry = ctk.CTkEntry(self, textvariable=self.input_value, font=("Helvetica", 16))
        self.value_entry.grid(row=3, column=1, padx=10, pady=10, sticky="ew")
        
        convert_btn = ctk.CTkButton(self, text="Конвертувати", font=("Helvetica", 16), command=self.convert)
        convert_btn.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        # Кнопка для оновлення валютних курсів (тільки для категорії Валюта)
        self.update_rates_btn = ctk.CTkButton(self, text="Оновити курси", font=("Helvetica", 16),
                                              command=self.update_currency_rates)
        self.update_rates_btn.grid(row=5, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        
        result_label = ctk.CTkLabel(self, textvariable=self.result_value, font=("Helvetica", 18))
        result_label.grid(row=6, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        custom_btn = ctk.CTkButton(self, text="Налаштувати одиниці", font=("Helvetica", 16),
                                   command=self.custom_units)
        custom_btn.grid(row=7, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        back_btn = ctk.CTkButton(self, text="Назад", font=("Helvetica", 16),
                                 command=lambda: self.controller.show_frame("MainMenu"))
        back_btn.grid(row=8, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        self.update_units(self.selected_category.get())
    
    def update_units(self, choice):
        cat = self.categories[choice]
        if choice == "Температура":
            units = cat  # Список температурних одиниць
        else:
            units = list(cat.keys())
        self.from_menu.configure(values=units)
        self.to_menu.configure(values=units)
        self.from_unit.set(units[0])
        self.to_unit.set(units[1] if len(units) > 1 else units[0])
    
    def convert(self):
        try:
            value = float(self.input_value.get())
            cat = self.selected_category.get()
            if cat == "Температура":
                from_unit = self.from_unit.get()
                to_unit = self.to_unit.get()
                if from_unit == "Цельсій":
                    base = value
                elif from_unit == "Фаренгейт":
                    base = (value - 32) * 5/9
                elif from_unit == "Кельвін":
                    base = value - 273.15
                if to_unit == "Цельсій":
                    result = base
                elif to_unit == "Фаренгейт":
                    result = base * 9/5 + 32
                elif to_unit == "Кельвін":
                    result = base + 273.15
            elif cat == "Валюта":
                factors = self.categories[cat]
                from_factor = factors[self.from_unit.get()]
                to_factor = factors[self.to_unit.get()]
                result = value * from_factor / to_factor
            else:
                factors = self.categories[cat]
                from_factor = factors[self.from_unit.get()]
                to_factor = factors[self.to_unit.get()]
                result = value * from_factor / to_factor
            self.result_value.set(str(result))
        except Exception as e:
            self.result_value.set("Error")
    
    def custom_units(self):
        win = ctk.CTkToplevel(self)
        win.title("Налаштування одиниць")
        label = ctk.CTkLabel(win, text="Функціонал налаштування одиниць у розробці", font=("Helvetica", 16))
        label.pack(padx=20, pady=20)
    
    def update_currency_rates(self):
        # Stub‑функція: тут можна інтегрувати API для оновлення валютних курсів
        # Наприклад, оновити self.categories["Валюта"] на основі веб-запиту
        self.categories["Валюта"] = {
            "USD": 1,
            "EUR": 0.9,
            "UAH": 42,
            "GBP": 0.8
        }
        self.update_units("Валюта")
        tk.messagebox.showinfo("Інформація", "Курси валют оновлено")
    
    def apply_settings(self, settings):
        font = ("Helvetica", settings.get("font_size", 18))
        self.value_entry.configure(font=font)

# Графічний модуль для побудови графіків функцій
class GraphPlot(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        func_label = ctk.CTkLabel(self, text="Введіть функцію f(x):", font=("Helvetica", 16))
        func_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.func_entry = ctk.CTkEntry(self, font=("Helvetica", 16))
        self.func_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        xmin_label = ctk.CTkLabel(self, text="x min:", font=("Helvetica", 16))
        xmin_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.xmin_entry = ctk.CTkEntry(self, font=("Helvetica", 16))
        self.xmin_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        
        xmax_label = ctk.CTkLabel(self, text="x max:", font=("Helvetica", 16))
        xmax_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.xmax_entry = ctk.CTkEntry(self, font=("Helvetica", 16))
        self.xmax_entry.grid(row=2, column=1, padx=10, pady=10, sticky="ew")
        
        plot_btn = ctk.CTkButton(self, text="Побудувати графік", font=("Helvetica", 16), command=self.plot_function)
        plot_btn.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        export_btn = ctk.CTkButton(self, text="Експорт графіка", font=("Helvetica", 16), command=self.export_graph)
        export_btn.grid(row=4, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        
        self.figure = plt.Figure(figsize=(5,3), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().grid(row=5, column=0, columnspan=2, padx=10, pady=10)
        
        back_btn = ctk.CTkButton(self, text="Назад", font=("Helvetica", 16),
                                 command=lambda: self.controller.show_frame("MainMenu"))
        back_btn.grid(row=6, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
    
    def plot_function(self):
        try:
            func_str = self.func_entry.get()
            xmin = float(self.xmin_entry.get())
            xmax = float(self.xmax_entry.get())
            if xmin >= xmax:
                self.ax.clear()
                self.ax.text(0.5, 0.5, "x min повинен бути меншим за x max", transform=self.ax.transAxes, ha="center")
                self.canvas.draw()
                return
            xs = [xmin + i*(xmax - xmin)/1000 for i in range(1001)]
            ys = []
            allowed_names = {"x": 0, "sin": math.sin, "cos": math.cos, "tan": math.tan,
                             "sqrt": math.sqrt, "log": math.log, "log10": math.log10, "pi": math.pi,
                             "e": math.e, "abs": abs, "pow": pow}
            for x in xs:
                allowed_names["x"] = x
                y = eval(func_str, {"__builtins__":{}}, allowed_names)
                ys.append(y)
            self.ax.clear()
            self.ax.plot(xs, ys)
            self.ax.set_title(f"f(x) = {func_str}")
            self.canvas.draw()
        except Exception as e:
            self.ax.clear()
            self.ax.text(0.5, 0.5, "Помилка у введенні функції", transform=self.ax.transAxes, ha="center")
            self.canvas.draw()
    
    def export_graph(self):
        try:
            filename = "graph_export.png"
            self.figure.savefig(filename)
            tk.messagebox.showinfo("Експорт", f"Графік збережено у файл {filename}")
        except Exception as e:
            tk.messagebox.showerror("Помилка", "Не вдалося зберегти графік")
    
    def apply_settings(self, settings):
        # Оновлення шрифту для елементів графічного модуля (якщо потрібно)
        pass

# Вікно довідки
class HelpWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Довідка")
        help_text = (
            "Довідка по використанню додатку:\n\n"
            "1. Звичайний калькулятор: базові арифметичні операції.\n"
            "2. Складний калькулятор: розширені функції (тригонометрія, логарифми, дроби, пам'ять, історія).\n"
            "   - Історія зберігається між сесіями. Можна шукати, сортувати та експортувати історію в CSV або PDF.\n"
            "3. Конвертор: конвертація одиниць за категоріями (довжина, об’єм, температура, вага, швидкість, енергія, тиск, валюта).\n"
            "   - Для валюти є можливість оновлення курсів.\n"
            "4. Графіки функцій: введіть вираз f(x), вкажіть діапазон x та побудуйте графік. Також можна експортувати графік у PNG.\n"
            "5. Налаштування: змініть тему, розмір шрифту та гарячі клавіші за бажанням.\n\n"
            "Для повернення до головного меню використовуйте кнопку 'Назад'."
        )
        text_widget = ctk.CTkTextbox(self, width=600, height=400, font=("Helvetica", 14), wrap="word")
        text_widget.insert("1.0", help_text)
        text_widget.configure(state="disabled")
        text_widget.pack(padx=20, pady=20)

if __name__ == "__main__":
    app = App()
    app.mainloop()
