# FMGWorld 0.2.1 构建 1794697542 汉化补丁 20

修订 19 装完后游戏内所有文字显示为 "?"（Ren'Py 的 config.missing_glyph），
原因是实际生效的字体仍是 `gui/fonts/rog.ttf`，而 v17 那张 `ChineseUI.ttc`
是 19.7 MB 的 TTC 集合，在 1794697542 上没有被文字渲染采用。

修订 20 的做法：不再依赖代码里的字体路径是否生效，直接顶掉字体文件本体。

- `assets/x-game/x-gui/x-fonts/x-ChineseUI.ttc` —— 换成单面 TTF（微软雅黑子集，7,570 字，6,180,108 B）
- `assets/x-game/x-gui/x-fonts/x-rog.ttf` —— 同样换成这份 TTF（覆盖默认字体）

这样无论样式走 `gui.text_font`（中文 TTC）还是走 `persistent.text_font = "rog"`，
拿到的都是带中文字形的字体。

- 原包 SHA-256：`3c124be45accca4bd4c08774baca7c29712f5fb889ae9e723345af58b0b35d05`
- payload.zip：229 条目，10,448,735 B，SHA-256 `d185e60a432f9d91005f653de3b8ce5fe69aa20014d40ca97b55d8587b116f4f`
- 中文 rpyc 221 个（字符串级替换 24,873 处）+ 6 个 shim
- 含 `x-zz_fmg_asset_paths.rpyc`（工具端 required_entries）
- 含物品赠送 / 牛奶 / 批量丢弃三处修复
- 已知未译：107 条敌人 / 怪物名（who 槽），与旧包一致
