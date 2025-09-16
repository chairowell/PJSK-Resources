# B站UP主内容批量下载器

这是一个用于批量下载B站（哔哩哔哩）UP主专栏文章和空间图文的Python脚本，支持筛选特定标题或内容的内容。

## 功能特点

- 批量获取UP主的所有专栏文章
- 批量获取UP主的空间图文动态
- 支持通过关键词筛选特定标题或内容的内容
- 并发下载，提高效率
- 保存为HTML格式，保留原始内容和格式
- 自动下载并保存文章和图文内容中的图片
- 图片与HTML文件同名同级保存，多图时自动添加顺序后缀
- 按作者和内容类型分类保存文件
- 支持选择下载内容类型：仅文章、仅图文或全部内容
- 支持禁用图片下载功能，保留原始图片链接

## 安装依赖

首先，确保你已经安装了Python 3.6或更高版本。然后安装所需的依赖包：

```bash
pip install -r requirements.txt
```

## 使用方法

### 基本用法

你可以通过命令行参数指定UP主的mid或空间URL：

```bash
# 通过mid下载文章
python bilibili_article_downloader.py --mid 12345678

# 通过UP主空间URL下载文章
python bilibili_article_downloader.py --url https://space.bilibili.com/12345678
```

### 筛选特定标题的文章

使用`--keyword`参数可以筛选标题中包含特定关键词的文章：

```bash
python bilibili_article_downloader.py --mid 12345678 --keyword "Python"
```

### 高级选项

- `--cookies`：指定Cookies字符串，用于访问需要登录才能查看的内容
- `--output`：指定输出目录，默认为`./output`
- `--threads`：指定并发线程数，默认为5
- `--type`：指定下载内容类型，可选值：`articles`(仅文章), `opuses`(仅图文), `all`(全部)，默认为`all`
- `--opus-type`：指定图文类型（当`--type`为`opuses`或`all`时有效），可选值：`all`(全部), `article`(专栏), `dynamic`(动态)，默认为`all`
- `--no-images`：禁用图片下载，保留原始图片链接

## 示例

```bash
# 下载mid为12345678的UP主的所有文章，标题中包含"Python"关键词
python bilibili_article_downloader.py --mid 12345678 --keyword "Python"

# 使用自定义Cookies和输出目录，使用10个线程下载
python bilibili_article_downloader.py --url https://space.bilibili.com/12345678 --cookies "你的Cookies字符串" --output ./bilibili_articles --threads 10

# 仅下载空间图文，内容中包含"教程"关键词
python bilibili_article_downloader.py --mid 12345678 --keyword "教程" --type opuses

# 下载所有内容（文章和图文），但仅下载动态类型的图文
python bilibili_article_downloader.py --mid 12345678 --type all --opus-type dynamic
```

## 注意事项

1. 本工具仅用于学习和研究，请勿用于商业用途
2. 请遵守B站的用户协议，不要过度请求API
3. 部分文章可能需要登录才能访问，此时需要提供有效的Cookies
4. 大量并发请求可能会触发B站的请求限制，建议合理设置线程数

## 常见问题

### 如何获取UP主的mid？

UP主的mid是其空间URL中的数字部分，例如：`https://space.bilibili.com/12345678`中的`12345678`就是mid。

### 如何获取Cookies？

1. 使用浏览器登录B站
2. 按F12打开开发者工具
3. 在"网络"或"应用程序"标签页中找到Cookies
4. 复制`SESSDATA`和`bili_jct`等关键Cookies

### 为什么下载的文章不全？

可能的原因：
- UP主设置了部分文章仅粉丝可见，需要提供登录Cookies
- API请求频率过高被限制，可以减少线程数或增加请求间隔
- 部分文章可能已被删除

## 免责声明

本工具仅用于学习和研究目的。使用本工具产生的一切后果由使用者自行承担，与开发者无关。请尊重内容创作者的版权，合理使用下载的内容。


## 空间图文

## 获取用户空间图文

> https://api.bilibili.com/x/polymer/web-dynamic/v1/opus/feed/space

*请求方法: GET*

