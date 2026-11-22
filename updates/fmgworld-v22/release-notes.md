# FMGWorld 0.2.1 构建1794697542 汉化22（缓存全修）

## 本修订修了什么
修订 21 只改了 `*.rpy` 的源码文件名（`game/xxx.rpy` -> `game/xxx_zh.rpy`）来让编译缓存失配，
但战斗/物品类脚本是 `*_ren.py` 模块（`game/scripts/combat/**/xxx_ren.py`），
正则只匹配 `.rpy` 漏掉了它们，共 17 个文件仍命中官方 `cache/bytecode-312.rpyb` 的旧字节码。

本修订把 `.py` 也一起改名（`xxx_ren.py` -> `xxx_ren_zh.py`），全量扫描后缓存命中为 0：

- patched total hit=0 miss=3280
- files with residual hits: 0

## 产物
- payload.zip：229 条目 / 10,446,056 B / sha256 458d4d9ab68ca553fa2ce13e61888f3a0cc8a30eed96f619cc801c118b2dff0a
- 官方 APK sha256：3c124be45accca4bd4c08774baca7c29712f5fb889ae9e723345af58b0b35d05
- 字体：单面 CJK TTF（x-ChineseUI.ttc 与 x-rog.ttf 同字节）
- 含物品赠送 / 牛奶 / 批量丢弃三处修复

## 副作用
首次进游戏会重新编译全部 python 块，启动比平时慢几十秒；之后正常。
