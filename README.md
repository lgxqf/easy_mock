# Easy Mock

## 简单、易用的接口Mock工具

根据Yaml文件快速生成Mock接口

## v 1.0 主要功能
- 根据Yaml文件内容返回Mock数据，两种方式： 
  - 一、根据request返回defined_data_list中与之匹配的response
  - 二、若defined_data_list未定义或无与request匹配的response,则根据response_schema返回随机数据：
    - 支持的随机数据类型:
      - bool 
      - int 
      - float 
      - double 
      - string
- 根据PB(.proto)生成Mock接口文件
    - 生成接口时可通过res和req选项生成response_schema和request_schema
- 根据request-schema对输入的数据做校验
- 支持命令行配置参数
- 支持ini文件配置
- 支持输入文件和目录
- 支持http/https
- 支持对request和response做定制化处理（见自定义扩展）
- 支持延时返回(sleep关键字)

## To Do

- 支持Swagger定义的接口文件
- 支持Request,Response schema存放在单独的文件

## 安装

```sh
两种安装方式：
一、pip安装（不需要源码）
pip install easy-mock

二、源码安装
下载源码并进入到setup.py所在目录
python setup.py install
```

## 使用

### 查看帮助

```sh
$ easy_mock -h
usage: easy_mock [-h] [-v] [-p PORT] [-https] [-req] [-res] file_path

Generate mock service according to the YAML/JSON file in the current directory

positional arguments:
  file_path      yaml configuration file, directory or .proto file

optional arguments:
  -h, --help     show this help message and exit
  -v, --version  show version
  -p PORT        port that needs mock service.
  -https         enable mock server https protocol
  -req           generate request_schema in yaml
  -res           generate response_schema in yaml

```

### 将PB转换为Yaml

**参数为.proto文件类型时生成yaml文件**
```sh
easy_mock server.proto -res
输出server.yml
```

### 启动Mock Server
**参数为.yml or .yaml文件时启动mock server**

```sh
easy_mock example.yml
```

### Yaml文件示例及详解
#### 精简写法
```yaml
apis:
  # 最精简写法
  - url: login # 接口路径
    method: GET # 接口方法
    defined_data_list: # request与response的匹配关系
      [
        {
          body: { "username": "edison", "password": "123" },
          response: { "code": -1, "msg": "密码输入不正确" }
        }
      ]
```

#### 复杂写法
```yaml
  - url: login # 接口路径
    method: POST # 接口方法
    sleep: 5 # （可选）延迟返回时间 单位：秒
    request_schema: # （可选）用于对request body做合法性校验
      {
        "type": "object",
        "properties": {
          "username": {
            "type": "string"
          },
          "password": {
            "type": "string"
          },
        },
        "required": [
            "username",
            "password"
        ]
      }
    response_schema: # (可选) 根据schema生成response随机数据  response_schema 和 defined_data_list 二者不可全为空
      {
        "type": "object",
        "properties": {
          "code": {
            "type": "integer", # 数据类型
            "maximun": 100, # 数据范围 最大
            "minimun": 1 # 数据范围 最小
          },
          "msg": {
            "type": "string"
          },
          "token": {
            "type": "string"
          },
        },
        "required": [ # required中的字段，response中必须返回, token字段则随机返回
            "code",
            "msg"
        ]
      }
    defined_data_list: # 自定义返回 如果请求体于list中的body匹配， 则返回对应的response  response_schema 和 defined_data_list必须有一个匹配
      [
        {
          body: { "username": "edison", "password": "123" },
          response: { "code": -1, "msg": "密码输入不正确" }
        },
        {
          body: { "password": "123" },
          response: { "code": -1, "msg": "用户名是必填的" }
        }
      ]
```


## 自定义扩展

在当前目录下新建python文件 `processor.py`

```sh
$ touch processor.py
$ vim processor.py

# 函数命名无限制，在yaml指定函数名即可 
def xxx_setup(req): 

    req["username"] = "abc"
   
    return req

def xxx_teardown(req, resp):
 
    resp["age"] = 100
    
    return resp
```

在YAML文件中新增`setup` or `teardown`字段

```yaml
apis:
  login:
    name: 用户登录
    desc: 用户登录成功，接口会返回一个token
    method: POST
    setup: xxxx_setup # 指定前置处理函数名，此函数接受一个参数, 对请求体做前置操作
    teardown: xxx_teardown # 指定后置处理函数名，此函数接受两个参数, 对请求体和响应体做后置操作
```

## 参考文档

- Json schema用法 http://json-schema.org/
- JSON Schema入门 https://www.jianshu.com/p/1711f2f24dcf?utm_campaign=hugo
- python打包及支持pip安装 https://blog.csdn.net/sinat_33718563/article/details/88928950
- 常用命令：
  * curl -X POST 'http://172.20.25.168:9000/login/mcw' -d '{"username":"zhangsan", "password": "123"}' | python -m json.tool

