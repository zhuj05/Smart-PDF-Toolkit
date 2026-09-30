#這個檔案告訴 Python 「src 是一個可被匯入的套件模組 (Package)」。

#加上後，你在 main.py 裡面就可以使用標準的模組匯入語法

from src.installer import setup_environment
from src.pdf_engine import PDFEngine