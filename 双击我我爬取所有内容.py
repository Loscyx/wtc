import os  
from multiprocessing import Process  

# 定义要执行的脚本  
scripts = [  
    '凌家山新闻报.py',  
    '所有信息的提取.py',  
    '智能商务学院信息爬取.py'  
]  

# 定义一个执行脚本的函数  
def run_script(script):  
    os.system(f'python {script}')  

if __name__ == '__main__':  
    processes = []  

    # 创建进程并启动  
    for script in scripts:  
        process = Process(target=run_script, args=(script,))  
        processes.append(process)  
        process.start()  

    # 等待所有进程完成  
    for process in processes:  
        process.join()  

    print("所有脚本已完成执行。")