echo run from *.py directory with specs/build.bat
dir
pyinstaller --noconfirm specs/npnearest.spec
pyinstaller --noconfirm specs/npcompare.spec
pyinstaller --noconfirm specs/nppredict.spec
copy dist\npcompare\npcompare.exe dist\npnearest\.
copy dist\nppredict\nppredict.exe dist\npnearest\.
md dist\npnearest\data
copy data\data.h.pickle dist\npnearest\data\.