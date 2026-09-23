# -*- coding: utf-8 -*-
# sub.cpp (GBK) 尾部追加 measure_osc_4p5m + measure_osc_64k (ACTIVE); sub.h 加声明
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

measure_fns = r"""// ===================================================================
// DALI: measure_osc_4p5m - TM301 Trim_OSC_4P5M (QTMU 测频, 重构 MHz)
// treg: osc_4p5m, 16步(Table 0-15, 0xF1 bits 7-5 + 0xF2 bit0), Target=4.5MHz
// 测量: 写 EFUSE trim 值 (0xF1/0xF2) -> QTMU 测 foldback ~35KHz -> x0.128 重构 4.5MHz
// 寄存器配置在 test.cpp: 0x10=0x43, 0x56=0x33, 0x57=0x08 (DMUX_SEL=51)
// ===================================================================
void measure_osc_4p5m(TRIM_NODE *trim_node, TREG_MEASURE_FLAG flag, double *results)
{
    DWORD working_value1[SITE_NUM] = { 0 };
    DWORD working_value2[SITE_NUM] = { 0 };
    double qtmu_results[SITE_NUM] = { 0 };

    if (TEST_FLOW == FT || TEST_FLOW == CP || TEST_FLOW == QUAL || TEST_FLOW == HTOL_Burn || TEST_FLOW == QA)
    {
        FOR_EACH_SITE(site)
        {
            if (flag == TREG_MEASURE_PRE || flag == TREG_MEASURE_POST)
                if (BURN_FLAG[site] == BURNNED)
                    trim_node->copy_read_to_work(site);
            working_value1[site] = (DWORD)trim_reg.assy("EFUSE_REG_F1").get_working(site);
            working_value2[site] = (DWORD)trim_reg.assy("EFUSE_REG_F2").get_working(site);
        }

        // 写 EFUSE trim 值 (osc_4p5m 16步: 0xF1 bits 7-5 + 0xF2 bit0)
        dcm.I2CWriteData(DEV_ADDR, 0xF1, 1, working_value1);
        dcm.I2CWriteData(DEV_ADDR, 0xF2, 1, working_value2);
        delay_us(1000);

        // QTMU 测频 (nQON -> CHA), 文档化 API 替代 QTMU_GP_MEASURE 宏
        QTMU_GP.Connect(QTMUe_RELAY_CHA, 500);
        QTMU_GP.SetInSource(QTMUe_SINGLE_SOURCE_A);
        QTMU_GP.Start(QTMUe_MU1, QTMUe_10V, QTMUe_POS, 2.0, QTMUe_FILTER_PASS);
        QTMU_GP.Measure(QTMUe_MU1, QTMUe_MEAS_FREQ, 20, 10, QTMUe_TRANGE_US);
        FOR_EACH_VALID_SITE(site)
        {
            qtmu_results[site] = QTMU_GP.GetMeasureResult(site, AVERAGE_RESULT, QTMUe_MU1);  // KHz
            results[site] = qtmu_results[site] * 0.128;  // KHz->MHz 重构 (foldback /128)
        }
        QTMU_GP.Disconnect(QTMUe_RELAY_CHA, 100);
    }
}

// ===================================================================
// DALI: measure_osc_64k - TM300 Trim_OSC_64K (QTMU 测频, KHz)
// [数据缺口] treg 无 [osc_64k] 段 (已报告); D2A_OSC_64K_TRIM 3bit -> 8步
//   暂按 reg_config 0xF2 写入 (与 TRIM_REG 0xF2 字段定义矛盾, 待用户确认)
// 测量: 写 0xF2 -> QTMU 测 64KHz 直接频率 (无 foldback, Test=Direct)
// 寄存器配置在 test.cpp: 0x56=0x0C, 0x57=0x08 (DMUX_SEL=12)
// ===================================================================
void measure_osc_64k(TRIM_NODE *trim_node, TREG_MEASURE_FLAG flag, double *results)
{
    DWORD working_value1[SITE_NUM] = { 0 };

    if (TEST_FLOW == FT || TEST_FLOW == CP || TEST_FLOW == QUAL || TEST_FLOW == HTOL_Burn || TEST_FLOW == QA)
    {
        FOR_EACH_SITE(site)
        {
            if (flag == TREG_MEASURE_PRE || flag == TREG_MEASURE_POST)
                if (BURN_FLAG[site] == BURNNED)
                    trim_node->copy_read_to_work(site);
            working_value1[site] = (DWORD)trim_reg.assy("EFUSE_REG_F2").get_working(site);
        }

        // 写 EFUSE trim 值 (osc_64k 8步: 0xF2, 待确认)
        dcm.I2CWriteData(DEV_ADDR, 0xF2, 1, working_value1);
        delay_us(1000);

        // QTMU 测频 (nQON -> CHA), 文档化 API 替代 QTMU_GP_MEASURE 宏
        QTMU_GP.Connect(QTMUe_RELAY_CHA, 500);
        QTMU_GP.SetInSource(QTMUe_SINGLE_SOURCE_A);
        QTMU_GP.Start(QTMUe_MU1, QTMUe_10V, QTMUe_POS, 2.0, QTMUe_FILTER_PASS);
        QTMU_GP.Measure(QTMUe_MU1, QTMUe_MEAS_FREQ, 20, 10, QTMUe_TRANGE_US);
        FOR_EACH_VALID_SITE(site)
        {
            results[site] = QTMU_GP.GetMeasureResult(site, AVERAGE_RESULT, QTMUe_MU1);  // KHz
        }
        QTMU_GP.Disconnect(QTMUe_RELAY_CHA, 100);
    }
}"""


