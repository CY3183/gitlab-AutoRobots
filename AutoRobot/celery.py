import os
from celery import Celery
from django.conf import settings
# 设置celery的环境变量和django-celery的工作目录
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AutoRobot.settings")
# 实例化celery应用，传入服务器名称
app = Celery("AutoRobot")
# 加载celery配置
app.config_from_object("django.conf:settings")
# 如果在项目中，创建了task.py,那么celery就会沿着app去查找task.py来生成任务
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# 手动导入并注册你的任务
from Sign_Listen_Form.time_task.task import mytask
app.register_task(mytask)

# # 定义定时任务调度
app.conf.beat_schedule = {
    'execute-every-minute': {
        'task': 'Sign_Listen_Form.time_task.task.mytask',
        'schedule': 180.0,  # 每3分钟执行一次
    },
}