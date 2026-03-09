# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for Document Image Search — single-folder Windows build."""

import os
import sys
import glob
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None

# Collect hidden imports that PyInstaller may miss
hidden_imports = (
    collect_submodules("uvicorn")
    + collect_submodules("fastapi")
    + collect_submodules("pydantic")
    + collect_submodules("pydantic_settings")
    + collect_submodules("cv2")
    + [
        "multipart",
        "multipart.multipart",
        "pdf2image",
        "PIL",
    ]
)

# Data files: frontend build, and any data files needed by dependencies
datas = []
frontend_dist = os.path.join("backend", "frontend_dist")
if os.path.isdir(frontend_dist):
    datas.append((frontend_dist, "frontend_dist"))

# Bundle poppler binaries for Windows PDF support.
# POPPLER_PATH env var should point to the directory containing pdftoppm.exe.
poppler_binaries = []
poppler_path = os.environ.get("POPPLER_PATH", "")
if poppler_path and os.path.isdir(poppler_path):
    for f in glob.glob(os.path.join(poppler_path, "*")):
        if os.path.isfile(f):
            poppler_binaries.append((f, "poppler"))

a = Analysis(
    [os.path.join("backend", "main.py")],
    pathex=[os.path.join(os.path.dirname(os.path.abspath(SPEC)), "backend")],
    binaries=poppler_binaries,
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="DocumentImageSearch",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="DocumentImageSearch",
)
