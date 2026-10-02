# GPT-6.1 Sol 订阅渠道目录补充

2026-10-02，Accepted。负责人本轮明确要求“GPT订阅渠道支持6.1 sol，加一下”。C级现有渠道目录兼容更新；不移动OAuth、Provider encoder、权限、Evidence或系统上下文边界。单独卡/代码PR，待用户回答恢复卡提交后实施。

允许代码：apps/desktop/electron/main/provider-adapters/openai-model-catalog.mjs及测试；llm-config-store.test.mjs与provider-encoder.test.mjs仅补新模型的选择持久化、上下文与请求编码覆盖。允许本卡、自测手册/报告和RC候选说明。现有Astra默认与现有模型保持，GPT-6.1 Sol排在旧Sol前，精确id gpt-6.1-sol。继承订阅400K/1M档位，不把API1.05M窗口写成订阅授权。

官方模型页 https://developers.openai.com/api/docs/models/gpt-6.1-sol 已实际读取：文本/图像输入、文本输出、128K输出上限；reasoning low/medium/high/xhigh/max，不支持none/minimal，工具走Responses。目录金额为API参考估算：input2/output10/cached0.10美元每百万，272K以上input/cache2倍、output1.5倍；不把API价格称为订阅账单。账号可用性以实际订阅请求为准，用户本轮已给可用事实。

focused目录/配置/encoder测试、Desktop受影响包全量及build/typecheck/architecture、两平台CI；使用隔离数据根、原渠道副本与现有统一Vault/helper进行实际gpt-6.1-sol read_file/post_reply，原用户配置不改、凭据副本清除，默认模型不切换。纳入下个RC候选安装后复验。


## 实施与本机证据

代码6c42a903/PR103已提交并推送。目录/配置/encoder focused123/123；Desktop5294项中5289通过、5项原有跳过，独立AST1项通过；全量build/typecheck/architecture通过。实际首轮请求gpt-6.1-sol到订阅端点HTTP200，两次空流、无工具与canonical回复；[失败证据](evidence/rc-gpt61-source-first-failed-20261002.json)已保留。该轮目录在提交前，sourceDirty=true；不能把sourceHead412303当作完整目录树绑定。干净6c42a903的新夹具通过现有产品Retry再测，尚未计作可用。API官方页与用户账号可用陈述不能替代本机工具请求成功。


干净6c42a903的显式产品Retry仍空响应，[失败证据](evidence/rc-gpt61-source-retry-failed-20261002.json)。准确模型id已到HTTP200订阅端点、无parseErrors；没有修改encoder或提示去伪造成功。复制凭据已清除。另一次源CLI经典输入自动化未进入模型请求，退出0、清除副本，不计作供应商或产品模型失败/成功。当前只完成目录与持久化支持，账号实际工具调用尚未通过。
