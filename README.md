NTPC Social System Robot
=============

![sms_logo_android](https://cloud.githubusercontent.com/assets/374786/5373220/52c7a9e2-808e-11e4-8565-ca981121353f.png)

Robot for periodically upload or download pdf files to/from ntpc social system.

自動（批次）上傳 PDF 檔案到[新北市社福資訊系統](https://social.ntpc.gov.tw/)的 Selenium 機器人。（[簡介投影片](https://docs.google.com/presentation/d/1OegbiGLZZNmpefV5Yi8UfIEokw42MvJGzMPhXCdlbHg/edit?usp=sharing)）


Usage 
-----

### PDF 檔案規範

使用前，請確定檔案是否符合下面規定：

1. PDF 檔名結尾是 `身分證字號.pdf`。例：`a123456789.pdf` 或 `張某某-a123456789.pdf` 或 `切結書.a123456789.pdf`。
2. 個案已經在社福系統中建檔。也就是說，持檔名的身分證字號至社福資訊系統查詢，應該可以找得到人。


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


Setup
-----

不幸地是，社政系統網頁有一部分使用 ActiveX，故目前系統只能在 Windows 上面才能運行。

### 1. 在 Windows 上安裝 Python

[去官網下載 Python 2.7](https://www.python.org/downloads/) 並安裝（一直下一步就好）。

接下來將 Python 的 binary 資料夾 `C:\python27` 與 `C:\python27\lib` 塞進 `PATH` 環境變數。設定好之後，應該就可以在命令提示字元直接打 `python` 與 `pip` 指令。


### 2. 安裝 dependency

打開命令提示字元，`cd` 到專案目錄，然後執行：

```
pip install -r requirements.txt
```

這個指令會安裝此程式所需的 python library。


### 3. 設定 Selenium Internet Explorer Driver

以下要點整理自[官方文件](https://code.google.com/p/selenium/wiki/InternetExplorerDriver#Required_Configuration)。

* 下載[最新版的 IEDriverServer](http://selenium-release.storage.googleapis.com/index.html)，將解壓後的 `IEDriverServer.exe` 置放在 `PATH` 環境變數中有指定的目錄下（`system32` 目錄，或者是前一步驟設定好的 `C:\python27` 都可以）。
* Windows Vista 以上的電腦，`控制台`（或 IE 的工具選單） > `網際網路設定` > 「`安全性`」頁籤 > `啟用受保護模式` 的設定，在不同區域（「網際網路」、「近端內部網路」、「信任的網站」或「封鎖的網站」）之間必須一致（要開就通通打勾，要關就通通不打勾）
* 承上點，若使用的是 IE10+，「啟用受保護模式」必須關閉。
* 瀏覽器縮放必須設定在 100%。
* 若 IE 版本為 11，需要在 Registry 裡面新增一個 `DWORD`，名稱為`iexplore.exe`、值為 `0`。Registry 位置：32 位元 Windows 為`HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Internet Explorer\Main\FeatureControl\FEATURE_BFCACHE`，而 64 位元 Windows 為 `HKEY_LOCAL_MACHINE\SOFTWARE\Wow6432Node\Microsoft\Internet Explorer\Main\FeatureControl\FEATURE_BFCACHE`。若 `FEATURE_BFCACHE` 不存在，就自己建立一個。


### 4. 設定 credential

將專案目錄下的 `social_credentials.py.sample` 更名為 `social_credentials.py`。填入用於登入社政系統的資訊。

Python 的 Windows installer 會安裝 [IDLE 文字編輯器](https://en.wikipedia.org/wiki/IDLE_(Python))，可以直接使用 IDLE 編輯。


Troubleshooting
------------

### `DEBUG` flag
`settings.py` 裡面有一個 `DEBUG` 變數，預設為 `False`，執行時會隱藏任何 exception。若程式無法正常運行，可以將 `DEBUG` 設為 `True` 以利除錯。


### IE11 登入社政系統後停止動作

若程式可以正常打開 IE11 瀏覽器、輸入帳號密碼，但登入後就沒有動作了，請解除安裝 Windows 更新檔 KB3025390 。（參考資料：[StackOverflow](http://stackoverflow.com/questions/28069064/selenium-scripts-fail-after-newest-windows-update)、[移除特定 Windows Update 教學](http://lifehacker.com/how-to-uninstall-a-windows-update-that-broke-something-1676817197)）
