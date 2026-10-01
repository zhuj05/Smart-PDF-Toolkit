# Smart-PDF-Toolkit

# 📄 Smart PDF Toolkit
## English

> A lightweight, efficient, and privacy-first PDF utility toolkit designed for merging, precise splitting, page adjustments, security encryption, and dynamic watermarking.

[![License](https://img.shields.io/badge/License-All_Rights_Reserved-red.svg)](#-license)

### 🌟 Key Features

* **🔒 100% Local & Privacy-Safe**: All PDF operations run locally within your browser or native client. Files are **never uploaded** to any external server.
* **⚡ Pure Python Full-Stack**: Built with modern, responsive Flet UI and powered by Pyodide for serverless execution in static web environments.
* **🛠️ Modular Architecture**: Complete decoupling of the UI from business logic—`PDFEngine` can be seamlessly integrated into CLI tools, desktop apps, or automated workflows.

### 🚀 Highlights

* **Merge**: Combine multiple PDF files sequentially into a single unified document.
* **Split**: Extract specific pages or intervals using intuitive page-range syntax (e.g., `1-3, 5`).
* **Page Adjustments (Rotate & Crop)**:
  * Rotate pages at 90°, 180°, or 270° clockwise and counter-clockwise.
  * Custom margin cropping via `MediaBox` and `CropBox` manipulation.
* **Text Extraction**: One-click batch extraction and preview of plain text layers from documents.
* **Security**: Protect PDFs with standard password encryption or decrypt secured files.
* **Metadata & Watermark**:
  * View and update document metadata entries (e.g., `/Title`, `/Author`).
  * Apply custom semi-transparent diagonal text watermarks dynamically.

### 📌 About This Project

`Smart-PDF-Toolkit` was created to provide a lightweight, privacy-focused tool that handles PDF tasks entirely in your browser without any server uploads.

Please note that this project focuses on page-level operations (such as merging, splitting, and rotating) as well as basic text extraction. **It currently does not support table recognition, layout parsing, or format conversion (e.g., extracting structured tables to Excel).**

As this is maintained as a personal side project, updates and feature requests may be limited. Thank you for your understanding!


### 🛠️ Tech Stack

* **GUI / Frontend**: [Flet](https://flet.dev/)
* **PDF Core Engine**: [pypdf](https://pypdf.readthedocs.io/)
* **Vector Graphics & Watermarking**: [ReportLab](https://www.reportlab.com/)
* **Web Runtime Compatibility**: Pyodide + micropip dynamic package loader

### 📂 Project Structure

```text
├── main.py              # Application entry point: UI rendering, state management, and events
├── requirements.txt     # Python package dependencies
├── README.md            # Project documentation (Bilingual: Traditional Chinese & English)
├── LICENSE              # Licensing and distribution terms
└── src/
    ├── __init__.py      # Package indicator
    ├── installer.py     # Dynamic package installer for Web / Pyodide runtime
    └── pdf_engine.py    # Stateless PDF manipulation engine
```

<h3 align=left>Support</h3>
<a href="https://www.buymeacoffee.com/zhuj70553" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>
