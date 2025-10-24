import tkinter as tk
from tkinter import ttk, colorchooser
import colorsys


def clamp(x, a, b):
    return max(a, min(b, x))


def rgb_to_cmyk(r, g, b):
    """Конвертирует RGB (0-255) в CMYK (%)."""
    if (r, g, b) == (0, 0, 0):
        return 0.0, 0.0, 0.0, 100.0
    r_p, g_p, b_p = r / 255.0, g / 255.0, b / 255.0
    k = 1 - max(r_p, g_p, b_p)
    if k == 1.0:
        return 0.0, 0.0, 0.0, 100.0

    c = (1 - r_p - k) / (1 - k)
    m = (1 - g_p - k) / (1 - k)
    y = (1 - b_p - k) / (1 - k)
    return round(c * 100, 2), round(m * 100, 2), round(y * 100, 2), round(k * 100, 2)


def cmyk_to_rgb(c, m, y, k):
    """Конвертирует CMYK (%) в RGB (0-255)."""
    c_p, m_p, y_p, k_p = c / 100.0, m / 100.0, y / 100.0, k / 100.0
    r = 255 * (1 - c_p) * (1 - k_p)
    g = 255 * (1 - m_p) * (1 - k_p)
    b = 255 * (1 - y_p) * (1 - k_p)
    return int(round(clamp(r, 0, 255))), int(round(clamp(g, 0, 255))), int(round(clamp(b, 0, 255)))


def rgb_to_hsv_vals(r, g, b):
    """
    Конвертирует RGB (0-255) в HSV (H: 0-360, S: 0-100, V: 0-100).  
    """
    r_p, g_p, b_p = r / 255.0, g / 255.0, b / 255.0
    h, s, v = colorsys.rgb_to_hsv(r_p, g_p, b_p)
    return round(h * 360, 2), round(s * 100, 2), round(v * 100, 2)


def hsv_to_rgb_vals(h, s, v):
    """
    Конвертирует HSV (H: 0-360, S: 0-100, V: 0-100) в RGB (0-255).
    """
    h_p, s_p, v_p = (h % 360) / 360.0, s / 100.0, v / 100.0
    r_p, g_p, b_p = colorsys.hsv_to_rgb(h_p, s_p, v_p)
    
    r = r_p * 255
    g = g_p * 255
    b = b_p * 255

    return (
        int(round(clamp(r, 0, 255))),
        int(round(clamp(g, 0, 255))),
        int(round(clamp(b, 0, 255)))
    )


class ColourConverterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Лабораторная 1 — RGB / CMYK / HSV')
        self.geometry('1200x520')
        self.resizable(False, False)

        self.updating = False

        self.rgb = (255, 0, 0) #храним только rgb

        self._build_ui()
        self._sync_all_from_rgb()

    def _build_ui(self):
        pad = 10
        left = ttk.Frame(self, padding=pad)
        left.pack(side='left', fill='y')

        self.display = tk.Canvas(left, width=360, height=360, bd=2, relief='sunken')
        self.display.grid(row=0, column=0, padx=pad, pady=pad)

        btns_frame = ttk.Frame(left)
        btns_frame.grid(row=1, column=0, pady=(0, pad))

        ttk.Button(btns_frame, text='Choose colour…', command=self._choose_colour).grid(row=0, column=0, padx=4)
        ttk.Button(btns_frame, text='Copy HEX', command=self._copy_hex).grid(row=0, column=1, padx=4)

        palette_frame = ttk.LabelFrame(left, text='Palette', padding=6)
        palette_frame.grid(row=2, column=0, sticky='we', pady=(0, pad))

        base_colours = ['#ffffff', '#000000', '#ff0000', '#00ff00', '#0000ff',
                        '#ffff00', '#ff00ff', '#00ffff', '#808080', '#c08040']
        for i, hexc in enumerate(base_colours):
            b = tk.Button(palette_frame, bg=hexc, width=3, height=1, command=lambda h=hexc: self._set_from_hex(h))
            b.grid(row=0, column=i, padx=2)

        right = ttk.Frame(self, padding=pad)
        right.pack(side='right', fill='both', expand=True)

        self.vars = {}

        group_rgb = ttk.LabelFrame(right, text='RGB — 0..255', padding=8)
        group_rgb.pack(fill='x', pady=6)
        self._make_rgb_controls(group_rgb)

        group_cmyk = ttk.LabelFrame(right, text='CMYK — %', padding=8)
        group_cmyk.pack(fill='x', pady=6)
        self._make_cmyk_controls(group_cmyk)

        group_hsv = ttk.LabelFrame(right, text='HSV — H:0..360 S/V:0..100', padding=8)
        group_hsv.pack(fill='x', pady=6)
        self._make_hsv_controls(group_hsv)

        hex_frame = ttk.Frame(right)
        hex_frame.pack(fill='x', pady=8)
        ttk.Label(hex_frame, text='Hex:').pack(side='left')
        self.hex_var = tk.StringVar()
        self.hex_entry = ttk.Entry(hex_frame, textvariable=self.hex_var, width=12)
        self.hex_entry.pack(side='left', padx=6)
        self.hex_entry.bind('<Return>', lambda e: self._set_from_hex(self.hex_var.get()))
        self.hex_entry.bind('<FocusOut>', lambda e: self._set_from_hex(self.hex_var.get()))

    def _make_rgb_controls(self, parent):
        frm = ttk.Frame(parent)
        frm.pack(fill='x')
        for i, comp in enumerate(['R', 'G', 'B']):
            v = tk.IntVar(value=0)
            self.vars[f'rgb_{comp}'] = v
            lbl = ttk.Label(frm, text=comp)
            lbl.grid(row=0, column=i * 3, padx=(0, 4))
            ent = ttk.Entry(frm, textvariable=v, width=6)
            ent.grid(row=0, column=i * 3 + 1)
            ent.bind('<Return>', lambda e, c=comp: self._on_rgb_entry(c))
            ent.bind('<FocusOut>', lambda e, c=comp: self._on_rgb_entry(c))
            s = ttk.Scale(frm, from_=0, to=255, orient='horizontal', command=lambda val, c=comp: self._on_rgb_slider(c, val))
            s.grid(row=0, column=i * 3 + 2, padx=(6, 12), sticky='we')
            self.vars[f'rgb_{comp}_scale'] = s

    def _make_cmyk_controls(self, parent):
        frm = ttk.Frame(parent)
        frm.pack(fill='x')
        for i, comp in enumerate(['C', 'M', 'Y', 'K']):
            v = tk.DoubleVar(value=0.0)
            self.vars[f'cmyk_{comp}'] = v
            lbl = ttk.Label(frm, text=comp)
            lbl.grid(row=0, column=i * 3, padx=(0, 4))
            ent = ttk.Entry(frm, textvariable=v, width=6)
            ent.grid(row=0, column=i * 3 + 1)
            ent.bind('<Return>', lambda e, c=comp: self._on_cmyk_entry(c))
            ent.bind('<FocusOut>', lambda e, c=comp: self._on_cmyk_entry(c))
            s = ttk.Scale(frm, from_=0, to=100, orient='horizontal', command=lambda val, c=comp: self._on_cmyk_slider(c, val))
            s.grid(row=0, column=i * 3 + 2, padx=(6, 12), sticky='we')
            self.vars[f'cmyk_{comp}_scale'] = s

    def _make_hsv_controls(self, parent):
        """Создает элементы управления для HSV."""
        frm = ttk.Frame(parent)
        frm.pack(fill='x')
        for i, comp in enumerate(['H', 'S', 'V']): 
            if comp == 'H':
                v = tk.DoubleVar(value=0.0)
                to = 360
            else:
                v = tk.DoubleVar(value=0.0)
                to = 100
            
            self.vars[f'hsv_{comp}'] = v
            lbl = ttk.Label(frm, text=comp)
            lbl.grid(row=0, column=i * 3, padx=(0, 4))
            ent = ttk.Entry(frm, textvariable=v, width=6)
            ent.grid(row=0, column=i * 3 + 1)
            ent.bind('<Return>', lambda e, c=comp: self._on_hsv_entry(c)) 
            ent.bind('<FocusOut>', lambda e, c=comp: self._on_hsv_entry(c)) 
            s = ttk.Scale(frm, from_=0, to=to, orient='horizontal', command=lambda val, c=comp: self._on_hsv_slider(c, val))
            s.grid(row=0, column=i * 3 + 2, padx=(6, 12), sticky='we')
            self.vars[f'hsv_{comp}_scale'] = s 


    def _on_rgb_entry(self, comp):
        try:
            v = int(self.vars[f'rgb_{comp}'].get())
        except Exception:
            return
        v = int(clamp(v, 0, 255))
        self._update_rgb_component(comp, v)

    def _on_rgb_slider(self, comp, val):
        v = int(round(float(val)))
        self.vars[f'rgb_{comp}'].set(v)
        self._update_rgb_component(comp, v)

    def _on_cmyk_entry(self, comp):
        try:
            v = float(self.vars[f'cmyk_{comp}'].get())
        except Exception:
            return
        v = clamp(v, 0.0, 100.0)
        self._update_cmyk_component(comp, v)

    def _on_cmyk_slider(self, comp, val):
        v = round(float(val), 2)
        self.vars[f'cmyk_{comp}'].set(v)
        self._update_cmyk_component(comp, v)

    def _on_hsv_entry(self, comp):
        """Обработчик ввода для HSV."""
        try:
            v = float(self.vars[f'hsv_{comp}'].get()) 
        except Exception:
            return
        if comp == 'H':
            v = v % 360
        else:
            v = clamp(v, 0.0, 100.0)
        self._update_hsv_component(comp, v)

    def _on_hsv_slider(self, comp, val):
        """Обработчик слайдера для HSV."""
        v = round(float(val), 2)
        self.vars[f'hsv_{comp}'].set(v) 
        self._update_hsv_component(comp, v) 


    def _update_rgb_component(self, comp, value):
        if self.updating:
            return
        self.updating = True
        r, g, b = self.rgb
        if comp == 'R':
            r = value
        elif comp == 'G':
            g = value
        else:
            b = value
        self.rgb = (r, g, b)
        self._sync_all_from_rgb()
        self.updating = False

    def _update_cmyk_component(self, comp, value):
        if self.updating:
            return
        self.updating = True
        c = self.vars['cmyk_C'].get() if comp != 'C' else value
        m = self.vars['cmyk_M'].get() if comp != 'M' else value
        y = self.vars['cmyk_Y'].get() if comp != 'Y' else value
        k = self.vars['cmyk_K'].get() if comp != 'K' else value
        r, g, b = cmyk_to_rgb(float(c), float(m), float(y), float(k))
        self.rgb = (r, g, b)
        self._sync_all_from_rgb()
        self.updating = False

    def _update_hsv_component(self, comp, value):
        """Обновляет цвет по компоненту HSV."""
        if self.updating:
            return
        self.updating = True
        h = self.vars['hsv_H'].get() if comp != 'H' else value
        s = self.vars['hsv_S'].get() if comp != 'S' else value
        v = self.vars['hsv_V'].get() if comp != 'V' else value 

        r, g, b = hsv_to_rgb_vals(float(h), float(s), float(v))
        self.rgb = (r, g, b)
        self._sync_all_from_rgb()
        self.updating = False

    def _sync_all_from_rgb(self):
        """Синхронизирует все цветовые модели, используя текущий RGB."""
        r, g, b = self.rgb
        hexc = '#%02x%02x%02x' % (r, g, b)
        self.display.delete('all')
        self.display.create_rectangle(0, 0, 360, 360, fill=hexc, outline='')

        self.hex_var.set(hexc.upper())

        for i, comp in enumerate(['R', 'G', 'B']):
            self.vars[f'rgb_{comp}'].set((r, g, b)[i])
            try:
                self.vars[f'rgb_{comp}_scale'].set((r, g, b)[i])
            except Exception:
                pass

        c, m, y, k = rgb_to_cmyk(r, g, b)
        self.vars['cmyk_C'].set(c)
        self.vars['cmyk_M'].set(m)
        self.vars['cmyk_Y'].set(y)
        self.vars['cmyk_K'].set(k)
        for comp in ['C', 'M', 'Y', 'K']:
            try:
                self.vars[f'cmyk_{comp}_scale'].set(self.vars[f'cmyk_{comp}'].get())
            except Exception:
                pass

        h, s, v = rgb_to_hsv_vals(r, g, b)
        self.vars['hsv_H'].set(h)
        self.vars['hsv_S'].set(s)
        self.vars['hsv_V'].set(v)
        
        for comp in ['H', 'S', 'V']: 
            try:
                self.vars[f'hsv_{comp}_scale'].set(self.vars[f'hsv_{comp}'].get())
            except Exception:
                pass

    def _choose_colour(self):
        hexc, _ = colorchooser.askcolor(color=self.hex_var.get(), parent=self)
        if hexc:
            self._set_from_hex(_)

    def _copy_hex(self):
        self.clipboard_clear()
        self.clipboard_append(self.hex_var.get())

    def _set_from_hex(self, hexstr):
        h = hexstr.strip()
        if not h:
            return
        if not h.startswith('#'):
            h = '#' + h
        if len(h) not in (4, 7):
            return
        try:
            if len(h) == 4:
                r = int(h[1] * 2, 16)
                g = int(h[2] * 2, 16)
                b = int(h[3] * 2, 16)
            else:
                r = int(h[1:3], 16)
                g = int(h[3:5], 16)
                b = int(h[5:7], 16)
        except Exception:
            return
        if self.updating:
            return
        self.updating = True
        self.rgb = (r, g, b)
        self._sync_all_from_rgb()
        self.updating = False


if __name__ == '__main__':
    app = ColourConverterApp()
    app.mainloop()
