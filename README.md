
# Word-book Maker

一个用于英文文本清洗、词形还原与去重的批处理工具，支持多线程处理，适合大规模文本预处理。
例如：我想要制作关于某英文名著的词书导入至不背单词，但是我不想其中包含四级单词，我可以将包含四级单词的文本置于 `deleterv/` ，名著文本置于 `bedeleted/` 。

## 项目功能

1. **批量词形还原**：使用 NLTK 对 `bedeleted/` 下的所有文本文件进行英文词形还原。  
2. **剔除敏感词**：根据 `deleterv/` 中提供的词汇列表，批量清除 `bedeleted/` 中内容。  
3. **去重输出**：对处理结果进行单词去重，并按 5000 个词一份拆分保存。  
4. **自动流程**：`txtdeleter.py` 执行完自动调用 `polish.py` 继续处理。  

## 项目结构

```
.
├── bedeleted/        # 待处理的原始文本
├── deleterv/         # 包含需要剔除的词汇
├── polish/           # 中间处理结果（会被 polish.py 清理）
├── output/           # 最终去重后的文本块输出
├── txtdeleter.py     # 主处理脚本（词形还原 + 剔除词）
├── polish.py         # 后处理脚本（去重 + 拆分）
├── done.txt          # 中间处理完成标志文件（自动生成）
├── requirements.txt  # Python 依赖列表
└── README.md
```

## 安装依赖

请确保使用 Python 3.7+

```bash
pip install -r requirements.txt
```

此外，程序依赖一些 NLTK 数据包，**首次运行前**请执行以下命令手动下载（也可以等待程序自动下载）：

```python
import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
```

## 使用方法

在项目目录下执行：

```bash
python txtdeleter.py
```

执行完成后，最终去重分块后的文本将保存在 `output/` 目录中。

## 示例输入输出

- `bedeleted/example.txt`：
  ```
  The cats are running faster than the dogs.
  ```

- `deleterv/stopwords.txt`：
  ```
  the
  than
  ```

- 输出文件 `output/example_lowercase_unique_words_part1.txt`：
  ```
  cat
  are
  running
  faster
  dog
  ```

## 注意事项

- 所有输入输出路径均为相对路径，程序无需修改即可运行。
- 中间产物 `polish/` 和 `done.txt` 会在流程中自动清理。
- 多线程处理适用于小中型项目，极大量数据建议拆分运行。

## 致谢

在制作本项目的过程中，[KyleBing/english-vocabulary](https://github.com/KyleBing/english-vocabulary) 项目提供了宝贵的词汇资源，帮助我制作词书。

感谢 [KyleBing](https://github.com/KyleBing)辛勤工作和贡献！
