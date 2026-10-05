# RC6 界面与交互评测候选

创建时间：2026-10-05。最后更新：2026-10-05。

2026-10-05，负责人明确授权落地、测试并发布新RC。已发布候选版本 `0.1.0-rc.6`；PR121已合入，源码、CI与实际产物绑定见下方。GA与复杂写任务Evidence缺口仍分别受原门禁约束。

## 范围

- 统一已批准Frost分组、标题、字体、间距与灰底控件；连续曲线分级12/8/16，菜单轻阴影与可辨焦点、禁用/选中态；分隔线铺满列宽、版本在右。
- 消息左右布局、真实Bot身份、正文下回执；紧凑引用定位，无左侧强调线；弱操作与可读过程、技术详情。
- 同一条回复流式增长，实际停止保留部分正文/未完成/草稿；选项绑定所属消息，自由输入自动收起与清除需要你计数。
- 文件选择、粘贴、拖放的既有附件链；单Bot模型和推理强度、输入区与档案共享、回合配置快照；滑动分段与键盘/减少动效。
- 通用页返回后读取保存值；发布版本/中英说明/生成changelog/24行升级矩阵。

本轮新表面为C级，附件与模型边界已在PR121对应ADR批准范围实施；不增加独立执行路径、依赖或发布通道。

## 自测与交接

本机完整build/typecheck/architecture/test通过；桌面5342项中5337通过、原5跳过，24行升级矩阵通过。首次候选回归在changelog固定RC5断言处失败，已更新为RC6后全套成功，首次失败保留。窗口首次底栏旧几何断言失败，修复为真实内边缘与全宽分隔线，后续窗口通过。完整门禁、最终CI、合入tree和发布产物的精确绑定记在本卡下方证据。

[生产设计QA](../../design/product/peer-frost-radius-rc6-design-qa.md)，[全面测试手册](acceptance-test-guide.md)，[开发者自测报告](rc-self-test-report.md)。原195项不减少，加入I11–I15后为200项唯一用例/6流程，不给未执行组合预填Pass。

## 升级路线

RC4/RC5：设置 → 更新与关于 → 自动或Beta → 检查更新，确认候选RC6后下载并安装重启。旧Beta5/RC1–3先从新Release下载同架构包手动升级，不接受旧Beta降级提示。退出旧宿主并备份完整数据；Desktop、CLI/TUI、Gateway同版本，不重置用户数据。

npm固定评测版本：`npm install -g @peer-agent/cli@0.1.0-rc.6`，确认 `peer --version`。npm rc指向RC6；latest保持0.0.18，beta保持0.1.0-beta.5。实际注册表、隔离npm安装与发布资产均已核对，发布完成。

## 持续限制

复杂写任务命令描述Evidence快照缺口仍阻塞总体Ready与GA；拒绝核验机制保留。生产远程/实体手机、跨应用拖放/超大文件、完整读屏、Windows/Linux交互安装及7天日用保持对应待验收范围。原生受控Provider演示不代表真实模型质量或所有云渠道可用。

## 合入与标签绑定

