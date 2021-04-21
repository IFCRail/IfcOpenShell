# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller import HOMEPATH
block_cipher = None

a = Analysis(['guiplus.py'],
             pathex=[],
             binaries=[],
             datas=[(os.path.join(HOMEPATH,'shiboken2'), 'shiboken2'), (os.path.join(HOMEPATH,'ifcopenshell'), 'ifcopenshell'), ('.\\bimtester\\features', 'features'), 
             ('.\\bimtester\\resources', 'resources'), ('.\\bimtester\\locale', 'locale'), ('.\\bimtester\\guiplus\\resources', 'guiplus\\resources')],
             hiddenimports=['behave.formatter.pretty','behave.formatter.json','numpy','pyparsing','bimtester.util','bimtester.table','bimtester.run','bimtester.reports','bimtester.clean','bimtester.ifc'],
             hookspath=[],
             runtime_hooks=None,
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='bimtesterplus',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
          icon=os.path.join('bimtester', 'resources', 'icons', 'bimtester.ico') 
          )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='bimtesterplus',
               icon=os.path.join('bimtester', 'resources', 'icons', 'bimtester.ico')
            )
