# android自动构建python脚本

## 零、配置
```python
from setuptools import setup

setup(
    author='handy',
    author_email='cvdnn@foxmail.com',
    url='https://github.com',

    license='Apache v2.0',
    description='python lang units',

    name='py-cli',
    version='1.0',
    packages=['xcli'],

    install_requires=['androguard', 'oss2', 'requests']
)
```

## 一、准备环境
```shell script
 pip install twine pytest
```

## 二、PyPi
0. 在[Pypi](https://pypi.org/)上注册账号，并创建`API tokens`，复制证书到`~/.pypirc` 
```text
[pypi]
  username = __token__
  password = pypi-xxxxxx
```
0. 设置权限
```shell script
chmod 600 ~/.pypirc
```

## 三、发布SDK
```shell script
python setup.py sdist
twine upload dist/*
```

## 四、应用
```shell script
# 安装SDK
pip install py-cli

# 运行测试用例
pytest -s
```

