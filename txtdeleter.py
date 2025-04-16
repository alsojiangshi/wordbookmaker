import os
import re
import shutil
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk import pos_tag
from nltk.corpus import wordnet
from concurrent.futures import ThreadPoolExecutor

# 获取当前脚本所在目录作为基准路径
BASE_DIR = os.path.dirname(__file__)

# 定义相对路径（基于脚本所在目录）
a_path = os.path.join(BASE_DIR, 'bedeleted')
b_path = os.path.join(BASE_DIR, 'deleterv')
output_path = os.path.join(BASE_DIR, 'polish')

# 下载必要的nltk数据（静默模式）
nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)

lemmatizer = WordNetLemmatizer()

def get_wordnet_pos(treebank_tag):
    """将NLTK的词性标签转换为WordNet格式"""
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN  # 默认为名词

#收集需要剔除的单词集合
def collect_words_from_b_path(b_path):
    words = set()
    for file in os.listdir(b_path):
        if file.endswith('.txt'):
            try:
                with open(os.path.join(b_path, file), 'r', encoding='utf-8') as f:
                    for line in f:
                        tokens = word_tokenize(line.strip())
                        for word in tokens:
                            if re.fullmatch(r"[A-Za-z\-']+", word):  # 过滤非字母字符
                                words.add(word.lower())  # 统一转为小写
            except Exception as e:
                print(f"处理文件 {file} 时发生错误: {e}")
    print(f"剔除词集合大小: {len(words)}")
    return words

# 词形还原函数（支持多线程）
def lemmatize_file(input_file, output_file):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.read().splitlines()  # 优化读取方式

        lemmatized_lines = []
        for line in lines:
            tokens = word_tokenize(line.strip())
            tagged = pos_tag(tokens)  # POS标注
            lemmatized_line = []

            for word, tag in tagged:
                if re.fullmatch(r"[A-Za-z\-']+", word):
                    wn_tag = get_wordnet_pos(tag)  # 获取WordNet词性
                    lemma = lemmatizer.lemmatize(word.lower(), wn_tag)  # 词形还原
                    lemmatized_line.append(lemma)
                else:
                    lemmatized_line.append(word)  # 非单词直接保留

            lemmatized_lines.append(' '.join(lemmatized_line))

        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lemmatized_lines))
            
    except Exception as e:
        print(f"词形还原失败: {input_file} -> {str(e)}")

def remove_words_and_save(input_file, output_file, words_to_remove):
    """删除指定词汇"""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 构建正则表达式模式（全词匹配且不区分大小写）
        pattern = re.compile(r'\b(' + '|'.join(map(re.escape, words_to_remove)) + r')\b', flags=re.IGNORECASE)
        cleaned_content = pattern.sub('', content)  # 一次性替换所有匹配项
        # 清理多余空格
        cleaned_content = re.sub(r'\s+', ' ', cleaned_content).strip()
        
        # 写入结果时处理空文件
        if cleaned_content:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
        else:
            print(f"文件 {input_file} 处理后为空，未生成输出文件")
            
    except Exception as e:
        print(f"清理剔除词失败: {input_file} -> {str(e)}")

# 主处理函数
def process_a_path(a_path, b_path, output_path):
    # 中间目录路径（在output_path下）
    lemmatized_dir = os.path.join(output_path, "lemmatized")
    os.makedirs(lemmatized_dir, exist_ok=True)
    
    # 第一步：词形还原所有文件
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        for file in os.listdir(a_path):
            if file.endswith('.txt'):
                input_file = os.path.join(a_path, file)
                output_file = os.path.join(lemmatized_dir, file)
                futures.append(executor.submit(lemmatize_file, input_file, output_file))
        
        # 等待所有任务完成
        for future in futures:
            future.result()

    # 第二步：收集剔除词列表
    words_to_remove = collect_words_from_b_path(b_path)

    # 第三步：清理剔除词
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        for file in os.listdir(lemmatized_dir):
            if file.endswith('.txt'):
                input_file = os.path.join(lemmatized_dir, file)
                output_file = os.path.join(output_path, file)
                futures.append(executor.submit(remove_words_and_save, input_file, output_file, words_to_remove))
        
        # 等待所有任务完成
        for future in futures:
            future.result()

    # 清理中间文件
    shutil.rmtree(lemmatized_dir)

# 直接执行处理（路径已改为相对路径）
process_a_path(a_path, b_path, output_path)

# 创建标志文件，表示处理完成
done_flag = os.path.join(BASE_DIR, 'done.txt')
with open(done_flag, 'w') as f:
    f.write('Processing completed.\n')

try:
    polish_script = os.path.join(BASE_DIR, 'polish.py')
    if os.path.exists(polish_script):
        print("正在运行 polish.py...")
        os.system(f'python "{polish_script}"')  # 调用 polish.py
    else:
        print("polish.py 文件不存在，跳过运行")
except Exception as e:
    print(f"运行 polish.py 时发生错误: {e}")