import tkinter as tk
from tkinter import ttk, colorchooser, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from collections import defaultdict
import textwrap
import os

class BarGraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bar Graph Editor")

        self.root.iconbitmap(os.path.join(os.path.dirname(__file__), 'logo.ico'))
        self.bars = defaultdict(dict)
        self.colors = {}
        self.set_colors = {}

        self._build_gui()
        self._draw_graph()

    def _build_gui(self):
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.left_panel = ttk.Frame(self.main_frame, padding=10)
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y)

        self.center_panel = ttk.Frame(self.main_frame)
        self.center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.right_panel = ttk.Frame(self.main_frame, padding=10)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.Y)

        self._create_left_controls()
        self._create_right_controls()
        self._create_canvas()

    def _create_left_controls(self):
        # Graph Title
        ttk.Label(self.left_panel, text="Graph Title:").pack()
        self.title_entry = ttk.Entry(self.left_panel)
        self.title_entry.pack(fill=tk.X)

        # Axis Title
        ttk.Label(self.left_panel, text="Y-axis Title:").pack()
        self.yaxis_entry = ttk.Entry(self.left_panel)
        self.yaxis_entry.pack(fill=tk.X)

        # Font Sizes
        self.title_font_size = self._add_font_slider(self.left_panel, "Title Font Size", 14)
        self.yaxis_font_size = self._add_font_slider(self.left_panel, "Y-axis Font Size", 10)
        self.label_font_size = self._add_font_slider(self.left_panel, "Label Font Size", 9)
        self.value_font_size = self._add_font_slider(self.left_panel, "Value Font Size", 9)

        # Label Rotation Options
        ttk.Label(self.left_panel, text="Label Orientation:").pack(anchor=tk.W)
        self.label_rotation = tk.StringVar(value="Horizontal")
        for text in ["Horizontal", "Vertical", "Diagonal"]:
            ttk.Radiobutton(self.left_panel, text=text, variable=self.label_rotation, value=text, command=self._draw_graph).pack(anchor=tk.W)

        # Toggles
        self._add_toggle(self.left_panel, "Show Title", True, 'show_title')
        self._add_toggle(self.left_panel, "Show Y-axis Title", True, 'show_ytitle')
        self._add_toggle(self.left_panel, "Show Bar Labels", True, 'show_labels')
        self._add_toggle(self.left_panel, "Show Values", True, 'show_values')
        self._add_toggle(self.left_panel, "Show Grid", True, 'show_grid')
        self._add_toggle(self.left_panel, "Use Percentage Y-axis", False, 'use_percentage')

        # Custom Max for Percentage
        self.use_custom_max = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.left_panel, text="Use Custom Max", variable=self.use_custom_max, command=self._draw_graph).pack(anchor=tk.W)

        ttk.Label(self.left_panel, text="Custom Max Value").pack(anchor=tk.W)
        self.percentage_max = tk.DoubleVar(value=100)
        self.percentage_max_entry = ttk.Entry(self.left_panel, textvariable=self.percentage_max)
        self.percentage_max_entry.pack(fill=tk.X)

    def _add_font_slider(self, panel, label, default):
        ttk.Label(panel, text=label).pack(anchor=tk.W)
        var = tk.IntVar(value=default)
        ttk.Scale(panel, from_=6, to=24, variable=var, orient=tk.HORIZONTAL, command=lambda e: self._draw_graph()).pack(fill=tk.X)
        return var

    def _add_toggle(self, panel, text, default, varname):
        var = tk.BooleanVar(value=default)
        setattr(self, varname, var)
        ttk.Checkbutton(panel, text=text, variable=var, command=self._draw_graph).pack(anchor=tk.W)

    def _create_right_controls(self):
        # Bar Label & Set
        ttk.Label(self.right_panel, text="Bar Label:").pack()
        self.bar_label_entry = ttk.Entry(self.right_panel)
        self.bar_label_entry.pack(fill=tk.X)

        ttk.Label(self.right_panel, text="Set Name:").pack()
        self.set_label_entry = ttk.Entry(self.right_panel)
        self.set_label_entry.pack(fill=tk.X)

        ttk.Label(self.right_panel, text="Value:").pack()
        self.value_entry = ttk.Entry(self.right_panel)
        self.value_entry.pack(fill=tk.X)

        ttk.Button(self.right_panel, text="Choose Bar Label Color", command=self.choose_label_color).pack()
        ttk.Button(self.right_panel, text="Choose Set Color", command=self.choose_set_color).pack()

        ttk.Button(self.right_panel, text="Add/Update Bar", command=self.add_bar).pack(fill=tk.X)
        ttk.Button(self.right_panel, text="Remove Selected Bar", command=self.remove_selected_bar).pack(fill=tk.X)

        # Listbox
        self.bar_listbox = tk.Listbox(self.right_panel)
        self.bar_listbox.pack(fill=tk.BOTH, expand=True)

        # Move and Save
        move_frame = ttk.Frame(self.right_panel)
        move_frame.pack(fill=tk.X)
        ttk.Button(move_frame, text="Move Up", command=self.move_up).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(move_frame, text="Move Down", command=self.move_down).pack(side=tk.LEFT, expand=True, fill=tk.X)

        ttk.Button(self.right_panel, text="Export Graph", command=self.save_graph).pack(fill=tk.X)

    def _create_canvas(self):
        self.fig = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.center_panel)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def choose_label_color(self):
        color = colorchooser.askcolor()[1]
        label = self.bar_label_entry.get()
        if color and label:
            self.colors[label] = color
            self._draw_graph()

    def choose_set_color(self):
        color = colorchooser.askcolor()[1]
        set_name = self.set_label_entry.get()
        if color and set_name:
            self.set_colors[set_name] = color
            self._draw_graph()

    def add_bar(self):
        label = self.bar_label_entry.get()
        set_name = self.set_label_entry.get()
        try:
            value = float(self.value_entry.get())
        except ValueError:
            return
        color = self.set_colors.get(set_name, self.colors.get(label, "#8888FF"))
        self.bars[label][set_name] = (value, color)
        self._refresh_listbox()
        self._draw_graph()

    def remove_selected_bar(self):
        selected = self.bar_listbox.curselection()
        if selected:
            item = self.bar_listbox.get(selected[0])
            label, set_name = item.split(" :: ")
            del self.bars[label][set_name]
            if not self.bars[label]:
                del self.bars[label]
            self._refresh_listbox()
            self._draw_graph()

    def move_up(self):
        idx = self.bar_listbox.curselection()
        if idx and idx[0] > 0:
            items = list(self.bar_listbox.get(0, tk.END))
            items[idx[0]], items[idx[0]-1] = items[idx[0]-1], items[idx[0]]
            self._rebuild_from_list(items)

    def move_down(self):
        idx = self.bar_listbox.curselection()
        if idx and idx[0] < self.bar_listbox.size() - 1:
            items = list(self.bar_listbox.get(0, tk.END))
            items[idx[0]], items[idx[0]+1] = items[idx[0]+1], items[idx[0]]
            self._rebuild_from_list(items)

    def _rebuild_from_list(self, items):
        new_bars = defaultdict(dict)
        for item in items:
            label, set_name = item.split(" :: ")
            val, color = self.bars[label][set_name]
            new_bars[label][set_name] = (val, color)
        self.bars = new_bars
        self._refresh_listbox()
        self._draw_graph()

    def _refresh_listbox(self):
        self.bar_listbox.delete(0, tk.END)
        for label in self.bars:
            for set_name in self.bars[label]:
                self.bar_listbox.insert(tk.END, f"{label} :: {set_name}")

    def _draw_graph(self):
        self.ax.clear()
        labels = list(self.bars.keys())
        sets = sorted(set(k for v in self.bars.values() for k in v))
        index_map = {s: i for i, s in enumerate(sets)}

        bar_width = 0.8 / max(1, len(sets))
        positions = list(range(len(labels)))

        for set_name in sets:
            raw_values = [self.bars[l].get(set_name, (0, '#DDD'))[0] for l in labels]
            colors = [self.bars[l].get(set_name, (0, '#DDD'))[1] for l in labels]

            if self.use_percentage.get():
                if self.use_custom_max.get():
                    max_val = self.percentage_max.get() or 1
                else:
                    max_val = max([max(v for v, _ in sets.values()) for sets in self.bars.values()] or [1])
                values = [v / max_val * 100 for v in raw_values]
            else:
                values = raw_values

            x_pos = [p + index_map[set_name]*bar_width for p in positions]
            bars = self.ax.bar(x_pos, values, bar_width, label=set_name, color=colors, edgecolor='black')

            if self.show_values.get():
                for i, bar in enumerate(bars):
                    height = bar.get_height()
                    if height:
                        label = f"{height:.1f}%" if self.use_percentage.get() else f"{height:.1f}"
                        self.ax.text(bar.get_x() + bar.get_width()/2, height, label,
                                     ha='center', va='bottom', fontsize=self.value_font_size.get())

        rot = {'Horizontal': 0, 'Vertical': 90, 'Diagonal': 45}[self.label_rotation.get()]
        wrapped_labels = ['\n'.join(textwrap.wrap(label, 15)) for label in labels]

        self.ax.set_xticks([p + bar_width * (len(sets) - 1)/2 for p in positions])
        self.ax.set_xticklabels(wrapped_labels, fontsize=self.label_font_size.get() if self.show_labels.get() else 0, rotation=rot)

        if self.show_title.get():
            self.ax.set_title(self.title_entry.get(), fontsize=self.title_font_size.get())
        if self.show_ytitle.get():
            self.ax.set_ylabel(self.yaxis_entry.get(), fontsize=self.yaxis_font_size.get())
        if self.show_grid.get():
            self.ax.yaxis.grid(True)
        if self.use_percentage.get():
            self.ax.set_ylim(0, 100)

        self.ax.legend()
        self.canvas.draw()

    def save_graph(self):
        file = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if file:
            self.fig.savefig(file)

if __name__ == '__main__':
    root = tk.Tk()
    app = BarGraphApp(root)
    root.mainloop()