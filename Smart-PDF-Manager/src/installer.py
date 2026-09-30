# src/installer.py
#(負責處理環境與套件下載)
#專門用來處理網頁端 Pyodide 的套件安裝，讓主程式不再充斥環境相容程式碼
import sys

async def setup_environment():
    """檢測是否運行於 Web/Pyodide 環境，若是則動態安裝套件"""
    if "pyodide" in sys.modules:
        import micropip
        await micropip.install(['pypdf', 'reportlab'])
        print("Web 環境套件安裝完成！")