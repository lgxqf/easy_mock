调用mock接口

```sh
$ curl -X POST 'http://172.20.25.168:9000/login' -d '{"username":"zhangsan", "password": "123"}' | python -m json.tool
返回结果：
{
    "code": 2,
    "msg": "gmBiSDVlixdNqntqciZHkyHwsLglpw",
    "token": "ZeyZODPPxnd",
    "username": "zhangsan"
}
```


调用mock接口
```sh
根据 response schema 返回随机数
$ curl -X POST 'http://172.20.25.168:9000/login/mcw' -d '{"username":"zhangsan", "password": "123"}' | python -m json.tool
返回结果：
{
    "code": 93,
    "msg": "qwWtdNaSuTbDYzSAODvBGvrrYaUPkXejjSdWmcnVtxKJsuwIPzFwGzSFBFPiKqAXGjUPClpVUKzXFVsFFNUPC",
    "token": "nLqGauEqZotIsq"
}


匹配自定义返回值

curl -X POST 'http://172.20.25.168:9000/login' -d '{"username":"root", "password": "123"}' | python -m json.tool
返回结果：
{
    "code": 1,
    "msg": "登录成功",
    "token": "5lCadRru(ADn2IE!$LV%x%JF3JNmz*Nf5nFieUG!r((&esi2CLI$jb!227Lh"
}
	
```

定义 json schema

```yaml
  response_schema:
    {
      "type": "object",
      "properties": {
        "code": {
          "type": "integer",
          "maximun": 1, # 修改数据范围 为 0-1
          "minimun": 0 # 修改数据范围 为 0-1
        },
        "msg": {
          "type": "string"
            "maxLength": 10, # 修改string长度为 5-10
          "minLength": 5 # 修改string长度为 5-10
        },
        "token": {
          "type": "string"
        },
      },
      "required": [
          "code",
          "msg"
      ]
    }
```

调用mock接口

```sh
$ curl -X POST 'http://172.20.25.168:9000/login' -d '{"username":"zhangsan", "password": "123"}' | python -m json.tool
返回结果：
{
    "code": 1,
    "msg": "Nlgedsc",
    "token": "sImDahqhaSKuosjXbFlcTAanzvV"
}
```