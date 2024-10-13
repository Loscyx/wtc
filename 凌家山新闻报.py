import requests
from lxml import etree
import os
from multiprocessing import Pool

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0'
}


def find_num(url):
    try:
        resp = requests.get(url)
        resp.encoding = 'utf-8'
        resp_text = etree.HTML(resp.text)
        sum_num = resp_text.xpath('//em[@class="all_pages"]/text()')
        return sum_num[0] if sum_num else "0"
    except Exception as e:
        print(f"在 find_num 中无法获取页面：{e}")
        return "0"


def process_big_title(big_title, title_index):
    base_url = 'https://news.wtc.edu.cn/'
    if not os.path.exists(f'./内容/凌家山新闻报/{big_title}'):
        os.makedirs(f'./内容/凌家山新闻报/{big_title}')
    sum_num = find_num(base_url + f'{title_index}/list.htm')
    for page_number in range(int(sum_num)):
        find_url = base_url + f'{title_index}/list{page_number}.htm'
        try:
            resp = requests.get(find_url, headers=headers)
            resp.encoding = 'utf-8'
            url_set_text = etree.HTML(resp.text)
            url_set = url_set_text.xpath('//span[@class="Article_Title"]/a/@href')
            for href in url_set:
                url = base_url + href
                try:
                    resp = requests.get(url, headers=headers)
                    resp.encoding = 'utf-8'
                    url_text = etree.HTML(resp.text)
                    title = url_text.xpath('//h1[@class="arti_title"]/text()')
                    if title:
                        title = title[0].strip()
                        content = url_text.xpath('//div[@class="wp_articlecontent"]//text()')
                        print(f'正在下载文章{title}')
                        filename = title.replace('/', '').replace('\\', '').replace(':', '').replace('*', '').replace('?', '').replace('"', '').replace('<', '').replace('>', '').replace('|', '')
                        if not os.path.exists(f'./内容/凌家山新闻报/{big_title}/{filename}.txt'):
                            with open(f'./内容/凌家山新闻报/{big_title}/{filename}.txt', 'w', encoding='utf-8') as f:
                                f.write(title + '\n')
                                for line in content:
                                    f.write(line.strip() + '\n')
                            print(f'文章{title}下载完成')
                except Exception as e:
                    print(f"无法获取或写入文章：{e}")
        except Exception as e:
            print(f"无法获取列表页面：{e}")


def fetch_and_write_content():
    url = 'https://news.wtc.edu.cn/346/list.htm'
    try:
        resp = requests.get(url)
        resp.encoding = 'utf-8'
        resp_text = etree.HTML(resp.text)
        resp_title = resp_text.xpath('//span[@class="item-name"]//text()')
        resp_title = resp_title[1:]
        index = [i for i in range(334, 347)]
        with Pool() as pool:
            pool.starmap(process_big_title, zip(resp_title, index))
    except Exception as e:
        print(f"在 fetch_and_write_content 中无法获取页面：{e}")


fetch_and_write_content()