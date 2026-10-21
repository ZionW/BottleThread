# BottleThread v1.0.0 — 第一個正式版本

將已確認可用的最新版定義為第一版，功能及幾何生成程式維持一致，套件版本統一為 **1.0.0**。

## 安裝

下載 `bottlethread-1.0.0-rh8_35-any.yak`，拖入 Rhino 安裝，**完全關閉並重新啟動 Rhino**，再輸入 `BottleThread`。
需要 Rhino **8.35+**。同一 Yak 包含 Mac／Windows 的 net7.0／net48 AnyCPU 載入器。
外掛會自動載入 Rhino 腳本服務，無需事先手動執行 ScriptEditor。

## 功能

- 瓶口、瓶蓋獨立勾選；雙選直接生成同軸組裝位置。
- PCO 1881、PCO 1810、24/410、28/410 等 17 項預設／模板。
- L／M style、自訂尺寸、牙側角度及圓角。
- PCO 1881 獨立內凸牙，可調牙高、牙頂寬及漸入／收頭。
- 瓶口與瓶蓋內牙的排氣缺口分別控制。
- 組合剖面、牙型放大、缺口俯視及繁中／英／日／韓介面。

## 驗證與限制

- Mac 已完成安裝、指令及幾何測試。
- Windows 使用者已確認直接執行 BottleThread 可成功啟動；完整幾何回歸尚未在 Windows 實測。
- 兩組載入器編譯成功，七項模擬主機的載入器測試通過。
- 局部參考模型，非完整商用瓶蓋認證；密封、耐壓及完整旋入路徑尚未驗證。

![PCO 1881 同軸組裝與操作面板](https://raw.githubusercontent.com/ZionW/BottleThread/main/docs/images/pco1881-assembly-panel.png)

## 實物對照與列印樣件

| 實物與 Rhino 模型對照 | 瓶口／瓶蓋 3D 列印樣件 |
| --- | --- |
| ![實物瓶蓋與 Rhino 螺紋模型對照](https://raw.githubusercontent.com/ZionW/BottleThread/main/docs/images/bottle-cap-physical-comparison.jpg) | ![綠色瓶口與瓶蓋的 3D 列印樣件](https://raw.githubusercontent.com/ZionW/BottleThread/main/docs/images/printed-neck-cap-samples.jpg) |

照片展示模型與實物對照，以及列印後的瓶口與瓶蓋內外牙細節。

English: First stable release, promoted from the confirmed working version. Install the universal Yak in Rhino 8.35+, restart Rhino, and run BottleThread directly. Windows startup is user-confirmed; full Windows geometry regression remains pending. Reference geometry only.
