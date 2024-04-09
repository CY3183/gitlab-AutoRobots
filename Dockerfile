# 使用官方的 Python 运行时作为基础镜像
FROM python:3.9
LABEL authors="chenyin"

# 设置容器的工作目录
WORKDIR /app

# 将整个项目复制到镜像中
COPY . .

RUN python -m pip install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple && pip install -i https://mirrors.aliyun.com/pypi/simple -r requirements.txt

# 暴露 Django 项目运行的端口
# 这样做可以让容器外部的应用程序通过这个端口与容器内运行的 Django 项目进行通信

EXPOSE 8000

#容器启动时执行的默认命令。这里指定了使用 Python 运行 Django 项目中的 manage.py 文件，
#并通过 runserver 命令在 0.0.0.0:8000 地址上启动 Django 项目
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]