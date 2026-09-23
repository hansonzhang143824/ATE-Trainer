void measure_mnt_v1p2_buf(TRIM_NODE *node, TREG_MEASURE_FLAG flag, double *results) {
  DWORD value = trim_reg.assy("EFUSE_REG_F6").get_working(0);
  dcm.I2CWriteData(DEV_ADDR, 0xF6, 1, value);
  results[0] = NTC_FOVI.GetMeasResult(0, MVRET) * 1e3;
}
