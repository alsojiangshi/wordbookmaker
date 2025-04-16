import os
import re
import shutil
import glob

# 定义相对路径（基于脚本所在目录）
current_dir = os.path.dirname(__file__)  # 获取当前脚本所在目录

input_dir = os.path.join(current_dir, 'polish')
output_dir = os.path.join(current_dir, 'output')
chunk_size = 5000  # 每个文件最多5000个单词

# 确保输出目录存在
os.makedirs(output_dir, exist_ok=True)

# 检查标志文件是否存在
done_flag = os.path.join(current_dir, 'done.txt')
if not os.path.exists(done_flag):
    print("未检测到完成标志文件，等待 txtdeleter.py 处理完成...")
    exit(1)

# 清理标志文件
os.remove(done_flag)

#处理单个文件并生成输出
def process_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # 提取长度≥2的英文单词并统一转为小写
        words = [word.lower() for word in re.findall(r'\b[a-zA-Z]{2,}\b', content)]
        
        # 基于小写形式去重（保留首次出现顺序）
        unique_words = list(dict.fromkeys(words))
        
        # 生成基础文件名（保留原文件名前缀）
        file_name = os.path.basename(file_path)
        file_base, ext = os.path.splitext(file_name)
        base_output_filename = f"{file_base}_lowercase_unique_words"
        
        # 分割单词列表为多个块
        chunks = [unique_words[i:i+chunk_size] for i in range(0, len(unique_words), chunk_size)]
        
        # 写入分块后的文件
        total_files = len(chunks)
        for idx, chunk in enumerate(chunks, 1):
            output_filename = f"{base_output_filename}_part{idx}.txt"
            output_path = os.path.join(output_dir, output_filename)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(chunk) + '\n')
        
        return len(words), len(unique_words), total_files
    
    except Exception as e:
        print(f"处理文件 {file_path} 时出错: {str(e)}")
        return (0, 0, 0)

# 遍历处理所有输入文件
total_all_words = 0
total_unique_words = 0
total_output_files = 0

# 使用相对路径遍历输入文件
for file_path in glob.glob(os.path.join(input_dir, '*.txt')):
    word_count, unique_count, file_count = process_file(file_path)
    total_all_words += word_count
    total_unique_words += unique_count
    total_output_files += file_count

    # 输出单个文件处理结果
    print(f"文件 {os.path.basename(file_path)}:")
    print(f"  原始单词数：{word_count}")
    print(f"  去重后单词数：{unique_count}")
    print(f"  生成文件数：{file_count}")
    print("------------------------------")

# 清理已处理的子目录
for file_path in glob.glob(os.path.join(input_dir, '*.txt')):
    try:
        os.remove(file_path)
    except Exception as e:
        print(f"删除文件 {file_path} 时出错: {e}")

# 如果 polish 目录为空，则删除它
if not os.listdir(input_dir):
    shutil.rmtree(input_dir)

print(f"总计：")
print(f"  全部原始单词数：{total_all_words}")
print(f"  全部去重后单词数：{total_unique_words}")
print(f"  总生成文件数：{total_output_files}")
print(f"所有文件已保存至：{output_dir}")
