# 修订 21：修复 python 代码块未汉化（bytecode 缓存）

## 原因

官方 APK 自带 `assets/x-game/x-cache/x-bytecode-312.rpyb`（约 250 万字节的编译缓存）。

Ren'Py 的 CompileCache key = `(hashcode, lineno, filename, mode, MAGIC, flags, column)`，
其中 hashcode 与 filename 都是从 rpyc 里读出的**定值**，不会因为源码字符串被改写而重算。

修订 19/20 只替换了 `PyCode.source` 里的字符串，hashcode 与 filename 都没变，
于是引擎每次都会命中旧缓存，python 块里的文案（物品说明、预设描述、
`renpy.input` 提示、`class ... __init__` 里的名字）仍然是英文；
而 Say 对话不走这个缓存，所以对话一直是中文。

## 修法

`repack_zh.py` 在替换字符串的同时，把每个 rpyc 内的 `game/xxx.rpy`
改名为 `game/xxx_zh.rpy`。filename 变了 → key 不匹配 → 缓存失效 →
引擎用中文源码重新编译。

## 副作用

- 首次进游戏会重新编译约 2700 个脚本，启动比以前慢几十秒；之后恢复正常。
- 崩溃堆栈里的文件名会显示 `_zh.rpy`，无功能影响。
- payload：229 条目 / 10446265 B / sha256 `339ec75f2251cd3916aa58e4d694c1821434bacbb5593c84f07ea4524935ea91`
