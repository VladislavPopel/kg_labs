import tkinter as tk
from tkinter import ttk
import math
import time

class RasterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Lab 3 - Растровые Алгоритмы")
        self.root.minsize(1100, 850)

        self.scale = 20.0
        self.pixels = []
        
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill="both", expand=True)

        self.controls_frame = ttk.Frame(self.main_frame, padding="10", width=250)
        self.controls_frame.pack(side="left", fill="y", anchor="n")
        self.controls_frame.pack_propagate(False)

        ttk.Label(self.controls_frame, text="Выберите Алгоритм:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 5))
        self.alg_var = tk.StringVar(value="step")
        
        alg_list = [
            ("Пошаговый", "step"),
            ("ЦДА (DDA)", "dda"),
            ("Брезенхем (Линия)", "bresenham_line"),
            ("Брезенхем (Окружность)", "bresenham_circle")
        ]

        for text, val in alg_list:
            ttk.Radiobutton(self.controls_frame, text=text, variable=self.alg_var, value=val, command=self.on_alg_change).pack(anchor="w")

        self.inputs_container = ttk.Frame(self.controls_frame)
        self.inputs_container.pack(fill="x", anchor="w", pady=15)

        self.line_inputs_frame = ttk.Frame(self.inputs_container)
        self.entry_x1, self.entry_y1, self.entry_x2, self.entry_y2 = self._create_line_inputs(self.line_inputs_frame)

        self.circle_inputs_frame = ttk.Frame(self.inputs_container)
        self.entry_xc, self.entry_yc, self.entry_r = self._create_circle_inputs(self.circle_inputs_frame)

        ttk.Label(self.controls_frame, text="Масштаб:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(15, 5))
        self.scale_var = tk.DoubleVar(value=self.scale)
        self.zoom_slider = ttk.Scale(self.controls_frame, from_=5, to=50, variable=self.scale_var, orient="horizontal", command=self.on_zoom_change)
        self.zoom_slider.pack(anchor="w", fill="x")
        self.scale_label = ttk.Label(self.controls_frame, text=f"{self.scale:.0f} пикс/ед.")
        self.scale_label.pack(anchor="w")

        self.draw_button = ttk.Button(self.controls_frame, text="Нарисовать", command=self.on_draw)
        self.draw_button.pack(fill="x", pady=10)
        self.clear_button = ttk.Button(self.controls_frame, text="Очистить", command=self.clear_canvas)
        self.clear_button.pack(fill="x")

        self.canvas_frame = ttk.Frame(self.main_frame, relief="sunken", borderwidth=2)
        self.canvas_frame.pack(side="right", fill="both", expand=True, padx=10)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg="white", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        self.canvas.bind("<Configure>", self.on_canvas_resize)

        self.status_var = tk.StringVar(value="Готово")
        self.status_label = ttk.Label(self.main_frame, textvariable=self.status_var, relief="sunken", anchor="w", padding=5)
        self.status_label.pack(side="bottom", fill="x", after=self.controls_frame)

        self.canvas_width = 0
        self.canvas_height = 0
        self.origin_x = 0
        self.origin_y = 0

        self.on_alg_change()

    def _create_line_inputs(self, parent):
        parent.columnconfigure(1, weight=1)
        
        ttk.Label(parent, text="X1:").grid(row=0, column=0, sticky="w", padx=5)
        x1 = ttk.Entry(parent, width=5)
        x1.grid(row=0, column=1, sticky="ew")
        
        ttk.Label(parent, text="Y1:").grid(row=0, column=2, sticky="w", padx=5)
        y1 = ttk.Entry(parent, width=5)
        y1.grid(row=0, column=3, sticky="ew")

        ttk.Label(parent, text="X2:").grid(row=1, column=0, sticky="w", padx=5)
        x2 = ttk.Entry(parent, width=5)
        x2.grid(row=1, column=1, sticky="ew", pady=5)
        
        ttk.Label(parent, text="Y2:").grid(row=1, column=2, sticky="w", padx=5)
        y2 = ttk.Entry(parent, width=5)
        y2.grid(row=1, column=3, sticky="ew", pady=5)
        
        x1.insert(0, "-10")
        y1.insert(0, "-5")
        x2.insert(0, "10")
        y2.insert(0, "8")
        
        return x1, y1, x2, y2

    def _create_circle_inputs(self, parent):
        parent.columnconfigure(1, weight=1)

        ttk.Label(parent, text="Xc:").grid(row=0, column=0, sticky="w", padx=5)
        xc = ttk.Entry(parent, width=5)
        xc.grid(row=0, column=1, sticky="ew")
        
        ttk.Label(parent, text="Yc:").grid(row=0, column=2, sticky="w", padx=5)
        yc = ttk.Entry(parent, width=5)
        yc.grid(row=0, column=3, sticky="ew")

        ttk.Label(parent, text="R:").grid(row=1, column=0, sticky="w", padx=5)
        r = ttk.Entry(parent, width=5)
        r.grid(row=1, column=1, sticky="ew", pady=5)
        
        xc.insert(0, "0")
        yc.insert(0, "0")
        r.insert(0, "12")

        return xc, yc, r

    def on_canvas_resize(self, event):
        self.canvas_width = event.width
        self.canvas_height = event.height
        self.origin_x = self.canvas_width / 2
        self.origin_y = self.canvas_height / 2
        self.redraw_all()

    def on_alg_change(self):
        alg = self.alg_var.get()
        if alg == "bresenham_circle":
            self.line_inputs_frame.pack_forget()
            self.circle_inputs_frame.pack(fill="x", anchor="w")
        else:
            self.circle_inputs_frame.pack_forget()
            self.line_inputs_frame.pack(fill="x", anchor="w")

    def on_zoom_change(self, val):
        self.scale = self.scale_var.get()
        self.scale_label.config(text=f"{self.scale:.0f} пикс/ед.")
        self.redraw_all()
            
    def on_draw(self):
        self.canvas.delete("pixel")
        self.pixels = []
        
        alg = self.alg_var.get()
        
        try:
            start_time = time.perf_counter()
            
            if alg == "bresenham_circle":
                xc = int(self.entry_xc.get())
                yc = int(self.entry_yc.get())
                r = int(self.entry_r.get())
                if r < 0:
                    self.status_var.set("Ошибка: Радиус не может быть отрицательным.")
                    return
                self.pixels = self.bresenham_circle(xc, yc, r)
            else:
                x1 = int(self.entry_x1.get())
                y1 = int(self.entry_y1.get())
                x2 = int(self.entry_x2.get())
                y2 = int(self.entry_y2.get())
                if alg == "step":
                    self.pixels = self.step_by_step_line(x1, y1, x2, y2)
                elif alg == "dda":
                    self.pixels = self.dda_line(x1, y1, x2, y2)
                elif alg == "bresenham_line":
                    self.pixels = self.bresenham_line(x1, y1, x2, y2)
            
            end_time = time.perf_counter()
            execution_time = (end_time - start_time) * 1000
            
            self.draw_pixels()
            
            time_report = f"Время: {execution_time:.3f} мс | "
            time_report += f"Точек: {len(self.pixels)} | "
            time_report += f"Алгоритм: {self.get_algorithm_name(alg)}"
            
            self.status_var.set(time_report)
            print(f"\n--- ОТЧЕТ ПРОИЗВОДИТЕЛЬНОСТИ ---")
            print(time_report)
            print("--- КОНЕЦ ОТЧЕТА ---")
        
        except ValueError:
            self.status_var.set("Ошибка: Введите целые числа во все поля.")
        except Exception as e:
            self.status_var.set(f"Произошла ошибка: {e}")

    def get_algorithm_name(self, alg_code):
        names = {
            "step": "Пошаговый",
            "dda": "ЦДА (DDA)",
            "bresenham_line": "Брезенхем (Линия)",
            "bresenham_circle": "Брезенхем (Окружность)"
        }
        return names.get(alg_code, "Неизвестный")

    def clear_canvas(self):
        self.pixels = []
        self.canvas.delete("pixel")
        self.draw_grid_and_axes()
        self.status_var.set("Холст очищен.")

    def redraw_all(self):
        self.canvas.delete("all")
        self.draw_grid_and_axes()
        self.draw_pixels()

    def draw_grid_and_axes(self):
        self.canvas.delete("grid")
        w, h = self.canvas_width, self.canvas_height
        ox, oy = self.origin_x, self.origin_y
        s = self.scale

        y = oy % s
        while y < h:
            self.canvas.create_line(0, y, w, y, fill="#f0f0f0", tags="grid")
            y += s
            
        x = ox % s
        while x < w:
            self.canvas.create_line(x, 0, x, h, fill="#f0f0f0", tags="grid")
            x += s

        self.canvas.create_line(0, oy, w, oy, fill="black", width=2, tags="grid", arrow=tk.LAST)
        self.canvas.create_line(ox, 0, ox, h, fill="black", width=2, tags="grid", arrow=tk.LAST)
        
        self.canvas.create_text(w - 10, oy - 10, text="X", font=("Arial", 12, "bold"), tags="grid")
        self.canvas.create_text(ox + 10, 10, text="Y", font=("Arial", 12, "bold"), tags="grid")
        
        if s > 10:
            i = 0
            x = ox + i * s
            while x < w:
                if i != 0:
                    self.canvas.create_text(x, oy + 8, text=str(i), anchor="n", tags="grid", font=("Arial", 8))
                i += 1
                x = ox + i * s
            
            i = -1
            x = ox + i * s
            while x > 0:
                self.canvas.create_text(x, oy + 8, text=str(i), anchor="n", tags="grid", font=("Arial", 8))
                i -= 1
                x = ox + i * s
                
            i = 1
            y = oy - i * s
            while y > 0:
                self.canvas.create_text(ox + 8, y, text=str(i), anchor="w", tags="grid", font=("Arial", 8))
                i += 1
                y = oy - i * s
            
            i = -1
            y = oy - i * s
            while y < h:
                self.canvas.create_text(ox + 8, y, text=str(i), anchor="w", tags="grid", font=("Arial", 8))
                i -= 1
                y = oy - i * s
            
            self.canvas.create_text(ox + 8, oy + 8, text="0", anchor="nw", tags="grid", font=("Arial", 8, "bold"))

    def plot_pixel(self, x, y, color):
        ox, oy = self.origin_x, self.origin_y
        s = self.scale
        
        center_x = ox + (x * s)
        center_y = oy - (y * s)
        
        x0 = center_x - (s / 2)
        y0 = center_y - (s / 2)
        x1 = center_x + (s / 2)
        y1 = center_y + (s / 2)

        self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline=color, tags="pixel")
        
        if s > 25 and len(self.pixels) < 10:
            self.canvas.create_text(center_x + s/2 + 5, center_y, 
                                  text=f"({x},{y})", anchor="w", 
                                  font=("Arial", 7), fill="darkgray", tags="pixel")

    def draw_pixels(self):
        for x, y, color in self.pixels:
            self.plot_pixel(x, y, color)

    def step_by_step_line(self, x1, y1, x2, y2):
        pixels = set()
        color = "#e63946"
        
        dx = x2 - x1
        dy = y2 - y1

        if dx == 0 and dy == 0:
            pixels.add((x1, y1, color))
            return list(pixels)

        if abs(dx) >= abs(dy):
            if dx == 0:
                pass
            
            if x1 > x2:
                x1, y1, x2, y2 = x2, y2, x1, y1
            
            k = dy / dx
            b = y1 - k * x1
            
            for x in range(x1, x2 + 1):
                y = round(k * x + b)
                pixels.add((x, y, color))
        
        else:
            if y1 > y2:
                x1, y1, x2, y2 = x2, y2, x1, y1

            k_inv = dx / dy
            b_inv = x1 - k_inv * y1
            
            for y in range(y1, y2 + 1):
                x = round(k_inv * y + b_inv)
                pixels.add((x, y, color))
                
        return list(pixels)

    def dda_line(self, x1, y1, x2, y2):
        pixels = set()
        color = "#2a9d8f"
        
        dx = x2 - x1
        dy = y2 - y1
        
        steps = max(abs(dx), abs(dy))
        
        if steps == 0:
            pixels.add((x1, y1, color))
            return list(pixels)

        x_inc = dx / steps
        y_inc = dy / steps
        
        x, y = float(x1), float(y1)
        
        for _ in range(steps + 1):
            pixels.add((round(x), round(y), color))
            x += x_inc
            y += y_inc
            
        return list(pixels)

    def bresenham_line(self, x1, y1, x2, y2):
        pixels = set()
        color = "#0077b6"
        
        debug_steps = []
        
        dx = abs(x2 - x1)
        dy = -abs(y2 - y1)
        
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        
        err = dx + dy
        x, y = x1, y1
        
        step = 0
        while True:
            pixels.add((x, y, color))
            debug_steps.append(f"Шаг {step}: точка ({x}, {y}), ошибка = {err}")
            
            if x == x2 and y == y2:
                break
                
            e2 = 2 * err
            
            if e2 >= dy:
                err += dy
                x += sx
                
            if e2 <= dx:
                err += dx
                y += sy
                
            step += 1
        
        if len(debug_steps) > 0:
            print("Вычисления для линии Брезенхема:")
            print(f"Исходные точки: ({x1}, {y1}) -> ({x2}, {y2})")
            print(f"dx = {dx}, dy = {dy}, sx = {sx}, sy = {sy}")
            for step_info in debug_steps[:5]:
                print(step_info)
            if len(debug_steps) > 5:
                print("... и еще", len(debug_steps) - 5, "шагов")
            print(f"Всего точек: {len(pixels)}")
        
        return list(pixels)

    def bresenham_circle(self, xc, yc, r):
        pixels = set()
        color = "#8338ec"
        
        x = 0
        y = r
        d = 3 - 2 * r

        def plot_8_points(cx, cy, x, y):
            pixels.add((cx+x, cy+y, color))
            pixels.add((cx-x, cy+y, color))
            pixels.add((cx+x, cy-y, color))
            pixels.add((cx-x, cy-y, color))
            pixels.add((cx+y, cy+x, color))
            pixels.add((cx-y, cy+x, color))
            pixels.add((cx+y, cy-x, color))
            pixels.add((cx-y, cy-x, color))

        while x <= y:
            plot_8_points(xc, yc, x, y)
            
            if d < 0:
                d = d + 4 * x + 6
            else:
                d = d + 4 * (x - y) + 10
                y -= 1
            x += 1
            
        return list(pixels)

if __name__ == "__main__":
    root = tk.Tk()
    app = RasterApp(root)
    root.mainloop()