PR121已按授权合入开发线 `f0b9b14eb7cc410e8f2ce9ec51e8f755b269093a`；最终源码 `2b3864d6`，CI[37262260463](https://github.com/ly-ccx/Peer-Agent/actions/runs/37262260463)两平台全部成功。源码、CI合成merge、实际merge的tree均 `da9f0989ce18d5a32c53cc4528a767829a073833`，干净合入源readiness/source-check再次通过。窗口9壳/13可访问性/7诊断/5回复、72布局通过，无页面/授权错误。固定标签 `v0.1.0-rc.6` 指向该合入提交。[精确绑定](evidence/rc6-candidate-ci-binding-20261005.json)、[源码门禁](evidence/rc6-source-gates-20261005.json)、[原生窗口](evidence/rc6-source-window-passed-20261005.json)。

## 发布完成与产物检查

[GitHub RC6](https://github.com/ly-ccx/Peer-Agent/releases/tag/v0.1.0-rc.6) 于2026-10-05发布，prerelease=true、draft=false、14项资产。[Release37263086451](https://github.com/ly-ccx/Peer-Agent/actions/runs/37263086451) 8个job全部成功，head为上述不可变merge：三平台Desktop、两平台CLI、meta、Release、npm。[工作流记录](evidence/rc6-release-workflow-20261005.json)、[资产元数据](evidence/rc6-published-release-20261005.json)。

实际下载Mac ZIP/DMG、两份CLI归档及三平台manifest：SHA256/size与GitHub digest匹配；Mac ZIP/DMG的SHA512与manifest匹配。ZIP应用与只读DMG内应用通过严格签名、同Team82672N97RP、Gatekeeper与公证票据；DMG完整性及卸载通过。归档Mac CLI与助手严格签名、CLI版本为RC6；助手保持Developer ID，peer保持既有Bun adhoc签名。实际包的更新Provider与项目应用服务字节与tag相同。[发布信任与模块绑定](evidence/rc6-published-assets-trust-20261005.json)、[DMG内应用](evidence/rc6-dmg-embedded-trust-20261005.json)。Windows/Linux Desktop只核对发布元数据/清单与CI打包，Linux CLI下载校验但未在本机执行；不视为实体互动安装通过。

公共npm四包固定RC6及rc标签已可见，latest与beta不变。首次缓存尚未返回固定版本的[查询记录](evidence/rc6-npm-metadata-first-20261005.json)保留，后续[四包查询](evidence/rc6-npm-metadata-passed-20261005.json)通过，没有重复发布。隔离prefix实际安装`@peer-agent/cli@0.1.0-rc.6`后执行得到`peer 0.1.0-rc.6`，安装与版本命令均exit0；未执行本轮完整模型/PTY流。[npm安装](evidence/rc6-npm-install-passed-20261005.json)。

真实GitHub feed/三平台manifest、生产Provider与SDK共21项联网选择/资格检查通过：Beta5/RC2/RC4/RC5在预览选择RC6，RC6不提示同版、旧Beta或旧正式降级，正式0.0.18不收到RC。此检查使用Node HTTP适配器和受控rollout资格；旧Beta5/RC1–3安装内的旧Provider仍需手动迁移，不能把“当前Provider以旧版本号探查”说成旧安装器已修好。[联网发现](evidence/rc6-update-live-discovery-passed-20261005.json)。

实际下载的未修改签名RC6已在隔离数据/profile中打开：通用页、版本、实际检查更新显示“已是最新·RC6”、左右对话/下方回执、灰底引用与定位、滑动分段/模型未配置禁用态均通过；[签名包UI](evidence/rc6-published-ui-passed-20261005.json)。两条合成历史仅验证表达，未用于宣称真实模型、工具或Evidence通过。自有应用已退出，本轮没有替换原用户应用、写其数据或执行原数据迁移/自动安装。

### 固定下载与SHA256

Mac DMG/ZIP、两CLI的hash已实际下载核对；Windows/Linux Desktop的hash来自上述GitHub发布digest。安装前对照同版本同架构，不以预览名称替代校验。

| 平台/文件 | 下载 | SHA256 |
|---|---|---|
| macOS Apple Silicon DMG | [Peer-Agent-0.1.0-rc.6-arm64.dmg](https://github.com/ly-ccx/Peer-Agent/releases/download/v0.1.0-rc.6/Peer-Agent-0.1.0-rc.6-arm64.dmg) | `3d53f29b88419b358b3aeaef9ce46fd918b643b4ef94b191152104cf55c04970` |
| macOS Apple Silicon ZIP | [Peer-Agent-0.1.0-rc.6-arm64.zip](https://github.com/ly-ccx/Peer-Agent/releases/download/v0.1.0-rc.6/Peer-Agent-0.1.0-rc.6-arm64.zip) | `5b6da39d8fc22df933d8143c5059609ac096e5355eb85a8ed2bc4bab2a9e18df` |
| Windows安装包 | [Peer-Agent-Setup-0.1.0-rc.6.exe](https://github.com/ly-ccx/Peer-Agent/releases/download/v0.1.0-rc.6/Peer-Agent-Setup-0.1.0-rc.6.exe) | `57e29e33b9fa0285c8aafd9d417fe5aa8a430e9e6a2a9b3639779bd9fcd153ba` |
| Linux AppImage | [Peer-Agent-0.1.0-rc.6-x64.AppImage](https://github.com/ly-ccx/Peer-Agent/releases/download/v0.1.0-rc.6/Peer-Agent-0.1.0-rc.6-x64.AppImage) | `7c576047408f1f3c979ddc8b938ee92d4d01eb6e6675e1d84026cd0e6a591a6a` |
| Linux DEB | [Peer-Agent-0.1.0-rc.6-x64.deb](https://github.com/ly-ccx/Peer-Agent/releases/download/v0.1.0-rc.6/Peer-Agent-0.1.0-rc.6-x64.deb) | `387233f2b398bdbed000381251a4d4fbffffb2559eb83a8f322981d9c8b04eeb` |
| macOS CLI | [peer-darwin-arm64.tar.gz](https://github.com/ly-ccx/Peer-Agent/releases/download/v0.1.0-rc.6/peer-darwin-arm64.tar.gz) | `f19e76321b942b2558ccf6e9a49488ce7049b9a10993079aa9b1b4895c01a5af` |
| Linux CLI | [peer-linux-x64.tar.gz](https://github.com/ly-ccx/Peer-Agent/releases/download/v0.1.0-rc.6/peer-linux-x64.tar.gz) | `4ce30548d36c7961c122b4e71c9063eae55ba020cd1d587225aae6f5cd6d1d0c` |

macOS用`shasum -a 256 下载文件`，Linux用`sha256sum 下载文件`，Windows PowerShell用`Get-FileHash 下载文件 -Algorithm SHA256`。CLI归档的peer与credential helper须保持同目录。总体Ready与GA门禁见前述持续限制，不以发布成功替代验收。
