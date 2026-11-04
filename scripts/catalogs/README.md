# 补丁修订选择与发布

目录仍使用 schema=1、kind=game-version-catalog；`min_tool` 不提高，旧工具继续只读取每个原包的 `release`，保持最新补丁行为。

签名数据新增 `patch_history_schema: 1`。每个 `versions[]` 条目新增 `patch_history` 数组，只放同一官方APK的旧补丁，按修订号降序排列；最新补丁仍是 `release`。数组为空表示尚无获准选择的历史修订。

```json
{
  "version_name": "0.2.1",
  "version_code": 1793629832,
  "label": "FMGWorld 0.2.1 新构建",
  "release": {"signed_data": "最新补丁原始签名数据", "signature": "原始签名"},
  "patch_history": [
    {
      "revision": 16,
      "label": "必须与该补丁签名数据中的label完全相同",
      "stable": false,
      "notes": "历史修订，未重新进行完整真机验证；建议优先使用最新补丁。",
      "release": {"signed_data": "旧补丁原始签名数据", "signature": "旧补丁原始签名"}
    }
  ]
}
```

上述内容全部包含在目录原有的 `signed_data` 内，外层用原发行密钥重新签名。历史补丁的内层签名不重写，`game` 和 `source_sha256` 必须与当前原包一致；不能把不同原包甚至不同游戏的补丁混进来。`stable=false` 不代表已确认有缺陷，只表示未重新做过完整真机验证，不冒充“稳定版”。

## App接入约定

1. 先校验外层目录签名及递增的 `catalog_version`，再按官方APK完整SHA-256、versionName、versionCode定位原包条目。不要只按游戏名称或0.2.1这样的显示版本匹配。
2. 选择列表由当前 `release` 和 `patch_history` 组成。每项再验证内层签名、游戏、原包SHA、min_tool、补丁大小与哈希；历史项 `revision` 必须等于内层 `version`，且小于最新修订。
3. 普通更新路径保留现有防回退。只有用户明确选择、并且选中项仍存在于当前有效签名目录中时，才授权激活这个精确修订；授权应绑定游戏、原包SHA、修订号、补丁SHA和目录修订。不要全局移除“拒绝旧补丁”的检查。
4. 用户偏好按 `(game, source_sha256)` 保存。选定历史补丁后，自动检查不切回最新；仍允许刷新目录、显示已撤下修订的提示。切回“最新”时恢复自动更新。不能降低目录或补丁的防重放高水位。
5. 目录未授权、原包不符、签名不符或附件哈希不符一律拒绝。选择、下载补丁不等于已安装中文版，仍需重新生成并由系统确认安装。

GitHub侧增加此字段不会让未接入选择逻辑的旧App自动获得回退功能。本仓库不包含Android界面源码，此变更不发布或替换工具APK。

## 后续发布

需要Python 3.11及JDK 17或以上，无额外Python依赖。证书是公开校验材料；私钥只留在发布者电脑上，禁止提交到仓库或补丁附件。

先发布并核验新补丁附件，下载当前线上目录作为基线，再运行：

```text
python scripts/catalogs/catalog_history.py advance --baseline 当前线上目录.json --manifest 新补丁update.json --version-name 0.2.1 --version-code 原包构建号 --label 原包说明 --key 本机私钥.pk8 --output 新目录.json
python scripts/catalogs/catalog_history.py verify 新目录.json --previous-directory 当前目录文件夹
```

生成器将前一个最新补丁自动加入历史，保留所有其他原包和既有历史；不接受最新补丁降版、同修订更换内容、原包版本信息冲突。确认附件已上线后，再提交生成的 `catalogs/游戏ID.json`。外层目录每次变更必须递增修订，不能手工编辑签名JSON。

已有故障版本不自动追溯收录；首次补历史要逐项审核，再用 `history --baseline ... --history 获准旧清单.json ... --key ... --output ...`。移除已批准历史会被常规发布验证拒绝；真正需要安全撤回时，应另做明确的签名撤回协议，不能静默改写旧修订。

本次收录：FMGWorld构建1793629832的修订15、16；万物生长领域0.3.4.2的修订1、2。其他原包暂时没有可选历史。附件已重新下载校验，不代表旧剧情或所有手机已完整回归测试。
