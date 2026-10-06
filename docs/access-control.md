# 仓库访问控制｜Verified，2026-10-06

## 负责人要求

成员不得直接修改 `Cedar-Knight/Nest` 的任何分支；修改通过Fork与PR提交，由 `@Cedar-Knight` 审阅并合并。原仓库新分支需事先批准，再由负责人创建或发布。

GitHub分支创建限制不是待审批队列：没有权限的推送会被拒绝；审批通过后由负责人发布分支。

## 当前配置与核查结果

- 仓库：经负责人明确选择，个人账号 `Cedar-Knight` 下的公开仓库；成员无需写权限即可Fork和提交PR。
- 成员：仅仓库所有者；没有待接受的成员邀请。
- 分支：仅main，已启用下方规则；自动合并关闭。
- 唯一绕过账号：`Cedar-Knight`（User 217698521），允许负责人直接维护自己的仓库及合并贡献。其他人不在例外列表。
- 已通过API读回验证：规则Active、分支／标签覆盖范围与唯一例外；main及一个尚不存在的任意分支名均匹配限制。
- 尚未使用非所有者成员账号尝试实际推送；不声称完成成员端运行测试。配置核验与成员端测试分别记录。

## 已启用规则

- [所有分支发布限制](https://github.com/Cedar-Knight/Nest/rules/24556182)：所有分支限制创建、更新、删除及强制推送，仅负责人绕过。
- [所有标签发布限制](https://github.com/Cedar-Knight/Nest/rules/24556186)：所有标签限制创建、更新、删除及强制推送，仅负责人绕过。
- [main审阅规则](https://github.com/Cedar-Knight/Nest/rules/24556187)：要求PR、至少1个批准、CODEOWNERS批准、改动后撤销旧批准及解决审阅讨论；负责人保留维护例外。
- `.github/CODEOWNERS` 指定全部文件由 `@Cedar-Knight` 审阅。该文件与Active规则共同形成审批要求；单独声明负责人不具备强制保护。

- 不给成员原仓库写权限或Admin权限；没有发送邀请。
- 成员在自己的Fork工作，提交PR；原仓库中需要的新分支由负责人按批准请求创建。
- 规则是原仓库的分支／标签规则，不限制成员自己Fork中的开发分支。

## 配置历史

仓库原为私有；规则接口返回403要求升级Pro或公开。负责人明确选择公开和Fork／PR路径后，改变可见性并启用规则。没有购买套餐、转移仓库或重写历史。

## 成员加入时的剩余检查

使用成员自己的账号验证原仓库创建新分支、推送已有分支和直接合并均被阻止；Fork及PR流程可用。无需为测试授予写权限。创建新分支的审批在Issue进行，由负责人执行发布；平台不会为被拒绝的推送自动生成审批请求。

## 官方依据

- [个人仓库权限](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/repository-access-and-collaboration/permission-levels-for-a-personal-account-repository)
- [规则集功能与套餐范围](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets)
- [CODEOWNERS及审批要求](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)
