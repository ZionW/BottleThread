# BottleThread v0.1.0-beta.1

Rhino 8 的瓶口／瓶蓋螺紋建模工具，首個 Yak 測試版。

![PCO 1881 同軸組裝與操作面板](https://raw.githubusercontent.com/ZionW/BottleThread/main/docs/images/pco1881-assembly-panel.png)

PCO 1881 瓶口與瓶蓋的同軸組裝示例，搭配半透明顯示、組合剖面與參數面板。

## 安裝

下載 `bottlethread-0.1.0-beta.1-rh8_35-any.yak`，拖入 Rhino 安裝，**重新啟動 Rhino**，再執行 `BottleThread`。

需要 **Rhino 8.35+**。同一安裝檔包含 Mac／Windows 使用的 AnyCPU .NET Core 與 .NET Framework 組件。尚未發布到公開 Yak 套件伺服器。

## 功能

- 瓶口與瓶蓋獨立勾選；雙選直接以同軸組裝位置生成。
- PCO 1881、1810、24/410、28/410 等 17 項預設／模板。
- L／M style、自訂尺寸、牙側角度及圓角。
- PCO 1881 獨立內凸牙，牙高、牙頂寬及漸入／收頭可調。
- 瓶口與瓶蓋內牙各自控制四處排氣缺口。
- 組合剖面、牙型放大、缺口俯視；繁中、英、日、韓介面。
- 修正瓶口內孔殘料、文件關閉後面板殘留及重開時的空白父視窗。

## 驗證與已知限制

- Mac / Rhino 8.35：Yak 安裝、外掛載入、指令啟動、重開及四語切換通過。
- 安裝後可生成有效封閉的 PCO 1881 瓶口與瓶蓋，具有對位位置及四處瓶蓋排氣缺口。
- Windows .NET Core／.NET Framework 組件已編譯；**Windows 尚未實機測試**。
- 局部參考模型，非完整商用瓶蓋認證尺寸。尚未驗證密封、耐壓與完整旋入路徑；缺口端部使用矩形近似。

附件含 Yak、SHA-256 校驗碼、安裝說明與精簡驗證紀錄。

English: Install the universal Yak in Rhino 8.35+, restart Rhino, then run `BottleThread`. Mac installation and command tested; Windows runtime testing remains pending. Reference geometry only; sealing and pressure performance are not certified.
