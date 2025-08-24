# 使用輕量級 Python 基底映像
FROM python:3.11-slim


# 建議安裝基礎依賴（Open3D wheels 一般可直接 pip 裝；保守加一些常用系統庫）
RUN apt-get update \
&& apt-get install -y --no-install-recommends \
build-essential \
libgl1 \
ca-certificates \
&& rm -rf /var/lib/apt/lists/*


WORKDIR /workspace
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt


# 放入程式
COPY app ./app


# 預設啟動 Jupyter Lab（亦可改成直接 python 執行）
EXPOSE 8888
CMD ["bash", "-lc", "jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --NotebookApp.token='' --NotebookApp.password='' --NotebookApp.allow_origin='*'"]