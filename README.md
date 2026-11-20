# Hierarchical Average Linkage

简体中文 | [English](README.en.md)

`skill-hierarchical-average-linkage` 是一个独立的 QuantSkills Community Project，用于执行 `Hierarchical Average Linkage` 方法，并按冻结的时间边界输出可审计的研究结果。

## 适用边界

- 适用于：使用本仓库声明的 `Hierarchical Average Linkage` 方法处理本地因子面板。
- 方法专属的排除条件和失败规则见 `SKILL.md`。
- Valid 和 OOS/holdout 不得违反 `SKILL.md` 中的冻结与防泄漏规则。

## 研究披露

- 数据来源：仅使用公开数据、用户提供的本地数据或用户有权使用的材料，并记录数据血缘。
- 假设：明确时间语义、股票池、因子方向、缺失值和标签可用性。
- 参数：保存阈值、随机种子、时间切分、预处理和方法设置。
- 限制：披露样本依赖、不稳定性、近似计算、数据缺失和未覆盖的市场环境。
- 风险边界：所有产物仅用于量化研究与教育。

## 当前状态

- Catalog: `02.factor-selection`
- Workflow: `factor-screening`
- Validation: `runnable`
- License: `GPL-3.0-only`

当前仓库包含经过 smoke 测试的 Python CLI、独立依赖、合成示例和 pytest 测试。

## 可运行实现

```bash
python -m pip install -r requirements.txt
python scripts/run_average_linkage.py \
  --curves /path/to/train_curves.csv \
  --output-dir /path/to/output \
  --train-start 2020-01-01 \
  --train-end 2023-12-31 \
  --n-clusters 20
python -m pytest -q
```

核心结构化输出为 `ranked_factor_set.json`，其 Profile 为 `ranked-factor-set` 1.0.0；其余文件用于方法审计与复现。

## 入口

- `SKILL.md`：权威 Skill 指令和 QuantSkills frontmatter。
- `references/protocol.md`：时间边界、输入审计和输出验收。
- `references/source_boundary.md`：数据、许可证、隐私和研究风险边界。

## 声明

本项目仅用于量化研究与教育，不构成投资建议、收益保证或生产上线批准。
