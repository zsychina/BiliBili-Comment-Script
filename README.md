# B站评论爬虫

按BV号列表爬取B站视频的一级评论、点赞数等，支持导出为多种格式

## 安装

1. 安装对应版本的chrome driver (edge driver)

2. 运行以下代码

    ```bash
    mkdir results
    touch config.json
    pip install selenium
    ```

    如果要保存为excel，还需要安装

    ```bash
    pip install pandas
    pip install openpyxl
    ```

3. 设置config.json，其格式为

    ```json
    {
        "driver_path": ,    // chrome driver的位置
        "max_count": 1000,  // 每个视频的最大爬取数量
        "vd_list": [        // 要爬取的BV号列表
            "BVxxxxx",      
            "BVyyyyy"       
        ]
    }
    ```

## 运行

第一次请运行

```bash
python -u first_time_login.py
```

会生成相应的cookie文件，保存在jsoncookie.json下

之后直接运行

```bash
python -u main.py
```

### 指定导出格式

默认以xlsx格式导出，如果想要以csv格式，指定

```bash
python -u main.py --format csv
```

更多功能、更多格式，请提交issue

## 声明

仅供交流学习，禁止用于商业、非法目的
