# ChatPlugin

## 大模型问答插件

### 适用场景

插件接口提供对话能力限定在知识库允许的范围内，回答内容更精准。应用场景是有知识库的情况下进行精准咨询问答。

### 接口描述

提供对用户问题进行知识检索以及大模型总结回答的能力。在数据库中对与问题最相关的知识文本进行匹配检索，大模型接口会根据问题，从检索出的知识中总结答案，并返回结果。接口支持多轮问答。

### 请求说明

**HTTP方法**：```POST```

**请求URI**：```predict```

**请求地址**：```{http url}:{port，默认9018}/{serviceName，默认llmplugin}/predict```

**请求参数**

| 参数名      | 是否必选 | 类型   | 可选值范围          | 说明                                                         |
| ----------- | -------- | ------ | ------------------- | ------------------------------------------------------------ |
| messages    | 是       | list   | -                   | 输入信息列表。列表中每一条dict是一句会话                     |
| +role       | 是       | string | "user", "assistant" | 会话的角色，"user"代表该条信息为用户问题，"assistant"代表该条信息为大模型回答 |
| +content    | 是       | string | -                   | 会话的内容                                                   |
| temperature | 否       | float  | 0~1                 | 模型答案多样性，值越小，同样的问题每次答案越固定，相反值越大，答案就越多样。默认0.1 |
| min_sim     | 否       | float  | 0~1                 | 向量知识库相似度阈值，低于该阈值的相似知识将不会作为大模型的输入。默认0.3 |
| topK        | 否       | int    | >=1                 | 向量检索阶段召回的用户输入相关知识的数量，默认3              |

**请求示例**

```json
# 单轮对话
{
	"messages": [{'role': 'user', 'content':'xxxxxx?'}],
    "temperature": 0.1, 
    "min_sim": 0.3,
    "topK":3
}

# 多轮对话需要将用户与大模型的对话历史，与新的用户问题（输入）进行拼接
{
	"messages": [
        {'role': 'user', 'content':'xxxxxx?'},
        {'role': 'assistant', 'content': 'xxxxxx'},
        {'role': 'user', 'content':'xxxxxx?'}
    ],
    "temperature": 0.1,
    "min_sim": 0.3,
    "topK":3
}

```

### 返回说明

**返回参数**

| 参数名           | 是否必选 | 类型   | 说明                                                         |
| ---------------- | -------- | ------ | ------------------------------------------------------------ |
| status           | 是       | dict   | 返回结果状态信息                                             |
| +code            | 是       | string | "0"代表没有异常；"1"代表接口返回存在异常                     |
| +error_msg       | 是       | string | 如果code为"1"，则会返回接口具体的错误信息，否为为空字符串    |
| result           | 是       | dict   | 结果存储字典                                                 |
| +message         | 是       | dict   | 接口返回信息存储字典                                         |
| ++role           | 是       | string | 会话角色，固定为"assistant"                                  |
| ++content        | 是       | string | 大模型的回复结果                                             |
| +source          | 是       | list   | 最终结果来源结果列表                                         |
| ++table_name     | 是       | string | 来源向量表名称                                               |
| ++id             | 是       | -      | 检索文本的rowguid，一般为字符串（在向量库中对应为primary key） |
| ++text           | 是       | string | 向量库中检索出的文本内容                                     |
| ++relevant_texts | 是       | dict   | 如果在算子配置时进行了多张表的配置，则根据rowguid将其他表中的文本项内容进行检索并返回。例如配置了table_1和table_2，则会返回形如{"table_1": "xxxxx", "table_2": "xxxxx"}格式内容 |
| ++sim            | 是       | float  | 输入文本与检索出文本的相似度                                 |
| +prompt          | 是       | string | 最终模型输入内容                                             |

**正确返回结果示例**

```json
{
    "status": {
        "code": "0", 
        "error_msg": ""
    }, 
    "result": {
        "message": {
            "content": "xxxxx", 
            "role": "assistant"
        },
        "source": [
            {
                "table_name": "name",
                "id": "xxxxx",
                "text": "xxxxx",
                "relevant_texts": {"name": "xxxxx"},
                "sim": 0.6
            }
        ],
        "prompt": "xxxxxx"
    }
}
```

## 部署说明

**部署方式：**MLOPS人工智能平台算子包部署

**配置步骤：**```deploy```

**配置参数**

