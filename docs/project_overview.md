---
name: project-overview
description: 项目整体概况——目标、架构、技术栈、当前状态
metadata: 
  node_type: memory
  type: project
  originSessionId: dff2b66d-5fe6-46c8-81d5-37cf0c503de6
---

# Auto Resource Pusher 项目概况

## 目标
每天自动从多个信息源拉取内容，经规则+AI 筛选后，通过飞书机器人推送到手机。五篇文章覆盖 GitHub 开源、国内热点、国外科技、AI 动态、国际大事。

## 技术栈
- Python 3.11+、requests、python-dotenv
- DeepSeek V4 Flash API（AI 精选）
- 飞书自定义机器人 Webhook（推送）
- Windows 任务计划程序（定时运行）

## 信息源（4 个）
- GitHub Trending（30 天窗口高星仓库）
- Hacker News（首页热帖，外链+讨论页回退）
- 掘金（国内技术社区热榜）
- 今日头条热榜（国内+国际综合）
- ~~Reddit（被墙已移除）~~
- ~~知乎（API 需认证已废弃）~~
- ~~开发者头条（反爬已废弃）~~

## 筛选流水线
75 篇文章 → 规则打分(每源保底5篇, 共30候选) → DeepSeek 按5主题各选1篇 → HEAD 链接可达性检查(按源区分超时) → 不可达按主题补位

## 当前状态
- ✅ 全流程跑通
- ✅ 30 天滑动去重
- ✅ 主题补位机制
- ✅ GitHub 仓库: fanwenjing729/auto-resource-pusher
- ⏳ 待启动定时任务（右键 setup_schedule.ps1）
