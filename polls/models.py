from django.db import models

class Stock(models.Model):
    date = models.DateField(unique=True, verbose_name="交易日期")

    open = models.FloatField(verbose_name="开盘价")
    high = models.FloatField(verbose_name="最高价")
    low = models.FloatField(verbose_name="最低价")
    last = models.FloatField(verbose_name="最后成交价")
    close = models.FloatField(verbose_name="收盘价")

    total_trade_quantity = models.BigIntegerField(verbose_name="成交量")
    turnover_lacs = models.FloatField(verbose_name="成交额（万）")

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.date} | 开:{self.open} 收:{self.close}"
