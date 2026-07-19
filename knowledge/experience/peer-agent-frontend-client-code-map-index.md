# Peer Agent 前端/客户端代码地图（索引）

完整报告：[`peer-agent-frontend-client-code-map.md`](./peer-agent-frontend-client-code-map.md)

## 规模快照

| Layer | Files | Prod LOC | Test LOC |
|-------|------:|---------:|---------:|

| frontend-renderer | 259 | 47205 | 4834 |
| client-main | 233 | 36616 | 23047 |
| client-preload | 1 | 314 | 0 |
| desktop-shell | 3 | 181 | 0 |
| shared-ui | 1 | 84 | 0 |
| shared-protocol | 7 | 2356 | 0 |
| shared-chat-kernel | 9 | 1489 | 714 |
| shared-task-thread | 2 | 116 | 75 |
| shared-i18n | 1 | 1783 | 0 |
| shared-conversation-store | 3 | 870 | 0 |
| shared-runtime | 58 | 5654 | 3219 |
| shared-credential-helper | 2 | 311 | 203 |
| capabilities-manifest | 8 | 348 | 0 |

**焦点合计**：579 files / 129071 LOC（prod 96979 + test 32092）

**符号**：2875 prod symbols；**IPC**：146 channels

## 章节导航（完整报告）

1. 边界与入口
2. 仓库全景与规模统计
3. 文件树与逐文件行数
4. 函数/方法/组件/Hook 目录与职责
5. 关键调用链
6. 静态分析限制与复核
