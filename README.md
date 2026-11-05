# 游戏汉化更新（Game Translator）

一个自己做的安卓小工具，用来分发和安装游戏汉化补丁。这个仓库是它的**更新源**：工具的新版本、各游戏的补丁和补丁目录都从这里发布。

> 个人业余作品，可能有不少 BUG，也可能不适配某些手机或系统，敬请谅解。遇到问题欢迎提 [Issue](https://github.com/diandian226/game-translation-updates/issues)。

> [!IMPORTANT]
> **非官方汉化 · 需自备正版 · 仅供学习交流 · 18+**
> 本仓库只发布汉化补丁和工具，**不提供任何完整游戏 APK**。

## 支持的游戏

| 游戏 | 适配的官方安卓原包 |
| --- | --- |
| FMGWorld | 0.2.1（多个构建，工具会自动识别） |
| 平行宇宙（In a Parallel Universe） | V1.3.1p |
| 女神制造者（Outgrow） | 1.1.67 PartOne |
| 万物生长领域（Realm of Evergrow） | 0.3.4.2 |
| Swole Blessings | 1.0.1 |

补丁按官方 APK 的**完整 SHA-256 和版本号**精确匹配。原包版本不对时，工具会拒绝打补丁，不会硬改。

## 下载工具

到 [Releases](https://github.com/diandian226/game-translation-updates/releases) 下载最新的 `Game-Translator-x.xx.apk` 并安装。

当前最新版：**V0.28**（[直接下载](https://github.com/diandian226/game-translation-updates/releases/download/tool-v0.28/Game-Translator-0.28.apk)）

已经装了旧版的话，在工具里点 **“检查工具新版本”**，下载后覆盖安装即可，原有数据会保留，不用卸载。很旧的版本没有这个按钮，请手动下载上面的 APK 覆盖安装。

## 使用方法

1. 打开工具，在游戏列表里选择要汉化的游戏。
2. 导入你自己的**官方安卓 APK**。
3. 选择对应的补丁（默认是最新版补丁，工具会自动下载并校验）。
4. 生成中文版 APK，按系统提示安装。

### 需要注意

- 生成的中文版和官方版**可以共存**，但官方版的私有存档**不会自动迁移**过去。
- **更新游戏补丁 ≠ 升级工具。** 两者分开检查、分开更新。
- 升级工具或换了补丁后，需要**重新生成并覆盖安装**中文版，改动才会生效（例如桌面图标的“汉”字角标）。
- 部分游戏可以在补丁列表里选择旧的历史修订。标注“未重新完整验证”的旧修订仍可使用，但建议优先用最新补丁。

## 安全与校验

- 工具更新信息在 [`tool-update.json`](tool-update.json)，包含新版 APK 的大小和 SHA-256，下载后逐一核对。
- 每个游戏的补丁目录在 [`catalogs/`](catalogs) 下，整个目录和其中每个补丁都带有数字签名。签名、原包或文件哈希任何一项对不上都会拒绝，也不会被退回到旧补丁。
- 公开的验签证书在 [`scripts/catalogs/update-cert.pem`](scripts/catalogs/update-cert.pem)，签名私钥只保存在发布者本机。

## 想要汉化某个游戏？

提交一个 [汉化申请](https://github.com/diandian226/game-translation-updates/issues/new?template=translation-request.yml)，填写游戏名称和资源地址。有安装包可以附上（先压成 ZIP，单个不超过 25 MB，更大的请填网盘链接），会让适配更快。

## 仓库结构

| 路径 | 内容 |
| --- | --- |
| `tool-update.json` | 工具更新信息（最新版本、下载地址、哈希、更新说明） |
| `catalogs/` | 各游戏的签名补丁目录 |
| `updates/` | 各次发布的补丁和工具更新数据 |
| `scripts/catalogs/` | 补丁目录的生成与校验脚本（[说明](scripts/catalogs/README.md)） |
| `announcement.txt` | 工具内显示的公告 |
| `.github/workflows/` | 自动发布与目录校验流程 |

## 免责声明

本项目为爱好者制作的非官方汉化，与各游戏的开发商、发行商无关，所有游戏内容版权归原作者所有。请支持正版：使用前请自行获取官方原版游戏。本项目仅供学习交流，部分游戏含成人内容，未满 18 岁请勿使用。如有侵权，请通过 Issue 联系，将及时处理。
