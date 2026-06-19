# BookConverter - 电子书格式转换器

跨平台电子书格式转换工具，支持 Windows EXE 和 Android APK。

## 功能特性

- 支持格式：EPUB、MOBI、AZW3、TXT、PDF、MD
- 格式相互转换
- 批量转换
- 中英双语界面
- 自动编码检测（防乱码）
- 目录结构保留

## 快速开始

### Windows EXE
直接运行 `dist/BookConverter.exe`

### 从源码运行
```bash
pip install -r requirements.txt
python main_tk.py
```

## 构建

### Windows EXE
```bash
pip install pyinstaller
python -m PyInstaller --clean --noconfirm BookConverter.spec
```

### Android APK
推送到GitHub后自动构建，或使用Google Colab。

## 项目结构

```
ebook_converter/
├── core/           # 核心模型和转换引擎
├── readers/        # 格式读取器
├── writers/        # 格式写入器
├── i18n/           # 国际化语言包
└── ui/             # 用户界面
```

## 版本

- v1.1.0 - 支持全部6种格式
- v1.0.0 - 初始版本（EPUB/MOBI/TXT）
