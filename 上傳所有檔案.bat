@echo off
SET PATH=%PATH%;C:\python27

echo 上傳「低收入戶」案件......
python lib/app.py reset-fail 低收
python lib/app.py batchupload -t lowIncome 低收

echo 上傳「中低收入戶」案件......
python lib/app.py reset-fail 中低收
python lib/app.py batchupload -t mediumIncome 中低收

echo 上傳「中低收入老人」案件......
python lib/app.py reset-fail 中低老人
python lib/app.py batchupload -t mediumIncomeOld 中低老人

echo 上傳「身障」案件......
python lib/app.py reset-fail 身障
python lib/app.py batchupload -t disability 身障

echo 上傳「兒少」案件......
python lib/app.py reset-fail 兒少
python lib/app.py batchupload -t poorKid 兒少

echo 上傳完成，可以打開資料夾看看結果囉！:)
pause