注: 该接口**只能**获取图文信息, 无法获取如转发动态一类的内容, 如需获取参见 [获取用户空间动态](docs/dynamic/space.md)

**URL 参数:**

| 参数名   | 类型   | 内容 | 必要性 | 备注 |
| -------- | ------ | ---- | ------ | ---- |
| host_mid | number | 被获取用户的 mid (UID) | 必要 |      |
| page     | number | 假装自己是分页信息 | 不必要 | 以 `1` 开始 |
| offset   | number | 偏移信息 | 不必要 | 上一次返回的 `offset` (同时也是最后一条的 opus id),  默认为空 |
| type     | string | 类型 | 不必要 | all: 全部 (默认)<br />article: 专栏<br />dynamic: 动态 |
| web_location | string | `333.1387` | 不必要 |  |
| w_rid    | string | WBI 签名 | 不必要 | 参见 [WBI 签名](../misc/sign/wbi.md) |
| wts      | number | UNIX 秒级时间戳 | 不必要 | 参见 [WBI 签名](../misc/sign/wbi.md) |

**JSON 回复:**

根对象:

| 字段 | 类型 | 内容 | 备注 |
| ---- | ---- | ---- | ---- |
| code | number | 返回值 | 0: 成功 |
| data | object | 数据本体 |  |
| message | string | 错误信息 | 成功时为 `0` |
| ttl | number | `1` |  |

`data` 对象:

| 字段 | 类型 | 内容 | 备注 |
| ---- | ---- | ---- | ---- |
| has_more | boolean | 是否还有更多 |  |
| items | object[] | 信息本体 |  |
| offset | string | 偏移信息 | 下次翻页请求时传入的 `offest` (同时也是最后一条的 opus id) |
| update_num | number | 更新数? | 0 |

`data.items[]` 对象:

| 字段 | 类型 | 内容 | 备注 |
| ---- | ---- | ---- | ---- |
| content | string | 文本内容 |  |
| cover | object? | 封面信息 |  |
| jump_url | string | 跳转 URL |  |
| opus_id | string | opus id |  |
| stat | object | 统计信息 |  |

`data.items[].cover` 对象:

| 字段 | 类型 | 内容 | 备注 |
| ---- | ---- | ---- | ---- |
| height | number | 高度 |  |
| url | string | 图片 URL |  |
| width | number | 宽度 |  |

`data.items[].stat` 对象:

| 字段 | 类型 | 内容 | 备注 |
| ---- | ---- | ---- | ---- |
| like | string | 点赞数 | 是个字符串 |
| view | string | 浏览数 | 仅当获取登录状态下获取自己的时才存在, 也是个字符串 |

**示例:**

获取 `645769214` 空间的最近几条全部图文

```shell
curl 'https://api.bilibili.com/x/polymer/web-dynamic/v1/opus/feed/space' \
--url-query 'host_mid=645769214'
```

<details>
<summary>查看响应示例:</summary>

