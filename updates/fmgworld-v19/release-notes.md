# FMGWorld 0.2.1 构建 1794697542 汉化补丁 19

修订 18 因缺少工具端 `required_entries` 要求的 `assets/x-game/x-zz_fmg_asset_paths.rpyc`，安装时报
`更新缺少必要文件`，已作废；修订 19 补齐该文件后重新发布。

- 原包 SHA-256：`3c124be45accca4bd4c08774baca7c29712f5fb889ae9e723345af58b0b35d05`
- payload.zip：228 条目，14,793,162 B，SHA-256 `bdfac0a19ea6f90419d5b2c709156de39229e26e59af90ebb13c89a705808d82`
- 下载：https://github.com/diandian226/game-translation-updates/releases/download/fmgworld-patch-v19/payload.zip

## 内容
- 221 个官方 rpyc 字符串级汉化（24,873 处替换）
- 字体 `x-gui/x-fonts/x-ChineseUI.ttc` + 三处 gui.*_font 指向
- shim 6 个：display_cn / dynamic_names_cn / fix_en_ui / asset_paths / inventory_fix / items_fix17
- 物品三修

## 已知问题
- 107 条敌人/怪物名未译（与旧版一致）
- 未真机实测
