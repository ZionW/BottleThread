# BottleThread 0.1.0-beta.3 — Rhino 8

## 安裝與使用（Mac／Windows）

1. 下載 `bottlethread-0.1.0-beta.3-rh8_35-any.yak`，拖入 Rhino 安裝。
2. **完全關閉並重新啟動 Rhino。**
3. 直接輸入 `BottleThread` 開啟面板，不需先手動執行 ScriptEditor。

需要 Rhino 8.35+，使用內建 Python 3。首次初始化 Python 可能需要等待。
此版先明確載入 Rhino 內建腳本服務，再執行面板。若初始化本身失敗，請提供 RhinoCodeLogs 錯誤。

同一 Yak 包含 net7.0／net48 AnyCPU 載入器。Windows 首次啟動仍待回測。
七項載入器測試使用模擬 Rhino 主機，不能取代 Windows 實測。

勾選瓶口、瓶蓋或兩者；雙選時以同軸組裝位置生成。
局部參考模型；尚未驗證密封、耐壓及完整旋入路徑。PCO 1881 蓋牙為可調參考值。

## 建置

    dotnet restore src/BottleThread.csproj
    python3 build_package.py

需要 Rhino Yak 工具、.NET SDK、Python 3；Windows 可用 `py -3`。
使用固定版本 RhinoCommon NuGet SDK；BOTTLETHREAD_YAK 可指定 Yak 工具路徑。
