# CSV 中两个 Net 短接的判定规则

## 一、判定目标

判断两个原理图 Net 名称是否属于同一个电气节点，或者是否通过器件形成永久/条件短接。

AI 必须区分：

- 直接导线连接
- Net Tie 有意短接
- 0Ω电阻短接
- Jumper/焊桥短接
- Relay/MOS 条件短接
- 普通元件连接，不属于短接

---

## 二、直接导线短接

### 首选判据

如果 CSV 存在以下记录：

```text
RecordType = ELECTRICAL_SHORT_GROUP
ShortKind = DIRECT_NET_ALIAS
ShortStatus = CONFIRMED
ShortNetCount >= 2
```

则 `ShortNets` 中列出的所有 Net 名称属于同一个 Altium 编译电气节点，判定为直接导线连接。

示例：

```text
NetName = NET_A
ShortKind = DIRECT_NET_ALIAS
ShortObject = DIRECT_WIRE
ShortNetCount = 2
ShortNets = NET_A | NET_B
ShortStatus = CONFIRMED
```

结论：

```text
NET_A 与 NET_B 直接电气相通。
Altium 编译后统一使用 NET_A 作为 Canonical NetName。
```

### 无汇总行时的回退判据

按照 `NetName` 对 CSV 行分组：

1. 只选择 `MemberType=NET_LABEL` 的记录。
2. 提取不同的 `MemberName`。
3. 对名称去除首尾空格并采用不区分大小写的方式去重。
4. 如果同一个 `NetName` 下存在两个或以上不同 Net Label，则这些标签属于同一个编译电气节点。

例如：

```csv
NetName,MemberType,MemberName
NET_A,NET_LABEL,NET_A
NET_A,NET_LABEL,NET_B
```

结论：`NET_A` 与 `NET_B` 直接连接。

注意：重复出现两个相同的 `NET_A` 标签不能判定为两个 Net 短接。

---

## 三、Net Tie 短接

满足以下条件时判定为确认的有意短接：

```text
RecordType = NET_TIE_GROUP
EffectiveShortNetCount >= 2
Status = OK 或 OK_WITH_DANGLING_PINS
```

实际被短接的 Net 从 `EffectiveShortNets` 读取。

示例：

```text
RecordType = NET_TIE_GROUP
Designator = NT5
EffectiveShortNetCount = 2
EffectiveShortNets = AGND | PGND
Status = OK
```

结论：

```text
AGND 与 PGND 通过 NT5 有意短接。
短接类型：NET_TIE。
短接状态：CONFIRMED。
```

`ObservedNets` 不能代替 `EffectiveShortNets`。标记为 `DANGLING_NET_TIE_PIN` 的端点不能计入有效短接。

---

## 四、0Ω电阻短接

按照 `ComponentUniqueID` 优先、`Designator` 次选，对电阻 PIN 行分组。

必须同时满足：

1. 同一个电阻具有至少两个有效 PIN。
2. PIN 分别连接到两个不同的 `NetName`。
3. `ComponentValue` 归一化后属于零欧姆值。
4. 元件未标记为 DNP、DNF、Not Fitted 或不装。

可视为零欧姆的典型写法：

```text
0
0R
0R0
0.0R
0Ω
000
```

示例：

```csv
Designator,ComponentValue,PinNumber,NetName
R123,0R,1,NET_A
R123,0R,2,NET_B
```

结论：

```text
NET_A 与 NET_B 通过 R123 的0Ω电阻短接。
```

如果缺少装配/DNP信息，应输出：

```text
ShortStatus = CONDITIONAL
Reason = 需要确认 R123 实际贴装
```

普通非零电阻不能判定为短接。

---

## 五、Jumper、焊桥、Relay和MOS

### Jumper或焊桥

如果元件类型明确为 Jumper、Solder Bridge、Short Link，并且装配状态为闭合，可判定：

```text
ShortStatus = CONFIRMED
```

如果默认状态或装配状态未知：

```text
ShortStatus = CONDITIONAL
```

### Relay或MOS

Relay和MOS连接两个 Net 不代表永久短接。

必须知道：

- 默认状态
- 线圈或Gate控制状态
- 测试步骤中是否闭合
- 对应继电器触点或MOS导通关系

只有在指定状态下导通时，才输出：

```text
ShortStatus = CONDITIONAL
Condition = 继电器Kxx闭合 / MOS导通
```

禁止仅根据两个 PIN 分别连接不同 Net 就判定短接。

---

## 六、不能判定为短接的情况

以下情况不得判定两个 Net 短接：

- 两个 Net 通过普通非零电阻连接
- 通过电容连接
- 通过电感连接，但没有明确的直流短接规则
- 通过二极管或芯片内部电路连接
- Relay/MOS状态未知
- 只有两个 Port 名称相同
- 只有 Port 与Net Label 同名
- 同一 Net 下重复出现相同 Net Label
- 只有几何坐标接近，没有编译连接证据
- Net Tie端点被标记为 `DANGLING_NET_TIE_PIN`

---

## 七、判定优先级

AI必须按以下优先级判断：

```text
1. ELECTRICAL_SHORT_GROUP 明确记录
2. NET_TIE_GROUP 的 EffectiveShortNets
3. 同一编译 Net 下的多个不同 NET_LABEL
4. 0Ω电阻两端 Net
5. Jumper/焊桥
6. Relay/MOS条件导通
7. 无充分证据：AMBIGUOUS
```

高优先级证据存在时，不应使用低优先级推测覆盖。

---

## 八、统一输出格式

AI判定后应返回：

```text
ShortStatus:
ShortKind:
CanonicalNet:
ShortNets:
ShortObject:
Condition:
Evidence:
Reason:
```

示例：

```text
ShortStatus: CONFIRMED
ShortKind: DIRECT_NET_ALIAS
CanonicalNet: NET_A
ShortNets: NET_A | NET_B
ShortObject: DIRECT_WIRE
Condition: ALWAYS
Evidence: CSV中的ELECTRICAL_SHORT_GROUP记录
Reason: 两个不同NET_LABEL被Altium编译到同一个NetName
```

如果证据不足：

```text
ShortStatus: AMBIGUOUS
ShortKind: UNKNOWN
ShortNets: NET_A | NET_B
ShortObject:
Condition:
Evidence: 只有两个元件PIN分别连接NET_A和NET_B
Reason: 没有直接导线、Net Tie、0Ω电阻或闭合开关证据
```

## 九、核心原则

“连接到同一个器件”不等于“短接”。

只有能够证明两个 Net 属于同一个编译电气节点，或者通过确认导通的低阻/开关对象连接，才可以判定短接。任何依赖器件状态、装配状态或控制条件的连接，都必须标记为 `CONDITIONAL`，不能标记为无条件 `CONFIRMED`。