NTPC Social System Robot
=============

![sms_logo_android](https://cloud.githubusercontent.com/assets/374786/5373220/52c7a9e2-808e-11e4-8565-ca981121353f.png)

Robot for periodically upload or download pdf files to/from ntpc social system.

自動（批次）上傳 PDF 檔案到[新北市社福資訊系統](https://social.ntpc.gov.tw/)的 Selenium 機器人。（[簡介投影片](https://docs.google.com/presentation/d/1OegbiGLZZNmpefV5Yi8UfIEokw42MvJGzMPhXCdlbHg/edit?usp=sharing)）


Usage
-----

### 使用步驟

1. 將 PDF 檔案分放在「低收」、「中低收」、「中低老人」、「身障」、「兒少」5 個資料夾。
2. 雙擊「`上傳所有檔案.bat`」以上上述 5 資料夾內的檔案，程式將會自動登入社政系統並執行上傳。
3. 上傳完成後，「低收」、「中低收」、「中低老人」、「身障」、「兒少」五個資料夾中的檔案名稱後應該都已被標上 `-done` 或 `failed`。被標上 `-done` 的檔案可以被安全刪除；再次執行 `.bat` 檔則可重新上傳被標上 `failed` 的檔案。

### PDF 命名規範

使用前，請確定檔案是否符合下面規定：

1. PDF 檔名結尾是 `身分證字號.pdf`。例：`a123456789.pdf` 或 `張某某-a123456789.pdf` 或 `切結書.a123456789.pdf`。
2. 個案已經在社福系統中建檔。也就是說，持檔名的身分證字號至社福資訊系統查詢，應該可以找得到人。


Setup
-----

不幸地是，社政系統網頁有一部分使用 ActiveX，故目前系統只能在 Windows 上面才能運行。

### 1. 在 Windows 上安裝 Python

[去官網下載 Python 2.7](https://www.python.org/downloads/) 並安裝（一直下一步就好）。
安裝完成後，C 槽底下應該會多一個 `python27` 資料夾。

### 2. 下載本專案並安裝 dependency

首先，請先安裝 Windows update KB2704299 [32bit](http://hotfixv4.microsoft.com/Windows%207/Windows%20Server2008%20R2%20SP1/sp2/Fix387976/7600/free/448094_intl_i386_zip.exe) / [64bit](http://hotfixv4.microsoft.com/Windows%207/Windows%20Server2008%20R2%20SP1/sp2/Fix387976/7600/free/448095_intl_x64_zip.exe)，使 Windows 可以正確解壓縮含有 UTF-8 檔案名稱的 zip 檔（需要重新開機）。

接著，點擊 Github 右邊的「Download ZIP」下載本專案，解壓縮到桌面上，然後改名成任何方便的名字。

最後，點兩下 `INSTALL/dependency.bat` 開始安裝系統需要的 dependency。

### 3. 設定 Selenium Internet Explorer Driver

以下要點整理自[官方文件](https://code.google.com/p/selenium/wiki/InternetExplorerDriver#Required_Configuration)。

* 依照「IE 的位元版本」﹙通常是 **32 位元** IE﹚下載[最新版的 IEDriverServer](http://selenium-release.storage.googleapis.com/index.html)，將解壓後的 `IEDriverServer.exe` 置放在 `PATH` 環境變數中有指定的目錄下（`system32` 目錄，或者是 `C:\python27` 都可以）。
* Windows Vista 以上的電腦，`控制台`（或 IE 的工具選單） > `網際網路設定` > 「`安全性`」頁籤 > `啟用受保護模式` 的設定，在不同區域（「網際網路」、「近端內部網路」、「信任的網站」或「封鎖的網站」）之間必須一致（要開就通通打勾，要關就通通不打勾）
* 承上點，若使用的是 IE10+，「啟用受保護模式」必須關閉。
* 瀏覽器縮放必須設定在 100%。
* 若 IE 版本為 11 且為 32bit Windows，請點兩下 `INSTALL/32bit_ie11.reg`；若 IE 版本為 11 且為 64bit Windows，請點兩下 `INSTALL/64bit_ie11.reg`。

以上設定完成後，可以刪除 `INSTALL` 資料夾、`.gitattributes`、`.gitignore`、`LICENSE` 以及 `README.md`。

### 4. 設定 credential

將 `lib/social_credentials.py.sample` 更名為 `lib/social_credentials.py`。打開此檔，填入用於登入社政系統的資訊。

Python 的 Windows installer 會安裝 [IDLE 文字編輯器](https://en.wikipedia.org/wiki/IDLE_(Python))，可以直接使用 IDLE 編輯。


Troubleshooting
------------

### `DEBUG` flag
`settings.py` 裡面有一個 `DEBUG` 變數，預設為 `False`，執行時會隱藏任何 exception。若程式無法正常運行，可以將 `DEBUG` 設為 `True` 以利除錯。


### IE11 登入社政系統後停止動作

若程式可以正常打開 IE11 瀏覽器、輸入帳號密碼，但登入後就沒有動作了，請解除安裝 Windows 更新檔 KB3025390 。（參考資料：[StackOverflow](http://stackoverflow.com/questions/28069064/selenium-scripts-fail-after-newest-windows-update)、[移除特定 Windows Update 教學](http://lifehacker.com/how-to-uninstall-a-windows-update-that-broke-something-1676817197)）


### Windows 防火牆問題

一開始執行程式時，Windows 防火牆可能會阻擋 IEDriverServer 存取網路。請在 `控制台 / Windows 防火牆 / 允許程式通過 Windows 防火牆通訊` 之中，允許 `Command line server for the IE driver` 的所有功能。

![Windows firewall settings](http://i.imgur.com/CfyVGKX.png)


### IE 視窗打開又停止回應。點擊「錯誤詳細資訊」，問題事件名稱為 `APPCRASH`。

可能是 IEDriverServer.exe 的位元版本（32bit 或 64 bit）與 Selenium 所啟動的 IE 位元版本不合。請更換 IEDriverServer.exe 的位元版本，再試試看。

ntpc_social_robot/lib/app.py CLI Reference
------------------------------------------

若需直接使用命令提示字元操作機器人，以下是可用的命令行指令。

### `upload`：上傳單一 PDF

```
python app.py upload -t=<upload-type> <path-to-file>
```

* `-t, --upload_type`：個案類別。可能值：`lowIncome`（低收）、`mediumIncome`（中低收）、`mediumIncomeOld`（中低老人）, `disability`（身障）, `poorKid`（兒少）
* `path-to-file` PDF 檔案路徑。檔名需符合規範。

### `batchupload`：上傳目錄下所有 PDF（含子目錄）

```
python app.py batchupload -t=<upload-type> <path-to-directory>
```

同「單一上傳 PDF」。

由於目錄下所有檔案都會視為同一個個案類別（`upload-type`），因此我們建議將不同類別的 PDF 檔分開存放、分次執行 `batchupload`。


### `reset-fail`： 重設上傳失敗標記

執行過 `upload` 或 `batchupload` 後，程式會將上傳成功的檔案檔名後面加上`-done`，而上傳失敗的檔案檔名後面會加上 `-failed`。`batchupload` 並不會處理加過 `-done` 或 `-failed` 的檔案，故若需要使用 `batchupload` 重新上傳，就必須要清除目錄下所有失敗檔案的 `-failed` 標記。下面指令可以快速清除目錄中，每個檔名的「`-failed`」後綴，但不會動檔名以 `-done` 結尾的檔案。

```
python app.py reset-fail <path-to-directory>
```



Contributors
----------

* 138T Colin Su [@littleq0903](https://github.com/littleq0903)
* 149T Johnson Liang [@MrOrz](https://github.com/MrOrz)
