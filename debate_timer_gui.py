# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
import time
import threading
import os
import sys
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

class ModernButton(tk.Canvas):
    def __init__(self, parent, text, command, width=120, height=45, 
                 bg_color="#00d4ff", hover_color="#00b8e6", text_color="white",
                 font=("Microsoft YaHei", 11, "bold"), **kwargs):
        super().__init__(parent, width=width, height=height, bg='#1a1a2e', 
                         highlightthickness=0, **kwargs)
        self.command = command
        self.text = text
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = font
        self.width = width
        self.height = height
        
        self.normal_bg = bg_color
        self._draw_button(bg_color)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        
    def _draw_button(self, bg_color):
        self.delete("all")
        self.create_round_rect(2, 2, self.width-2, self.height-2, 10, fill=bg_color, outline="")
        self.create_text(self.width/2, self.height/2, text=self.text, 
                        fill=self.text_color, font=self.font)
        
    def create_round_rect(self, x1, y1, x2, y2, r, **kwargs):
        self.create_arc(x1, y1, x1+2*r, y1+2*r, start=90, extent=90, **kwargs)
        self.create_arc(x2-2*r, y1, x2, y1+2*r, start=0, extent=90, **kwargs)
        self.create_arc(x1, y2-2*r, x1+2*r, y2, start=180, extent=90, **kwargs)
        self.create_arc(x2-2*r, y2-2*r, x2, y2, start=270, extent=90, **kwargs)
        self.create_rectangle(x1+r, y1, x2-r, y2, **kwargs)
        self.create_rectangle(x1, y1+r, x2, y2-r, **kwargs)
        
    def on_enter(self, event):
        self._draw_button(self.hover_color)
        
    def on_leave(self, event):
        self._draw_button(self.normal_bg)
        
    def on_click(self, event):
        self._draw_button(self.hover_color)
        self.after(100, lambda: self._draw_button(self.normal_bg))
        if self.command:
            self.command()

class ModernCard(tk.Frame):
    def __init__(self, parent, border_color="#00d4ff", bg_color="rgba(255,255,255,0.05)", **kwargs):
        super().__init__(parent, bg='#1a1a2e', **kwargs)
        self.border_color = border_color
        self.config(highlightbackground=border_color, highlightthickness=2)
        self.inner_frame = tk.Frame(self, bg='#1a1a2e')
        self.inner_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

class DebateTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("辩论赛计时器")
        self.root.geometry("1400x800")
        self.root.configure(bg='#1a1a2e')
        
        self.positive_time = 180
        self.negative_time = 180
        self.positive_running = False
        self.negative_running = False
        self.positive_remaining = 180
        self.negative_remaining = 180
        self.current_stage = "开篇立论"
        
        self.positive_timer = None
        self.negative_timer = None
        
        self.stages = {
            "开篇立论": {"正方": 180, "反方": 180},
            "攻辩环节": {"正方": 60, "反方": 60},
            "自由辩论": {"正方": 240, "反方": 240},
            "总结陈词": {"正方": 120, "反方": 120}
        }
        
        self.warning_time = 30
        self.danger_time = 10
        
        self.setup_ui()
        
    def setup_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TCombobox", fieldbackground="#2a2a4e", background="#3a3a5e", 
                       foreground="white", arrowcolor="#00d4ff")
        style.map("TCombobox", fieldbackground=[('readonly', '#2a2a4e')],
                 background=[('readonly', '#3a3a5e')])
        
        main_container = tk.Frame(self.root, bg='#1a1a2e')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        title_label = tk.Label(main_container, text="辩论赛计时器", 
                              font=("Microsoft YaHei", 32, "bold"),
                              bg='#1a1a2e', fg='transparent')
        title_label.configure(foreground='#00d4ff')
        title_label.pack(pady=(0, 15))
        
        stage_frame = tk.Frame(main_container, bg='#1a1a2e')
        stage_frame.pack(pady=10)
        
        tk.Label(stage_frame, text="当前阶段:", font=("Microsoft YaHei", 16), 
                bg='#1a1a2e', fg='white').pack(side=tk.LEFT, padx=10)
        
        self.stage_var = tk.StringVar(value="开篇立论")
        stage_combo = ttk.Combobox(stage_frame, textvariable=self.stage_var, 
                                   values=list(self.stages.keys()), font=("Microsoft YaHei", 14),
                                   width=12, state="readonly")
        stage_combo.pack(side=tk.LEFT, padx=10)
        stage_combo.bind("<<ComboboxSelected>>", self.on_stage_change)
        
        self.current_stage_label = tk.Label(stage_frame, text=self.current_stage, 
                                           font=("Microsoft YaHei", 16, "bold"),
                                           bg='#1a1a2e', fg='#00d4ff', padx=20, pady=8)
        self.current_stage_label.pack(side=tk.LEFT, padx=15)
        
        self.timers_frame = tk.Frame(main_container, bg='#1a1a2e')
        self.timers_frame.pack(pady=15, fill=tk.BOTH, expand=True)
        
        self.positive_frame = tk.Frame(self.timers_frame, bg='#1a1a2e')
        self.positive_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        
        self._create_side_timer(self.positive_frame, "正方", "#00d4ff", 
                               self.start_positive, self.pause_positive, self.reset_positive,
                               "positive")
        
        self.negative_frame = tk.Frame(self.timers_frame, bg='#1a1a2e')
        self.negative_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(15, 0))
        
        self._create_side_timer(self.negative_frame, "反方", "#ff6b6b",
                               self.start_negative, self.pause_negative, self.reset_negative,
                               "negative")
        
        settings_frame = tk.Frame(main_container, bg='#1a1a2e')
        settings_frame.pack(pady=20, fill=tk.X)
        
        tk.Label(settings_frame, text="正方时间(秒):", font=("Microsoft YaHei", 12), 
                bg='#1a1a2e', fg='white').grid(row=0, column=0, padx=10, pady=5)
        self.positive_setting = tk.Entry(settings_frame, font=("Microsoft YaHei", 12), 
                                         width=10, bg='#2a2a4e', fg='white', insertbackground='white')
        self.positive_setting.insert(0, "180")
        self.positive_setting.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(settings_frame, text="反方时间(秒):", font=("Microsoft YaHei", 12), 
                bg='#1a1a2e', fg='white').grid(row=0, column=2, padx=10, pady=5)
        self.negative_setting = tk.Entry(settings_frame, font=("Microsoft YaHei", 12), 
                                         width=10, bg='#2a2a4e', fg='white', insertbackground='white')
        self.negative_setting.insert(0, "180")
        self.negative_setting.grid(row=0, column=3, padx=10, pady=5)
        
        btn_frame = tk.Frame(settings_frame, bg='#1a1a2e')
        btn_frame.grid(row=0, column=4, padx=20)
        
        ModernButton(btn_frame, text="应用设置", command=self.apply_settings,
                    width=100, height=35, bg_color="#7b2cbf", hover_color="#9d4edd").pack(side=tk.LEFT, padx=5)
        ModernButton(btn_frame, text="双方互换", command=self.swap_sides,
                    width=100, height=35, bg_color="#28a745", hover_color="#34c759").pack(side=tk.LEFT, padx=5)
        
        self.status_label = tk.Label(main_container, text="就绪 | 希沃白板课堂辩论计时器", 
                                    font=("Microsoft YaHei", 11), 
                                    bg='#1a1a2e', fg='#888')
        self.status_label.pack(pady=(0, 5))
        
        footer_frame = tk.Frame(main_container, bg='#1a1a2e')
        footer_frame.pack(fill=tk.X)
        
        ModernButton(footer_frame, text="打开自动检测版", command=self.open_web_version,
                    width=160, height=35, bg_color="#6c757d", hover_color="#5a6268").pack(side=tk.RIGHT)
        
        self.warning_label = tk.Label(main_container, text="", 
                                     font=("Microsoft YaHei", 14, "bold"),
                                     bg='#1a1a2e', fg='#ffc107')
        self.warning_label.pack(pady=5)

    def _create_side_timer(self, parent, side_name, color, start_cmd, pause_cmd, reset_cmd, side_type):
        card_frame = tk.Frame(parent, bg='#1a1a2e')
        card_frame.pack(fill=tk.BOTH, expand=True)
        
        highlight_frame = tk.Frame(card_frame, bg=color, padx=3, pady=3)
        highlight_frame.pack(fill=tk.BOTH, expand=True)
        
        inner_frame = tk.Frame(highlight_frame, bg='#1a1a2e')
        inner_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        name_label = tk.Label(inner_frame, text=side_name, font=("Microsoft YaHei", 28, "bold"),
                             bg='#1a1a2e', fg=color)
        name_label.pack(pady=(20, 10))
        
        if side_type == "positive":
            self.timer_label = tk.Label(inner_frame, text="03:00", font=("Courier New", 80, "bold"),
                                       bg='#1a1a2e', fg=color)
        else:
            self.timer_label = tk.Label(inner_frame, text="03:00", font=("Courier New", 80, "bold"),
                                       bg='#1a1a2e', fg=color)
        self.timer_label.pack(pady=15)
        
        btn_container = tk.Frame(inner_frame, bg='#1a1a2e')
        btn_container.pack(pady=20)
        
        ModernButton(btn_container, text="开始", command=start_cmd,
                    width=90, height=35, bg_color=color, hover_color=self._brighten(color, 20)).pack(side=tk.LEFT, padx=8)
        ModernButton(btn_container, text="暂停", command=pause_cmd,
                    width=90, height=35, bg_color="#ffc107", hover_color="#ffcd38", text_color="black").pack(side=tk.LEFT, padx=8)
        ModernButton(btn_container, text="重置", command=reset_cmd,
                    width=90, height=35, bg_color="#6c757d", hover_color="#5a6268").pack(side=tk.LEFT, padx=8)
        
        self.active_frame = inner_frame

    def _brighten(self, color, amount):
        hex_color = color.lstrip('#')
        r = min(255, int(hex_color[0:2], 16) + amount)
        g = min(255, int(hex_color[2:4], 16) + amount)
        b = min(255, int(hex_color[4:6], 16) + amount)
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def format_time(self, seconds):
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins:02d}:{secs:02d}"
    
    def update_display(self):
        positive_color = '#00d4ff'
        if self.positive_remaining <= self.warning_time:
            positive_color = '#ffc107'
            self.warning_label.config(text="⚠️ 正方剩余时间不足30秒！")
        if self.positive_remaining <= self.danger_time:
            positive_color = '#ff3838'
            self.warning_label.config(text="🚨 正方剩余时间不足10秒！")
        
        negative_color = '#ff6b6b'
        if self.negative_remaining <= self.warning_time:
            if positive_color == '#ff3838':
                self.warning_label.config(text="⚠️ 双方剩余时间不足30秒！")
            else:
                self.warning_label.config(text="⚠️ 反方剩余时间不足30秒！")
        if self.negative_remaining <= self.danger_time:
            if positive_color == '#ff3838':
                self.warning_label.config(text="🚨 双方剩余时间不足10秒！")
            else:
                self.warning_label.config(text="🚨 反方剩余时间不足10秒！")
        
        self.timer_label.config(text=self.format_time(self.positive_remaining), fg=positive_color)
        
        if self.positive_remaining <= 0:
            self.pause_positive()
            self.warning_label.config(text="⏰ 正方时间到！")
            messagebox.showinfo("提示", "正方时间到！")
            self.warning_label.config(text="")
    
    def update_negative_display(self):
        negative_color = '#ff6b6b'
        if self.negative_remaining <= self.warning_time:
            negative_color = '#ffc107'
        if self.negative_remaining <= self.danger_time:
            negative_color = '#ff3838'
        
        self.negative_timer_label.config(text=self.format_time(self.negative_remaining), fg=negative_color)
        
        if self.negative_remaining <= 0:
            self.pause_negative()
            messagebox.showinfo("提示", "反方时间到！")
    
    def start_positive(self):
        if not self.positive_running:
            self.positive_running = True
            self.status_label.config(text="正方计时中...")
            self._run_positive_timer()
    
    def _run_positive_timer(self):
        if self.positive_running and self.positive_remaining > 0:
            self.positive_remaining -= 1
            self.update_display()
            self.positive_timer = self.root.after(1000, self._run_positive_timer)
    
    def pause_positive(self):
        self.positive_running = False
        if self.positive_timer:
            self.root.after_cancel(self.positive_timer)
            self.positive_timer = None
        self.status_label.config(text="正方已暂停")
    
    def reset_positive(self):
        self.pause_positive()
        try:
            self.positive_time = int(self.positive_setting.get())
        except ValueError:
            self.positive_time = 180
        self.positive_remaining = self.positive_time
        self.update_display()
        self.status_label.config(text="正方已重置")
    
    def start_negative(self):
        if not self.negative_running:
            self.negative_running = True
            self.status_label.config(text="反方计时中...")
            self._run_negative_timer()
    
    def _run_negative_timer(self):
        if self.negative_running and self.negative_remaining > 0:
            self.negative_remaining -= 1
            self.update_negative_display()
            self.negative_timer = self.root.after(1000, self._run_negative_timer)
    
    def pause_negative(self):
        self.negative_running = False
        if self.negative_timer:
            self.root.after_cancel(self.negative_timer)
            self.negative_timer = None
        self.status_label.config(text="反方已暂停")
    
    def reset_negative(self):
        self.pause_negative()
        try:
            self.negative_time = int(self.negative_setting.get())
        except ValueError:
            self.negative_time = 180
        self.negative_remaining = self.negative_time
        self.update_negative_display()
        self.status_label.config(text="反方已重置")
    
    def on_stage_change(self, event):
        self.current_stage = self.stage_var.get()
        self.current_stage_label.config(text=self.current_stage)
        
        stage_times = self.stages.get(self.current_stage, {"正方": 180, "反方": 180})
        self.positive_time = stage_times["正方"]
        self.negative_time = stage_times["反方"]
        
        self.positive_remaining = self.positive_time
        self.negative_remaining = self.negative_time
        
        self.positive_setting.delete(0, tk.END)
        self.positive_setting.insert(0, str(self.positive_time))
        self.negative_setting.delete(0, tk.END)
        self.negative_setting.insert(0, str(self.negative_time))
        
        self.pause_positive()
        self.pause_negative()
        
        self.update_display()
        self.update_negative_display()
        
        self.status_label.config(text=f"已切换到 {self.current_stage}")
    
    def apply_settings(self):
        try:
            new_positive = int(self.positive_setting.get())
            new_negative = int(self.negative_setting.get())
            
            if new_positive > 0 and new_negative > 0:
                self.positive_time = new_positive
                self.negative_time = new_negative
                
                if not self.positive_running:
                    self.positive_remaining = self.positive_time
                if not self.negative_running:
                    self.negative_remaining = self.negative_time
                
                self.update_display()
                self.update_negative_display()
                
                messagebox.showinfo("成功", "时间设置已更新！")
            else:
                messagebox.showwarning("警告", "时间必须大于0！")
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字！")
    
    def swap_sides(self):
        self.positive_time, self.negative_time = self.negative_time, self.positive_time
        self.positive_remaining, self.negative_remaining = self.negative_remaining, self.positive_remaining
        
        self.positive_setting.delete(0, tk.END)
        self.positive_setting.insert(0, str(self.positive_time))
        self.negative_setting.delete(0, tk.END)
        self.negative_setting.insert(0, str(self.negative_time))
        
        self.update_display()
        self.update_negative_display()
        
        messagebox.showinfo("成功", "双方时间已互换！")
    
    def open_web_version(self):
        webbrowser.open('http://localhost:5000/auto')

def run_flask():
    os.chdir(str(Path(__file__).parent))
    from app import app
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

def main():
    root = tk.Tk()
    root.update_idletasks()
    
    x = (root.winfo_screenwidth() - 1400) // 2
    y = (root.winfo_screenheight() - 800) // 2
    root.geometry(f"1400x800+{x}+{y}")
    
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    app = DebateTimer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