```json
{
  "code": 0,
  "data": {
    "has_more": true,
    "items": [
      {
        "content": "我在 Google I/O 2025 的 puzzle 取得了获胜的优异成绩, 你也来试试吧",
        "cover": {
          "height": 1640,
          "url": "http://i0.hdslb.com/bfs/new_dyn/a48c47c07bf19f07c01b489eb6b42e63645769214.jpg",
          "width": 720
        },
        "jump_url": "//www.bilibili.com/opus/1057955152016703512",
        "opus_id": "1057955152016703512",
        "stat": {
          "like": "1"
        }
      },
      {
        "content": "通过 DevTools 绕过 SSR 抓包某站专栏正文接口",
        "cover": {
          "height": 430,
          "url": "http://i0.hdslb.com/bfs/article/9071997152b6fec0ae465fe2a86b580e645769214.jpg",
          "width": 768
        },
        "jump_url": "//www.bilibili.com/opus/1056353752004427792",
        "opus_id": "1056353752004427792",
        "stat": {
          "like": "3"
        }
      },
      {
        "content": "今天也是看上 Minecraft 大电影 了, 看的人几乎没有, 虽然看的是中配, 总体上感觉剧情有趣甚至有点小感动, 音乐也感觉不错, 价格也实惠",
        "cover": {
          "height": 4080,
          "url": "http://i0.hdslb.com/bfs/new_dyn/408d4e2b2ad8df6873c303cf26f571db645769214.jpg",
          "width": 3060
        },
        "jump_url": "//www.bilibili.com/opus/1052711525276450824",
        "opus_id": "1052711525276450824",
        "stat": {
          "like": "3"
        }
      },
      {
        "content": "糟了没注意, 自己成小丑了",
        "cover": {
          "height": 1640,
          "url": "http://i0.hdslb.com/bfs/new_dyn/6ebb3894cfab53966d6e440e4f5a905d645769214.jpg",
          "width": 720
        },
        "jump_url": "//www.bilibili.com/opus/1051313732437671938",
        "opus_id": "1051313732437671938",
        "stat": {
          "like": "3"
        }
      },
      {
        "content": "好消息, 我免费了, 想玩的随时联系\nhttps://t.me/c/2148747379/77",
        "cover": {
          "height": 720,
          "url": "http://i0.hdslb.com/bfs/new_dyn/fbc2b38406099df0bdaea47d08daa6f1645769214.jpg",
          "width": 1640
        },
        "jump_url": "//www.bilibili.com/opus/1050579658107518984",
        "opus_id": "1050579658107518984",
        "stat": {
          "like": "2"
        }
      },
      {
        "content": "认真的, 我的 Linux 发行版是 Android",
        "cover": {
          "height": 1080,
          "url": "http://i0.hdslb.com/bfs/new_dyn/3e512d84361323c319f79061d2f078d1645769214.jpg",
          "width": 1440
        },
        "jump_url": "//www.bilibili.com/opus/1032607998809210903",
        "opus_id": "1032607998809210903",
        "stat": {
          "like": "8"
        }
      },
      {
        "content": "于学校机房启动 QEMU 珍贵影像",
        "cover": {
          "height": 1080,
          "url": "http://i0.hdslb.com/bfs/new_dyn/2fdc7524449b029f8baf241d94663256645769214.jpg",
          "width": 1440
        },
        "jump_url": "//www.bilibili.com/opus/993403941079220225",
        "opus_id": "993403941079220225",
        "stat": {
          "like": "3"
        }
      },
      {
        "content": "BAC 正处于历史以来最困难的时期 - 中秋考古有感",
        "cover": {
          "height": 188,
          "url": "https://i0.hdslb.com/bfs/article/0c9b5e20356e07f89a8bb7769fef8eeb645769214.jpg",
          "width": 640
        },
        "jump_url": "//www.bilibili.com/opus/985444108243828741",
        "opus_id": "985444108243828741",
        "stat": {
          "like": "7"
        }
      },
      {
        "content": "发送文件到手机的 N 种正确姿势",
        "cover": {
          "height": 420,
          "url": "http://i0.hdslb.com/bfs/article/56a4024abebf7ed1166a1d247bb5cf64645769214.jpg",
          "width": 750
        },
        "jump_url": "//www.bilibili.com/opus/971804623539011587",
        "opus_id": "971804623539011587",
        "stat": {
          "like": "8"
        }
      },
      {
        "content": "我在朝鲜?",
        "cover": {
          "height": 468,
          "url": "http://i0.hdslb.com/bfs/new_dyn/ea12cca6abd75fe3fb5ad1abd1f347d3645769214.png",
          "width": 474
        },
        "jump_url": "//www.bilibili.com/opus/971255284349534210",
        "opus_id": "971255284349534210",
        "stat": {
          "like": "5"
        }
      },
      {
        "content": "一周没上 B 站就 99+ 了?",
        "cover": {
          "height": 284,
          "url": "http://i0.hdslb.com/bfs/new_dyn/9e3b889fd2dc75e9bae38a13e55fee26645769214.png",
          "width": 165
        },
        "jump_url": "//www.bilibili.com/opus/970197833343827970",
        "opus_id": "970197833343827970",
        "stat": {
          "like": "6"
        }
      },
      {
        "content": "今天因为Linux被骂, 决定放弃支持 Windows. 而且明天要开始军训了, 将停更若干时间, 遂发此动态, 望不知.",
        "cover": {
          "height": 1080,
          "url": "http://i0.hdslb.com/bfs/new_dyn/0f6f939334104ddc347566514fa4bfa7645769214.jpg",
          "width": 1440
        },
        "jump_url": "//www.bilibili.com/opus/967717348014293017",
        "opus_id": "967717348014293017",
        "stat": {
          "like": "73"
        }
      },
      {
        "content": "我的萌ICP备案通过了!",
        "cover": {
          "height": 2712,
          "url": "http://i0.hdslb.com/bfs/new_dyn/0a9bb3e82bbefe499b10b7fd02f2a4f4645769214.jpg",
          "width": 1220
        },
        "jump_url": "//www.bilibili.com/opus/956241611959828547",
        "opus_id": "956241611959828547",
        "stat": {
          "like": "1"
        }
      },
      {
        "content": "新年第一个AP",
        "cover": {
          "height": 1220,
          "url": "https://album.biliimg.com/bfs/new_dyn/ea5a39d37a4a1f20f32b25bfed466004645769214.jpg",
          "width": 2712
        },
        "jump_url": "//www.bilibili.com/opus/896448108088524805",
        "opus_id": "896448108088524805",
        "stat": {
          "like": "1"
        }
      },
      {
        "content": "新年快乐？",
        "cover": {
          "height": 605,
          "url": "https://album.biliimg.com/bfs/new_dyn/dab5d3e2ff03027215e5bfd4933abe45645769214.jpg",
          "width": 1220
        },
        "jump_url": "//www.bilibili.com/opus/896342627995090966",
        "opus_id": "896342627995090966",
        "stat": {
          "like": "1"
        }
      },
      {
        "content": "我回苏州了",
        "cover": {
          "height": 1280,
          "url": "https://album.biliimg.com/bfs/new_dyn/65c880f64997fab0c79527649d7fbe1b645769214.png",
          "width": 720
        },
        "jump_url": "//www.bilibili.com/opus/831507996405137432",
        "opus_id": "831507996405137432",
        "stat": {
          "like": "1"
        }
      },
      {
        "content": "Phigros RKS 12 纪念",
        "cover": {
          "height": 720,
          "url": "https://album.biliimg.com/bfs/new_dyn/dab03003aee2166987428857acbf4ffb645769214.png",
          "width": 1280
        },
        "jump_url": "//www.bilibili.com/opus/830690195959447605",
        "opus_id": "830690195959447605",
        "stat": {
          "like": "0"
        }
      },
      {
        "content": "现在知道B站推荐机制有多烂了吧",
        "cover": {
          "height": 1280,
          "url": "https://album.biliimg.com/bfs/new_dyn/05a5f769bed2705d2c8c3c69f60441df645769214.png",
          "width": 720
        },
        "jump_url": "//www.bilibili.com/opus/829284474633060387",
        "opus_id": "829284474633060387",
        "stat": {
          "like": "0"
        }
      },
      {
        "content": "求证: B站创始人们的成分\n证: [图片]",
        "cover": {
          "height": 1600,
          "url": "https://album.biliimg.com/bfs/new_dyn/830a9bbc3d5179a6d33af97e5baac7c8645769214.jpg",
          "width": 720
        },
        "jump_url": "//www.bilibili.com/opus/828071498582327315",
        "opus_id": "828071498582327315",
        "stat": {
          "like": "1"
        }
      },
      {
        "content": "如果排除掉可能的误差, 14=12.",
        "cover": {
          "height": 720,
          "url": "https://album.biliimg.com/bfs/new_dyn/79823dd0b617af6fc71126d6e042de3f645769214.png",
          "width": 1280
        },
        "jump_url": "//www.bilibili.com/opus/827727935543705620",
        "opus_id": "827727935543705620",
        "stat": {
          "like": "1"
        }
      }
    ],
    "offset": "827727935543705620",
    "update_num": 0
  },
  "message": "0",
  "ttl": 1
}
```
</details>

<!-- Generated by json-apidoc-gen @ 2025-05-01T00:59:41.402217612Z -->