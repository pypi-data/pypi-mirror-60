# 安装方法

提供两种方式。在中国大陆境内建议通过手动导入数据文件。
境外建议直接下载现成的数据文件。

## 手动合成数据文件

1. 下载[fxcm-data-graber](https://neworld.science:8443/newtrader/fxdatagraber).
```bash
git clone https://neworld.science:8443/newtrader/fxdatagraber
```
2. 然后运行，从而下载数据,
```bash
cd fx-market-data-graber
pip install -r requirements.txt
python main.py
```
3. 通过本项目提供的工具合成数据文件

先切换到本目录下
```bash
python tools/data_import.py -i ../fxdatagraber/data/m1
```
其中`../fxdatagraber/data/m1`用来指代数据文件位置

喝两口咖啡，脚本运行结束即大功告成。

## 直接下载

以下面的方法运行即可

```bash
pip install -r requirements.txt
python install.py
```

注意，如果在国内这个过程应该非常慢。