# モジュールのインポート
import os
import glob
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
import cv2
from PIL import Image
import numpy as np

# アプリケーションクラスの定義
class App:
    # アプリケーションGUIの初期化
    def __init__(self, root):
        self.root = root
        self.root.title("Image to Mp4")
        
        # ボタンとテキストエントリーの作成
        self.select_button = ttk.Button(
            root, text="画像フォルダ選択", command=self.select_directory
        )
        self.select_button.grid(row=0, column=0, padx=10, pady=10)
        
        self.folder_label = ttk.Label(root, text="")
        self.folder_label.grid(row=0, column=1, padx=10, pady=10)

        self.fps_label = ttk.Label(root, text="FPS/Hz:")
        self.fps_label.grid(row=1, column=0, padx=10, pady=10, sticky=tk.E)

        self.fps_entry = ttk.Entry(root)
        self.fps_entry.grid(row=1, column=1, padx=10, pady=10)
        self.fps_entry.insert(0, "10")

        self.start_button = ttk.Button(
            root, text="変換開始", command=self.convert
        )
        self.start_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

        self.progress = ttk.Progressbar(
            root, orient="horizontal", length=300, mode="determinate"
        )
        self.progress.grid(row=3, column=0, columnspan=2, padx=10, pady=10)


    # フォルダ選択ダイアログを表示する関数
    def select_directory(self):
        # filedialog.askdirectoryでフォルダ選択ダイアログを表示
        self.directory = filedialog.askdirectory(title="画像フォルダを選択")
        if not self.directory:
            return

        # フォルダ名を表示(10文字以上は...で省略)
        folder_name = os.path.basename(self.directory)
        self.output_name = folder_name
        if len(folder_name) > 10:
            folder_name = folder_name[:10] + "..."

        self.folder_label["text"] = folder_name 


    # image to mp4変換処理を行う関数
    def convert(self):
        if not hasattr(self, 'directory'):
            # フォルダが選択されていない場合はエラーメッセージを表示
            messagebox.showinfo(
            "Error", 
            "フォルダが選択されていません"
            )
            return

        # .jpg と .png のファイルを取得
        jpg_filepaths = glob.glob(os.path.join(self.directory, "*.jpg"))
        png_filepaths = glob.glob(os.path.join(self.directory, "*.png"))

        # 2つのリストを結合してソート
        filepaths = sorted(jpg_filepaths + png_filepaths)
        
        if not filepaths:
            # ファイルが存在しない場合はエラーメッセージを表示
            messagebox.showinfo(
            "Error", 
            "指定されたフォルダにはjpg/pngファイルがありません"
            )
            return


        # スクリプトの実行場所（ディレクトリ）を取得
        script_directory = os.path.dirname(os.path.abspath(__file__))
        output_directory = os.path.join(script_directory, 'output')

        # output ディレクトリが存在するか確認し、存在しない場合は作成
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
            
        # 出力ファイルのパスを設定
        output_filepath = os.path.join(output_directory, f"{self.output_name}.mp4")

        fps = int(self.fps_entry.get() or 10)
        # img = cv2.imread(filepaths[0])
        # h, w, layers = img.shape
        pil_img = Image.open(filepaths[0])
        img = np.array(pil_img)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        h, w, layers = img.shape
        size = (w, h)

        # スクリプトと同じ階層のoutputフォルダにoutput.mp4を保存
        out = cv2.VideoWriter(
            output_filepath, 
            cv2.VideoWriter_fourcc(*'mp4v'), fps, size
        )

        total_files = len(filepaths)
        for idx, filename in enumerate(filepaths):
            # PILを使用して画像を読み込む
            # 2bit文字がpathに含まれるとエラーが発生する対策
            pil_img = Image.open(filename)
            # PILの画像をNumPy配列に変換
            img = np.array(pil_img)
            # BGR形式に変換（OpenCVはBGR形式を使用するため）
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            out.write(img)

            # Update progress
            self.progress["value"] = (idx+1) / total_files * 100
            self.root.update_idletasks()

        out.release()

        # 処理完了のメッセージボックスを表示
        messagebox.showinfo(
            "Successfully", 
            "処理が完了しました。終了する際は[✕]を、続けて処理する際はもう一度選択してください"
        )
        
        self.initialize()


    # 再度処理を行うための初期化を行う関数
    def initialize(self):
        # 初期化処理
        self.progress["value"] = 0
        self.folder_label["text"] = ""


# tkのGUIウインドウを中央に配置する関数
def center_window(root):
    # ウィンドウを表示する前に更新して正確なサイズ情報を取得
    root.update_idletasks()

    # ウィンドウの幅と高さを取得
    width = root.winfo_width()
    height = root.winfo_height()

    # 画面の幅と高さを取得
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # ウィンドウの左上のx, y座標を計算
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    # ウィンドウの位置を設定
    root.geometry(f'{width}x{height}+{x}+{y}')


if __name__ == "__main__":
    # tkクラスのインスタンス生成を行い、オブジェクトをrootに格納
    root = tk.Tk()
    # rootを引数にAppクラスのインスタンスを生成
    app = App(root)
    # ウインドウを中央に配置
    center_window(root)
    # tkinterのループ処理開始
    root.mainloop()
