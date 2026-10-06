# 入口规则研究与复算

范围：已知野外活动入口的人工事件统计。结果不能作为室内机器人误报率、检出率或定位性能。

从仓库根目录运行（Python 3.10及以上）：

```sh
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements-research.txt
python docs/research/scripts/ant_entry_public_data.py
python docs/research/scripts/ant_entry_crosscheck.py
```

第一步重新生成逐事件CSV、逐记录统计与汇总；第二步用独立提取器核对首180秒事件。脚本会更新 `data/Pless2015/` 的派生结果，原表抽查PDF写入被忽略的 `tmp/`。

来源与边界详见[证据说明](Nest_ant_entry_evidence_2026-10-05.md)。`package_ant_entry_review.py` 为此前报告打包脚本，只有核验结果与它的断言一致时才运行；它不是系统入口。

## 第三方材料

`data/Pless2015/journal.pone.0141971.s004.zip` 和 `.s009.docx` 来源于 Pless et al. (2015), PLOS ONE, DOI [10.1371/journal.pone.0141971](https://doi.org/10.1371/journal.pone.0141971) 的补充数据；著作权与使用条件归原始来源。

原始S3压缩包SHA256：`ec3103f7db6fc1524cbda196159c4e63153d51dc02cd2547a45e0befab9a0b45`。仓库中的CSV和JSON是保留来源及提取检查的复算结果；不要混作本项目采集的实验。

依赖版本是本次核查环境所用版本，不代表跨所有平台验证。
