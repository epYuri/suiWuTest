import os
import tkinter as tk
from tkinter import messagebox, filedialog
from pydub import AudioSegment
import random
import ctypes


myappid = 'yuri.suiwu.audio.processor.1.0'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


class AudioProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("随舞生成器 - Yuri")
        self.wenJian_dir = "wenJian"
        self.wenJianPin_dir = "wenJianPin"
        self.out_dir = "out"
        self.countdown_file = "倒计时.mp3"
        self._create_directories()
        list_frame = tk.Frame(root)
        list_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL)
        self.file_listbox = tk.Listbox(
            list_frame,
            width=50,
            yscrollcommand=scrollbar.set,
            selectmode=tk.SINGLE
        )
        scrollbar.config(command=self.file_listbox.yview)
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_listbox.bind("<Button-3>", self.show_context_menu)
        button_frame = tk.Frame(root)
        button_frame.pack(pady=5, fill=tk.X)
        center_frame = tk.Frame(button_frame)
        center_frame.pack(side=tk.TOP, expand=True)
        self.import_button = tk.Button(center_frame, text="导入文件", command=self.import_files)
        self.import_button.pack(side=tk.LEFT, padx=5)
        self.clear_button = tk.Button(center_frame, text="清空列表", command=self.clear_files)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        self.file_count_label = tk.Label(center_frame, text="文件数: 0")
        self.file_count_label.pack(side=tk.LEFT, padx=5)
        name_frame = tk.Frame(root)
        name_frame.pack(pady=5, fill=tk.X)
        self.name_label = tk.Label(name_frame, text="输出文件名:")
        self.name_label.pack(side=tk.LEFT)
        self.name_entry = tk.Entry(name_frame)
        self.name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        path_frame = tk.Frame(root)
        path_frame.pack(pady=5, fill=tk.X)
        self.path_label = tk.Label(path_frame, text="输出路径:")
        self.path_label.pack(side=tk.LEFT)
        self.path_entry = tk.Entry(path_frame)
        self.path_entry.insert(0, self.out_dir)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.path_button = tk.Button(path_frame, text="选择...", command=self.select_output_path)
        self.path_button.pack(side=tk.RIGHT)
        self.generate_button = tk.Button(root, text="生成音频和歌单", command=self.generate_playlist)
        self.generate_button.pack(pady=10)
        self.waiting_window = None
        self.update_file_list()

    def _create_directories(self):
        for dir_path in [self.wenJian_dir, self.wenJianPin_dir, self.out_dir]:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

    def update_file_list(self):
        self.file_listbox.delete(0, tk.END)
        file_count = 0
        for filename in os.listdir(self.wenJian_dir):
            if filename.lower().endswith('.mp3'):
                self.file_listbox.insert(tk.END, filename)
                file_count += 1
        self.file_count_label.config(text=f"文件数: {file_count}")

    def show_context_menu(self, event):
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="删除", command=lambda: self.delete_file(event))
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def delete_file(self, event):
        selection = self.file_listbox.curselection()
        if selection:
            index = selection[0]
            filename = self.file_listbox.get(index)
            file_path = os.path.join(self.wenJian_dir, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                self.update_file_list()

    def clear_files(self):
        result = messagebox.askyesno("确认", "确定要清空所有文件吗？")
        if result:
            for filename in os.listdir(self.wenJian_dir):
                file_path = os.path.join(self.wenJian_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            self.update_file_list()

    def import_files(self):
        files = filedialog.askopenfilenames(filetypes=[("MP3 files", "*.mp3")])
        for file in files:
            filename = os.path.basename(file)
            dest_path = os.path.join(self.wenJian_dir, filename)
            with open(file, 'rb') as src, open(dest_path, 'wb') as dest:
                dest.write(src.read())
        self.update_file_list()

    def show_waiting_window(self):
        self.waiting_window = tk.Toplevel(self.root)
        self.waiting_window.title("请等待")
        tk.Label(self.waiting_window, text="正在处理，请稍候...").pack(padx=20, pady=20)
        self.waiting_window.grab_set()

    def hide_waiting_window(self):
        if self.waiting_window:
            self.waiting_window.destroy()
            self.waiting_window = None

    def _add_fade(self, audio_segment):
        audio_with_fade = audio_segment.fade_in(2000)
        audio_with_fade = audio_with_fade.fade_out(2000)
        return audio_with_fade

    def add_countdown(self):
        if not os.path.exists(self.countdown_file):
            messagebox.showerror("错误", "倒计时文件不存在，请检查根目录！")
            return
        countdown = AudioSegment.from_mp3(self.countdown_file)
        for filename in os.listdir(self.wenJian_dir):
            if filename.lower().endswith('.mp3'):
                audio_path = os.path.join(self.wenJian_dir, filename)
                audio = AudioSegment.from_mp3(audio_path)
                audio_with_fade = self._add_fade(audio)
                combined = countdown + audio_with_fade
                output_path = os.path.join(self.wenJianPin_dir, filename)
                combined.export(output_path, format="mp3")

    def select_output_path(self):
        path = filedialog.askdirectory(initialdir=self.out_dir)
        if path:
            self.out_dir = path
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, path)

    def generate_playlist(self):
        output_name = self.name_entry.get()
        if not output_name:
            output_name = "随舞"
            self.name_entry.insert(0, output_name)

        self.out_dir = self.path_entry.get()
        if not os.path.exists(self.out_dir):
            os.makedirs(self.out_dir)

        self.show_waiting_window()
        self.root.update()
        try:
            self.add_countdown()

            files = [f for f in os.listdir(self.wenJianPin_dir) if f.lower().endswith('.mp3')]
            if not files:
                messagebox.showerror("错误", "没有可处理的音频文件！")
                return
            random.shuffle(files)

            combined = AudioSegment.empty()
            for filename in files:
                audio_path = os.path.join(self.wenJianPin_dir, filename)
                audio = AudioSegment.from_mp3(audio_path)
                combined += audio
            output_audio_path = os.path.join(self.out_dir, f"{output_name}.mp3")
            combined.export(output_audio_path, format="mp3")
            output_playlist_path = os.path.join(self.out_dir, f"{output_name}.txt")
            with open(output_playlist_path, 'w', encoding='utf-8') as f:
                for filename in files:
                    song_name = os.path.splitext(filename)[0]
                    f.write(song_name + '\n')
            messagebox.showinfo("完成", "歌单生成成功！")
        except Exception as e:
            messagebox.showerror("错误", f"处理过程中出现错误: {str(e)}")
        finally:
            self.hide_waiting_window()


if __name__ == "__main__":
    root = tk.Tk()
    app = AudioProcessorApp(root)
    root.mainloop()
