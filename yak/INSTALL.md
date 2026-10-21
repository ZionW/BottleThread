# BottleThread 0.1.0-beta.1 — Rhino 8

繁體中文 / English / 日本語 / 한국어

## 安裝（Mac 與 Windows）

1. 將 `bottlethread-0.1.0-beta.1-rh8_35-any.yak` 拖入 Rhino 8 視窗，依提示安裝。
2. 安裝後請重新啟動 Rhino。
3. 在 Rhino 指令列輸入 `BottleThread` 開啟面板。

需要 Rhino 8.35 或更新版本、內建 Python 3。首次執行如需初始化 Python 3，請讓 Rhino 完成初始化。
單一 Yak 內含 AnyCPU 的 net7.0 與 net48 載入器，供 Mac 與 Windows 的 Rhino 8 使用。
未上傳至公開 Yak 套件伺服器，請使用本地 Yak 安裝。

## 使用

勾選瓶口、瓶蓋或兩者，選擇規格及自訂參數。雙選時直接生成同軸組裝位置的兩個獨立封閉實體。
PCO 瓶口及瓶蓋內牙可獨立啟用排氣缺口。自訂規格及語言設定保存在使用者 LocalApplicationData/BottleThread，與外掛安裝目錄分開。

## 驗證與限制

Mac 實機驗證結果另見發行目錄測試紀錄。Windows 已提供 .NET Core/.NET Framework 對應組件，但未實機測試。
此版本為局部參考建模工具，非完整 ISBT 瓶蓋認證尺寸；不包含完整防盜環、密封結構、耐壓驗證或全旋入路徑驗證。
PCO 1881 瓶蓋內凸牙為可調參考牙型。缺口使用矩形近似，並非所有商業瓶蓋的缺口細節。

## Build

在已安裝 Rhino 8.35+ 與 .NET SDK 的 Mac/Windows 執行：

    dotnet restore src/BottleThread.csproj --ignore-failed-sources
    python3 build_package.py

Windows 可用 `py -3 build_package.py`。可用 BOTTLETHREAD_YAK 指定 Yak 工具路徑。
參考：https://developer.rhino3d.com/en/guides/yak/creating-a-multi-targeted-rhino-plugin-package/
