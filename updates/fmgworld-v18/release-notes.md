# FMGWorld 0.2.1 构建 1794697542 汉化补丁 18

- 目标原包：`com.fmgworld.evilfemboy-0.2.1-1794697542-release.apk`
- 原包 SHA-256：`3c124be45accca4bd4c08774baca7c29712f5fb889ae9e723345af58b0b35d05`
- payload.zip：227 条目，14,791,461 B，SHA-256 `7603d935d24ec3c43420c06947a670a116a02b548ef716c4bfdb783d2ef7e7ac`
- 下载：https://github.com/diandian226/game-translation-updates/releases/download/fmgworld-patch-v18/payload.zip

## 内容
- 221 个官方 rpyc 的字符串级汉化（共 24,873 处替换，AST 路径对齐，不重编译）
- 字体：`gui/fonts/ChineseUI.ttc`，`gui.text_font` / `name_text_font` / `interface_text_font` 三处指向
- shim（5 个）：`display_cn`、`dynamic_names_cn`、`fix_en_ui`、`inventory_fix`、`items_fix17`
- 物品三修：赠送装备保留、牛奶效果遍历副本、批量丢弃 `_fmg_drop_items17`

## 已知问题
- 107 条敌人/怪物名未译（与旧版一致）
- 未真机实测
