# 📄 Smart PDF Toolkit

[繁體中文](https://github.com/zhuj05/Smart-PDF-Toolkit/blob/main/README.md) | [English](https://github.com/zhuj05/Smart-PDF-Toolkit/blob/main/english_readme.md)

---

## 🇹🇼 繁體中文

> 一款輕量、高效且注重隱私的純前端 PDF 處理工具箱，支援多檔合併、精準拆分、頁面微調、安全加密與動態浮水印。

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Flet](https://img.shields.io/badge/UI-Flet-blueviolet.svg)](https://flet.dev/)
[![pypdf](https://img.shields.io/badge/Engine-pypdf-brightgreen.svg)](https://pypdf.readthedocs.io/)
[![License](https://img.shields.io/badge/License-All_Rights_Reserved-red.svg)](#-版權與授權宣告-license)

### 🌟 核心特色

* **🔒 100% 本地與隱私安全**：所有 PDF 處理運算皆於使用者瀏覽器／本機環境內完成，檔案**絕不上傳**至任何外部伺服器。
* **⚡ 純 Python 全端架構**：以 Flet 打造現代化響應式 UI，結合 Pyodide 實現 Web 靜態環境無伺服器運行。
* **🛠️ 模組化引擎**：UI 與商業邏輯徹底解耦，`PDFEngine` 可無縫移植至 CLI、桌面版或自動化腳本。

### 🚀 功能亮點

* **多檔合併 (Merge)**：支援將多份 PDF 檔案依序拼接為單一文件。
* **精準拆分 (Split)**：自訂頁碼範圍（支援語法如 `1-3, 5`）提取指定頁面。
* **頁面微調 (Rotate & Crop)**：
  * 支援 90°、180°、270° 順時針與逆時針旋轉。
  * 支援自訂四邊邊距裁切 (MediaBox / CropBox)。
* **內容提取 (Extract)**：一鍵批次解析並預覽 PDF 內部純文字層。
* **隱私安全 (Security)**：支援密碼加密保護與已加密文件之解密操作。
* **自訂資料 (Metadata & Watermark)**：
  * 修改文件詮釋資料（標題 `/Title`、作者 `/Author` 等）。
  * 動態套用 45 度半透明文字防偽浮水印。

### 🛠️ 技術堆疊

* **前端介面 (GUI)**：[Flet](https://flet.dev/)
* **PDF 核心運算**：[pypdf](https://pypdf.readthedocs.io/)
* **向量繪圖與浮水印**：[ReportLab](https://www.reportlab.com/)
* **Web 環境相容**：Pyodide + micropip 動態模組載入器

### 📂 專案結構

```text
├── main.py              # 應用程式入口：UI 渲染、狀態管理與事件排程
├── requirements.txt     # 相依套件清單
├── README.md            # 專案說明文件 (中英雙語)
├── LICENSE              # 版權宣告文件
└── src/
    ├── __init__.py      # 套件模組宣告
    ├── installer.py     # Web/Pyodide 環境相容套件動態安裝器
    └── pdf_engine.py    # PDF 處理無狀態運算引擎
