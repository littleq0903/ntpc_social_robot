@echo off
SET PATH=%PATH%;C:\python27

echo �W�ǡu�C���J��v�ץ�......
python lib/app.py reset-fail �C��
python lib/app.py batchupload -t lowIncome �C��

echo �W�ǡu���C���J��v�ץ�......
python lib/app.py reset-fail ���C��
python lib/app.py batchupload -t mediumIncome ���C��

echo �W�ǡu���C���J�ѤH�v�ץ�......
python lib/app.py reset-fail ���C�ѤH
python lib/app.py batchupload -t mediumIncomeOld ���C�ѤH

echo �W�ǡu���١v�ץ�......
python lib/app.py reset-fail ����
python lib/app.py batchupload -t disability ����

echo �W�ǡu��֡v�ץ�......
python lib/app.py reset-fail ���
python lib/app.py batchupload -t poorKid ���

echo �W�ǧ����A�i�H���}��Ƨ��ݬݵ��G�o�I:)
pause
