import os
import tkinter as tk
from tkinter import messagebox, filedialog
from pydub import AudioSegment
import random
import sys
import ctypes


# 在文件顶部添加
def resource_path(relative_path):
    """获取资源的绝对路径"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# 添加Windows API调用
myappid = 'yuri.suiwu.audio.processor.1.0'  # 可以自定义
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


class AudioProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("随舞生成器 - Yuri")

        # 初始化目录
        self.wenJian_dir = "wenJian"
        self.wenJianPin_dir = "wenJianPin"
        self.out_dir = "out"  # 修改默认输出路径
        self.countdown_file = "倒计时.mp3"
        self._create_directories()

        # 文件列表框架
        list_frame = tk.Frame(root)
        list_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        # 文件列表带滚动条
        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL)
        self.file_listbox = tk.Listbox(
            list_frame,
            width=50,
            yscrollcommand=scrollbar.set,
            selectmode=tk.SINGLE
        )
        scrollbar.config(command=self.file_listbox.yview)

        # 布局
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.file_listbox.bind("<Button-3>", self.show_context_menu)

        # 按钮行框架
        button_frame = tk.Frame(root)
        button_frame.pack(pady=5, fill=tk.X)

        # 个居中框架
        center_frame = tk.Frame(button_frame)
        center_frame.pack(side=tk.TOP, expand=True)

        # 导入文件按钮
        self.import_button = tk.Button(center_frame, text="导入文件", command=self.import_files)
        self.import_button.pack(side=tk.LEFT, padx=5)

        # 清空列表按钮
        self.clear_button = tk.Button(center_frame, text="清空列表", command=self.clear_files)
        self.clear_button.pack(side=tk.LEFT, padx=5)

        # 文件个数显示
        self.file_count_label = tk.Label(center_frame, text="文件数: 0")
        self.file_count_label.pack(side=tk.LEFT, padx=5)

        # 命名框
        name_frame = tk.Frame(root)  # 新增框架
        name_frame.pack(pady=5, fill=tk.X)

        self.name_label = tk.Label(name_frame, text="输出文件名:")
        self.name_label.pack(side=tk.LEFT)

        self.name_entry = tk.Entry(name_frame)
        self.name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # 添加输出路径选择
        path_frame = tk.Frame(root)
        path_frame.pack(pady=5, fill=tk.X)

        self.path_label = tk.Label(path_frame, text="输出路径:")
        self.path_label.pack(side=tk.LEFT)

        self.path_entry = tk.Entry(path_frame)
        self.path_entry.insert(0, self.out_dir)  # 设置默认路径
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        self.path_button = tk.Button(path_frame, text="选择...", command=self.select_output_path)
        self.path_button.pack(side=tk.RIGHT)

        # 生成歌单按钮
        self.generate_button = tk.Button(root, text="生成音频和歌单", command=self.generate_playlist)
        self.generate_button.pack(pady=10)

        # 等待框
        self.waiting_window = None

        # 最后更新文件列表
        self.update_file_list()

    def _create_directories(self):
        """创建所需的目录"""
        for dir_path in [self.wenJian_dir, self.wenJianPin_dir, self.out_dir]:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

    def update_file_list(self):
        """更新文件列表"""
        self.file_listbox.delete(0, tk.END)
        file_count = 0
        for filename in os.listdir(self.wenJian_dir):
            if filename.lower().endswith('.mp3'):
                self.file_listbox.insert(tk.END, filename)
                file_count += 1
        self.file_count_label.config(text=f"文件数: {file_count}")

    def show_context_menu(self, event):
        """显示右键菜单"""
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="删除", command=lambda: self.delete_file(event))
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def delete_file(self, event):
        """删除选中的文件"""
        selection = self.file_listbox.curselection()
        if selection:
            index = selection[0]
            filename = self.file_listbox.get(index)
            file_path = os.path.join(self.wenJian_dir, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                self.update_file_list()

    def clear_files(self):
        """清空 wenJian 目录下的所有文件"""
        result = messagebox.askyesno("确认", "确定要清空所有文件吗？")
        if result:
            for filename in os.listdir(self.wenJian_dir):
                file_path = os.path.join(self.wenJian_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            self.update_file_list()

    def import_files(self):
        """导入本地的 mp3 文件"""
        files = filedialog.askopenfilenames(filetypes=[("MP3 files", "*.mp3")])
        for file in files:
            filename = os.path.basename(file)
            dest_path = os.path.join(self.wenJian_dir, filename)
            with open(file, 'rb') as src, open(dest_path, 'wb') as dest:
                dest.write(src.read())
        self.update_file_list()

    def show_waiting_window(self):
        """显示等待框"""
        self.waiting_window = tk.Toplevel(self.root)
        self.waiting_window.title("请等待")
        tk.Label(self.waiting_window, text="正在处理，请稍候...").pack(padx=20, pady=20)
        self.waiting_window.grab_set()  # 阻止其他操作

    def hide_waiting_window(self):
        """隐藏等待框"""
        if self.waiting_window:
            self.waiting_window.destroy()
            self.waiting_window = None

    def _add_fade(self, audio_segment):
        """为音频添加淡入淡出效果"""
        # 添加2秒淡入 (2000毫秒)
        audio_with_fade = audio_segment.fade_in(2000)
        # 添加2秒淡出
        audio_with_fade = audio_with_fade.fade_out(2000)
        return audio_with_fade

    def add_countdown(self):
        """添加倒计时到每个音频文件"""
        if not os.path.exists(self.countdown_file):
            messagebox.showerror("错误", "倒计时文件不存在，请检查根目录！")
            return
        countdown = AudioSegment.from_mp3(self.countdown_file)
        for filename in os.listdir(self.wenJian_dir):
            if filename.lower().endswith('.mp3'):
                audio_path = os.path.join(self.wenJian_dir, filename)
                audio = AudioSegment.from_mp3(audio_path)
                # 先添加淡入淡出效果
                audio_with_fade = self._add_fade(audio)
                # 再拼接倒计时
                combined = countdown + audio_with_fade
                output_path = os.path.join(self.wenJianPin_dir, filename)
                combined.export(output_path, format="mp3")

    def select_output_path(self):
        """选择输出路径"""
        path = filedialog.askdirectory(initialdir=self.out_dir)
        if path:
            self.out_dir = path
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, path)

    def generate_playlist(self):
        """生成歌单"""
        output_name = self.name_entry.get()
        if not output_name:
            output_name = "随舞"
            self.name_entry.insert(0, output_name)

        # 更新输出路径
        self.out_dir = self.path_entry.get()
        if not os.path.exists(self.out_dir):
            os.makedirs(self.out_dir)

        self.show_waiting_window()
        self.root.update()
        try:
            # 添加倒计时
            self.add_countdown()

            # 获取 wenJianPin 目录下的所有 mp3 文件
            files = [f for f in os.listdir(self.wenJianPin_dir) if f.lower().endswith('.mp3')]
            if not files:
                messagebox.showerror("错误", "没有可处理的音频文件！")
                return
            random.shuffle(files)

            # 拼接音频
            combined = AudioSegment.empty()
            for filename in files:
                audio_path = os.path.join(self.wenJianPin_dir, filename)
                audio = AudioSegment.from_mp3(audio_path)
                combined += audio

            # 输出音频文件
            output_audio_path = os.path.join(self.out_dir, f"{output_name}.mp3")
            combined.export(output_audio_path, format="mp3")

            # 生成歌单文件
            output_playlist_path = os.path.join(self.out_dir, f"{output_name}.txt")
            with open(output_playlist_path, 'w', encoding='utf-8') as f:
                for filename in files:
                    # 移除.mp3后缀
                    song_name = os.path.splitext(filename)[0]
                    f.write(song_name + '\n')

            messagebox.showinfo("完成", "歌单生成成功！")
        except Exception as e:
            messagebox.showerror("错误", f"处理过程中出现错误: {str(e)}")
        finally:
            self.hide_waiting_window()


if __name__ == "__main__":
    root = tk.Tk()
    try:
        if sys.platform == 'win32':
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception as e:
        print(f"图标设置失败: {e}")
    app = AudioProcessorApp(root)
    root.mainloop()
