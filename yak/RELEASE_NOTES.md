# BottleThread v0.1.0-beta.3 — 自動載入 Rhino 腳本服務

針對「必須先執行 ScriptEditor，BottleThread 才能開啟」的問題，補上明確載入 Rhino 內建腳本服務的步驟。

## 更新

下載 `bottlethread-0.1.0-beta.3-rh8_35-any.yak` 安裝後，**完全關閉並重新啟動 Rhino**，直接輸入 `BottleThread`。
正常使用無需先手動開啟 ScriptEditor。首次 Python 初始化可能需要等待。
需要 Rhino 8.35+；同一套件支援 Mac／Windows 的 net7.0／net48 環境。

## 修正

- 先明確載入內建 RhinoCodePlugin，註冊腳本語言服務。
- 載入成功才派送 ScriptEditor 的腳本執行入口；載入失敗會停止並提示查看 RhinoCodeLogs。
- 保留 ScriptRunner 標記及明確 Python 3 語言宣告。
- 幾何生成、預設規格與面板參數未改動。

## 驗證範圍

- 兩組載入器編譯成功。
- 正式載入器程式以模擬 Rhino 主機測試，七項通過：首次載入順序、正確服務 ID、檔案路徑、重複啟動、服務失敗停止、腳本指令失敗、資源缺失。
- 模擬測試不等於 Rhino 實機測試。**Windows 首次啟動仍待回測**；Mac 啟動測試受授權占用限制。
- 模型仍為參考幾何，密封、耐壓及完整旋入路徑尚未驗證。

English: Explicitly loads Rhino’s built-in scripting provider before dispatching the panel script. Install beta.3, fully restart Rhino, and run BottleThread directly. Both assemblies build; seven simulated-host launcher tests pass. Windows first-launch runtime verification remains pending.