def detect_enc(raw):
    for enc in ('utf-8-sig', 'utf-8', 'gbk'):
        try:
            raw.decode(enc)
            return enc
        except (UnicodeDecodeError, ValueError):
            continue
    return 'gbk'


# ===== sub.cpp (GBK) 尾部追加 =====
sp = r'D:\PROJECT6-DALI\devel\source\sub.cpp'
with open(sp, 'rb') as f:
    sub_raw = f.read()
enc = detect_enc(sub_raw)
print('sub.cpp encoding:', enc)
sub_text = sub_raw.decode(enc)
add_text = measure_fns.replace('\r\n', '\n').replace('\n', '\r\n')
if not sub_text.endswith('\r\n'):
    sub_text += '\r\n'
new_sub = sub_text + '\r\n' + add_text + '\r\n'
try:
    out_bytes = new_sub.encode(enc)
except UnicodeEncodeError as e:
    print(f'sub.cpp encode 失败: {e}')
    # 逐个替换无法编码的字符
    out = new_sub
    for ch in set(out):
        try:
            ch.encode(enc)
        except UnicodeEncodeError:
            print(f'  替换无法编码字符: {ch!r} -> _')
            out = out.replace(ch, '_')
    out_bytes = out.encode(enc)
with open(sp, 'wb') as f:
    f.write(out_bytes)
print(f'sub.cpp: {len(sub_raw)} -> {len(out_bytes)} bytes, CRLF={out_bytes.count(b"\\r\\n")}')

# ===== sub.h 编码检测 + 加声明 =====
hp = r'D:\PROJECT6-DALI\devel\source\sub.h'
with open(hp, 'rb') as f:
    h_raw = f.read()
henc = detect_enc(h_raw)
print('sub.h encoding:', henc)
h_text = h_raw.decode(henc)
anchor = 'void measure_osc_4p5m(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results);'
decl = 'void measure_osc_64k(TRIM_NODE *trim_node, TREG_MEASURE_FLAG treg_measure_flag, double *results);'
if decl in h_text:
    print('sub.h: measure_osc_64k 已存在')
elif anchor in h_text:
    h_text = h_text.replace(anchor, anchor + '\r\n' + decl)
    with open(hp, 'wb') as f:
        f.write(h_text.encode(henc))
    print(f'sub.h: 已追加 measure_osc_64k 声明, CRLF={h_text.count(chr(13)+chr(10))}')
else:
    print('sub.h: 未找到 anchor!')