| 参数名               | 是否必选 | 类型        | 可选值范围 | 说明                                                         |
| -------------------- | -------- | ----------- | ---------- | ------------------------------------------------------------ |
| encode_model_url     | 是       | modelchoose | -          | 文字编码模型地址，由中研院提供，上传至平台模型结果中         |
| llm_url              | 是       | modelchoose | -          | 大语言模型接口地址                                           |
| milvus_url           | 是       | string      | -          | Milvus向量数据库地址，结构为host:port★用户名★密码            |
| milvus_table_name    | 是       | string      | -          | Milvus向量数据库表名称，多个表名之间用英文逗号","分隔        |
| embedding_field_name | 是       | string      | -          | Milvus向量数据库表中embedding列名称，多个列名称之间用英文逗号","分隔 |
| doc_field_name       | 是       | string      | -          | Milvus向量数据库表中文本列名称，多个列名称之间用英文逗号","分隔 |
| milvus_metric_type   | 是       | string      | IP，L2     | 向量相似度算法，IP代表内积算法，L2代表欧式l2距离算法         |
| serviceName          | 是       | string      | -          | 服务名，默认llmplugin                                        |
| port                 | 是       | int         | -          | 端口号，默认9018                                             |

### 配置多个Milvus向量数据库表的条件与内部检索流程说明：

Milvus数据库（版本2.2.x）特性：单张表必须有且仅能有一列作为向量存储列，即embedding_field，有且必须有一列作为该表的全局唯一索引列（guid），在Milvus中成为primery key（类似其他数据库中的rowguid概念）。

因此，在Milvus构建表（在Milvus中表称为collection）时，一般要求必须有一列作为rowguid，一列为原文本（数据类型为字符串），一列为源文本对应的向量（数据类型为向量），且向量建议在存储前进行L2归一化。

如果配置多张表，则算法会在每张表的embedding_field中计算得到诺干个topK结果，再从这些结果中再进行一次相似度排序得到topK，例如表1取前5，表2取前5，则最终再在这10个结果中取前5，在这5个结果中可能表1有3项，表2有2项，但最终获得的结果文本需要将表1和表2中的拼接起来，因此需要根据表1中这3项的rowguid去表2中查找到对应文本；同理，表2中的2项也需要在表1中找到对应文本。最终整合出来的5条文本为返回项。

**示例**

背景：一份知识库中的知识内容分成了标题和内容两个部分，标题和内容一一对应，现将标题和内容中的文本分别向量化后存在milvus的两张表中，两张表可以通过构建相同的rowguid来互相索引。



**标题collection**

| rowguid/primary key | doc field | embedding field  |
| ------------------- | --------- | ---------------- |
| 001                 | abc       | [0.1, 0.2, ...]  |
| 002                 | xyz       | [0.2, 0.3, ....] |
| ...                 | ...       | ...              |

**内容collection**

| rowguid/primary key | doc field | embedding field  |
| ------------------- | --------- | ---------------- |
| 001                 | abcdefg   | [0.1, 0.2, ...]  |
| 002                 | xyzijk    | [0.2, 0.3, ....] |
| ...                 | ...       | ...              |



现需要根据用户问题，检索出知识库中最相关的前3条知识（标题+内容），则算法会在两张表中分别计算得到各自的前3相似内容，结果为6条：

| 检索来源       | 来源rowguid | 文本内容 | 相似度 |
| -------------- | ----------- | -------- | ------ |
| 标题collection | 005         | a        | 0.9    |
| 标题collection | 010         | b        | 0.8    |
| 内容collection | 006         | c        | 0.7    |
| 内容collection | 008         | d        | 0.6    |
| 标题collection | 009         | e        | 0.5    |
| 内容collection | 007         | f        | 0.4    |

在这6条结果中取前3条最相似的，因此检索结果为：

| 检索来源       | 来源rowguid | 文本内容 | 相似度 |
| -------------- | ----------- | -------- | ------ |
| 标题collection | 005         | a        | 0.9    |
| 标题collection | 010         | b        | 0.8    |
| 内容collection | 006         | c        | 0.7    |

现在需要根据rowguid，将对应另外一张表中的文本内容提取出来才能拼接成完整的标题加内容，因此最终结果为：

| rowguid | 检索来源       | 相似度 | 文本内容 | 关联来源       | 关联文本 | 最终文本 |
| ------- | -------------- | ------ | -------- | -------------- | -------- | -------- |
| 005     | 标题collection | 0.9    | a        | 内容collection | x        | ax       |
| 010     | 标题collection | 0.8    | b        | 内容collection | y        | by       |
| 006     | 内容collection | 0.7    | c        | 标题collection | z        | zc       |

## 说明

- 独立部署算子包请联系中研院并进行算子部署
- 目前算子不支持自己训练模型


