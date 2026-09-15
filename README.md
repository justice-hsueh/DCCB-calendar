# DCCB-calendar

竹小兒樂公開行事曆。網站資料由「竹小兒樂」Google 日曆自動同步。

## 自動同步設定

1. 在 Google 日曆設定中，找到竹小兒樂專用日曆的「整合日曆」。
2. 複製「iCal 格式的私密網址」。請勿把網址貼在公開檔案或對話中。
3. 在本 repository 的 Settings → Secrets and variables → Actions 建立 repository secret：
   `GOOGLE_CALENDAR_ICAL_URL`
4. 到 Actions → Sync Google Calendar，手動執行一次確認設定。

設定完成後，GitHub 每 15 分鐘檢查一次；資料有變更時會更新
`events.json`，接著由 GitHub Pages 自動發布。
