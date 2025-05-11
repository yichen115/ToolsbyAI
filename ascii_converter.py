import tkinter as tk
from tkinter import ttk
import re

class ASCIIConverter(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # 设置窗口属性
        self.title("ASCII转换器")
        self.attributes('-topmost', True)  # 窗口置顶
        self.resizable(False, False)  # 禁止调整大小
        
        # 创建主框架
        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建输入框和标签
        ttk.Label(main_frame, text="输入字符或十六进制值:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # 创建一个框架来容纳输入框和关闭按钮
        input_row_frame = ttk.Frame(main_frame)
        input_row_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        input_row_frame.columnconfigure(0, weight=1)  # 让输入框占据大部分空间
        
        self.input_var = tk.StringVar()
        self.input_entry = ttk.Entry(input_row_frame, width=20, textvariable=self.input_var)
        self.input_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        self.input_entry.focus()
        
        # 在同一行添加关闭按钮
        ttk.Button(input_row_frame, text="关闭", command=self.quit).grid(row=0, column=1, sticky=tk.E)
        
        # 绑定输入事件
        self.input_var.trace_add("write", self.on_input_change)
        
        # 创建结果文本区域（初始隐藏）
        self.result_frame = ttk.LabelFrame(main_frame, text="ASCII信息", padding="10")
        self.result_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.result_frame.grid_remove()  # 初始隐藏
        
        self.result_text = tk.Text(self.result_frame, width=25, height=6, wrap=tk.WORD)
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.result_text.config(state=tk.DISABLED)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(self.result_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.result_text.config(yscrollcommand=scrollbar.set)
        
        # 非打印字符的描述字典
        self.control_chars = {
            0: "NUL (空字符)",
            1: "SOH (标题开始)",
            2: "STX (正文开始)",
            3: "ETX (正文结束)",
            4: "EOT (传输结束)",
            5: "ENQ (询问)",
            6: "ACK (确认)",
            7: "BEL (响铃)",
            8: "BS (退格)",
            9: "HT (水平制表符)",
            10: "LF (换行)",
            11: "VT (垂直制表符)",
            12: "FF (换页)",
            13: "CR (回车)",
            14: "SO (移出)",
            15: "SI (移入)",
            16: "DLE (数据链路转义)",
            17: "DC1 (设备控制1)",
            18: "DC2 (设备控制2)",
            19: "DC3 (设备控制3)",
            20: "DC4 (设备控制4)",
            21: "NAK (否定确认)",
            22: "SYN (同步空闲)",
            23: "ETB (传输块结束)",
            24: "CAN (取消)",
            25: "EM (介质结束)",
            26: "SUB (替换)",
            27: "ESC (转义)",
            28: "FS (文件分隔符)",
            29: "GS (组分隔符)",
            30: "RS (记录分隔符)",
            31: "US (单元分隔符)",
            127: "DEL (删除)"
        }
    
    def on_input_change(self, *args):
        """当输入变化时更新结果"""
        input_text = self.input_var.get().strip()
        
        if not input_text:
            self.result_frame.grid_remove()  # 如果输入为空，隐藏结果区域
            return
        
        # 尝试解析输入
        try:
            # 只有当输入以"0x"开头时才按十六进制解析
            if input_text.lower().startswith('0x'):
                # 处理十六进制输入
                decimal_value = int(input_text, 16)
            else:
                # 处理字符输入
                if len(input_text) == 1:
                    decimal_value = ord(input_text)
                else:
                    self.result_frame.grid_remove()
                    return
            
            # 确保值在ASCII范围内 (0-127)
            if 0 <= decimal_value <= 127:
                self.update_result(decimal_value)
            else:
                self.update_result(decimal_value, is_extended=True)
                
        except ValueError:
            # 如果输入无法解析，隐藏结果区域
            self.result_frame.grid_remove()
    
    def update_result(self, decimal_value, is_extended=False):
        """更新结果文本区域"""
        # 启用文本区域进行编辑
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        
        # 准备结果文本
        char_repr = chr(decimal_value)
        hex_value = hex(decimal_value)
        bin_value = bin(decimal_value)
        
        # 添加基本信息
        self.result_text.insert(tk.END, f"十进制: {decimal_value}\n")
        self.result_text.insert(tk.END, f"十六进制: {hex_value}\n")
        self.result_text.insert(tk.END, f"二进制: {bin_value}\n")
        
        # 对于可打印字符，显示字符表示
        if 32 <= decimal_value <= 126:
            self.result_text.insert(tk.END, f"字符: '{char_repr}'")
        # 对于控制字符，显示描述
        elif decimal_value in self.control_chars:
            self.result_text.insert(tk.END, f"控制字符: {self.control_chars[decimal_value]}")
        else:
            self.result_text.insert(tk.END, f"字符: '{char_repr}' (非标准ASCII)")
        
        # 禁用文本区域编辑
        self.result_text.config(state=tk.DISABLED)
        
        # 显示结果区域
        self.result_frame.grid()
        
        # 调整窗口大小以适应内容
        self.update_idletasks()
        self.geometry('')

if __name__ == "__main__":
    app = ASCIIConverter()
    app.mainloop()