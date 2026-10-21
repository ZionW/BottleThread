# BottleThread v0.1.0-beta.2 — Windows 啟動修正

修正 beta.1 在尚未載入 Rhino Python 語言服務時，執行 `BottleThread` 出現 `Can not determine language for ...` 的啟動路徑。

## 更新方式

1. 下載 `bottlethread-0.1.0-beta.2-rh8_35-any.yak`，拖入 Rhino 安裝。
2. **完全關閉並重新啟動 Rhino。**
3. 執行 `BottleThread`。
4. 若 Python 3 尚未初始化，先執行 `ScriptEditor`，等待初始化完成後再試。

需要 Rhino **8.35+**；同一 Yak 包含 Mac／Windows 的 net7.0／net48 AnyCPU 載入器。

## 變更

- 使用官方 `_-ScriptEditor _Run` 入口，讓 Rhino 載入並初始化 Python 3。
- 載入器加入 ScriptRunner 標記，允許啟動 Rhino 腳本指令。
- 面板明確指定 `#! python 3`。
- 移除載入器對 `Rhino.Runtime.Code` 的直接依賴。
- 固定建置 SDK，避免已安裝 Rhino 更新後意外提高套件版本需求。
- 螺紋幾何與參數功能未變更。

## 驗證與限制

- net7.0／net48 編譯成功；兩組組件皆確認不依賴 Rhino.Runtime.Code 或 macOS 專用組件。
- Mac Yak 安裝成功；首次啟動回歸測試因 Rhino 授權占用而停止。
- **Windows 的啟動修正仍需實機回測。** 若仍有錯誤，請提供新的命令列／ScriptEditor 錯誤。
- 原有模型為參考幾何，密封、耐壓及完整旋入路徑尚未驗證。

![PCO 1881 組合模型與操作面板](https://raw.githubusercontent.com/ZionW/BottleThread/main/docs/images/pco1881-assembly-panel.png)

English: Fixes the beta.1 launch path behind the reported language-detection error. Install beta.2, completely restart Rhino, then run BottleThread. If needed, open ScriptEditor once and wait for Python 3 initialization. Both assemblies build and the Yak installs on Mac; Windows runtime retesting is still pending.
