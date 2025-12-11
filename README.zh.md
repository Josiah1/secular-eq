# Secular Equilibrium Calculator

放射性衰变链长期平衡计算工具

## 📦 功能特性

- 基于测量的子核素活度，计算源头核素的活度和质量
- 支持任何放射性衰变链，包括天然系列（U-238、Th-232、U-235）和人工衰变链
- 自动计算衰变链中的累积分支比
- 支持所有衰变类型 (α, β-, β+, EC, SF, IT, p, n 等)
- 衰变类型指定，支持简写 (a 代表 α, b 代表 β-, e 代表 EC)
- 提供命令行接口(CLI)和Python API
- 详细的错误处理和输入验证
- 灵活的输出来模式，包括静默和仅输出质量模式

## 🔧 安装

### 通过pip安装（推荐）

```bash
pip install secular-equilibrium
```

### 从源代码安装

```bash
# 克隆仓库
git clone https://github.com/Josiah1/secular-eq.git
cd secular-eq

# 安装依赖
pip install -r requirements.txt

# 开发模式安装
pip install -e .
```

## 🚀 快速开始

### 方法1: Python库使用

```python
from secular_equilibrium import calculate_secular_equilibrium

# 从Pb-214活度计算U-238含量
results = calculate_secular_equilibrium(
    measured_nuclide='Pb-214',
    measured_activity=100.0,  # Bq
    parent_nuclides=['U-238', 'Ra-226'],
    verbose=True
)

print(f"U-238活度: {results['U-238']['activity_Bq']:.4e} Bq")
print(f"U-238质量: {results['U-238']['mass_g']:.4e} g")
```

### 方法2: 命令行使用

```bash
# 基本用法
secular-eq --measured Pb-214 --activity 100 --parents U-238 Ra-226

# 简写形式
secular-eq -m Pb-214 -a 100 -p U-238

# 多个源头核素
secular-eq -m Bi-214 -a 50 -p U-238 U-234 Ra-226 Rn-222

# 静默模式（只输出关键结果）
secular-eq -m Pb-214 -a 100 -p U-238 -q

# 指定衰变类型（如α衰变）
secular-eq -m Pb-214 -a 100 -p U-238 -d α

# 使用简写衰变类型（a代表alpha，b代表beta，e代表EC）
secular-eq -m Pb-214 -a 100 -p U-238 -d a

# 仅输出质量模式（只输出质量，单位克，每行一个）
secular-eq -m Pb-214 -a 100 -p U-238 Ra-226 --mass-only
```

## 📊 实际应用示例

### 示例1: 环境样品中U-238含量测定

```python
from secular_equilibrium import calculate_secular_equilibrium

# 测量了土壤样品中Pb-214的活度为85 Bq/kg
results = calculate_secular_equilibrium(
    measured_nuclide='Pb-214',
    measured_activity=85.0,  # Bq/kg
    parent_nuclides=['U-238'],
    verbose=True
)

# 获取U-238含量
u238_mass_per_kg = results['U-238']['mass_g']
u238_ppm = u238_mass_per_kg * 1e6  # 转换为ppm
print(f"\n土壤中U-238浓度: {u238_ppm:.2f} ppm")
```

### 示例2: Th-232系列分析

```python
# 测量了Bi-212活度
results = calculate_secular_equilibrium(
    measured_nuclide='Bi-212',
    measured_activity=120.0,
    parent_nuclides=['Th-232', 'Ra-228', 'Th-228'],
    verbose=False  # 不打印详细信息
)

# 提取关键信息
for parent, data in results.items():
    print(f"{parent}:")
    print(f"  活度: {data['activity_Bq']:.2e} Bq")
    print(f"  质量: {data['mass_g']:.2e} g")
    print(f"  分支比: {data['branching_ratio']:.4f}")
```

## 📚 API文档

### `SecularEquilibriumCalculator` 类

#### 初始化参数
- `measured_nuclide` (str): 测量的核素名称 (如 'Pb-214', 'Bi-214')
- `measured_activity` (float): 测量的活度 (Bq)
- `parent_nuclides` (List[str]): 源头核素列表 (如 ['U-238', 'Ra-226'])
- `decay_type` (str, 可选): 考虑的衰变类型 (如 'α', 'β-', 'β+', 'EC')。如果为None，考虑所有衰变类型（默认）。

#### 方法
- `calculate()`: 执行计算，返回结果字典
- `print_results(results)`: 打印格式化的结果

### `calculate_secular_equilibrium()` 函数

便捷函数，自动创建计算器并返回结果。

```python
def calculate_secular_equilibrium(
    measured_nuclide: str,
    measured_activity: float,
    parent_nuclides: List[str],
    decay_type: Optional[str] = None,
    verbose: bool = True
) -> Dict[str, Dict[str, float]]
```

#### 衰变类型指定示例

```python
# 从测量的Pb-214 α衰变活度计算U-238活度
results = calculate_secular_equilibrium(
    measured_nuclide='Pb-214',
    measured_activity=50.0,  # α衰变活度 (Bq)
    parent_nuclides=['U-238'],
    decay_type='α',  # 或使用简写 'a'
    verbose=True
)

# 使用衰变类型简写
results = calculate_secular_equilibrium(
    measured_nuclide='Pb-214',
    measured_activity=50.0,
    parent_nuclides=['U-238'],
    decay_type='a',  # α衰变的简写
    verbose=True
)
```

#### 返回值格式

```python
{
    'U-238': {
        'activity_Bq': 100.0,           # 活度 (Bq)
        'mass_g': 8.04e-6,              # 质量 (g)
        'branching_ratio': 1.0,         # 分支比
        'halflife_yr': 4.468e9,         # 半衰期 (年)
        'atomic_mass': 238.05078826     # 原子质量 (u)
    }
}
```

## 🔬 支持的衰变链

本计算器支持**任何放射性衰变链**，基于核衰变数据库。虽然常用于天然放射性系列，但同样适用于人工衰变链和自定义核素组合。

### 主要天然放射性系列（常见示例）

1. **U-238系列** (铀系)
   - U-238 → Th-234 → Pa-234m → U-234 → Th-230 → Ra-226 → Rn-222 → Po-218 → Pb-214 → Bi-214 → Po-214 → Pb-210

2. **Th-232系列** (钍系)
   - Th-232 → Ra-228 → Ac-228 → Th-228 → Ra-224 → Rn-220 → Po-216 → Pb-212 → Bi-212 → Po-212/Tl-208

3. **U-235系列** (锕系)
   - U-235 → Th-231 → Pa-231 → Ac-227 → Th-227 → Ra-223 → Rn-219 → Po-215 → Pb-211 → Bi-211

## ⚠️ 注意事项

1. **封闭系统**: 假设系统封闭，无外来核素加入或流失
2. **平衡时间**: 需要等待约7-10个子核半衰期才能达到平衡
3. **分支衰变**: 包自动考虑分支比，但需确保衰变链正确
4. **测量不确定度**: 结果精度取决于输入活度的测量精度

## 🧪 运行测试

```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试
python -m pytest tests/test_calculator.py::TestSecularEquilibrium::test_u238_chain

# 使用unittest
python -m unittest tests/test_calculator.py
```

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🤝 贡献

欢迎提交Issue和Pull Request！

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📧 联系方式

如有问题，请在GitHub上提交Issue。
