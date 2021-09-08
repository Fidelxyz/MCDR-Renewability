# MCDR-Renewability
 A [MCDReforged](https://github.com/Fallen-Breath/MCDReforged) plugin that allows players to clone non-renewable items.

 一个允许玩家复制不可再生物品的 [MCDR](https://github.com/Fallen-Breath/MCDReforged) 插件。

 [![License](https://img.shields.io/github/license/Fidelxyz/MCDR-Renewability.svg)](https://github.com/Fidelxyz/MCDR-Renewability/blob/master/LICENSE)
 [![Release](https://img.shields.io/github/v/release/Fidelxyz/MCDR-Renewability.svg)](https://github.com/Fidelxyz/MCDR-Renewability/releases)

## 安装

依赖 [MCDReforged](https://github.com/Fallen-Breath/MCDReforged) 1.x 和 [MinecraftDataAPI](https://github.com/MCDReforged/MinecraftDataAPI)。

## 用法

`!!clone` 复制手中物品

`!!clone help` 查看帮助

`!!clone query` 查询今日剩余复制次数

`!!clone list` 查看可复制的物品列表

## 配置

第一次运行时会在 MCDR 目录中的 `config/renewability/` 目录新建 `config.json` 配置文件。

### `'max_daily_items_cloned'`

每人每日允许复制物品的最大数量。

类型：`Integer`

默认值：`1`

### `'allowed_items_list'`

允许复制的物品 ID。

类型：`list`

默认值：

```json
[
	"minecraft:elytra",
	"minecraft:enchanted_golden_apple",
	"minecraft:sponge"
]
```
