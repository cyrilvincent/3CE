echo run from root directory with specs/build.bat
pyinstaller --noconfirm specs/npnearest.spec
pyinstaller --noconfirm specs/npcompare.spec
pyinstaller --noconfirm specs/nppredict.spec
md dist\npnearest\html
copy html\*.* dist\npnearest\html\.
copy dist\npcompare\npcompare.exe dist\npnearest\.
copy dist\nppredict\nppredict.exe dist\npnearest\.
md dist\npnearest\data
copy data\data.h.pickle dist\npnearest\data\.
copy data\data.linux.h.pickle dist\npnearest\data\.
md dist\npnearest\doc
copy doc\* dist\npnearest\doc\.
copy dist\VC_redist.x64.exe dist\npnearest\.


