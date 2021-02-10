# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['cli.py'],
             pathex=[],
             binaries=[],
             datas=[('D:\\Job\\libraries\\Python\\Python38\\Lib\\site-packages\\ifcopenshell', 'ifcopenshell'), ('.\\bimtester\\features', 'features'), ('.\\bimtester\\resources', 'resources'), ('.\\bimtester\\locale', 'locale')],
             hiddenimports=['behave.formatter.pretty','behave.formatter.json','numpy','pyparsing'],
             hookspath=[],
             runtime_hooks=None,
             excludes=['PySide2','PyQt5', 'PyQt4'],
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
          name='bimtester',
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
               name='bimtester',
               icon=os.path.join('bimtester', 'resources', 'icons', 'bimtester.ico')
            )
