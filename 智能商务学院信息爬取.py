import requests
from lxml import etree
import os
from concurrent.futures import ProcessPoolExecutor, as_completed

# Corrected user agent header
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0'
}


def find_institution_name():
    url = 'https://www.wtc.edu.cn/410/list.htm'
    resp = requests.get(url)
    resp.encoding = 'utf-8'
    resp_text = etree.HTML(resp.text)

    big_institution_name = resp_text.xpath('//div[@id="wp_content_w6_0"]/p/strong//text()')
    government_organization_name = resp_text.xpath("//div[@id='l-container']//p[2]/a//text()")
    educational_organization_name = resp_text.xpath("//div[@id='l-container']//p[6]/a/span//text()")

    if len(educational_organization_name) > 3:
        new_element = educational_organization_name.pop(2) + educational_organization_name.pop(2)
        educational_organization_name.insert(2, new_element)

    scientific_institution_name = resp_text.xpath("//p[10]/a//text()")
    return big_institution_name, government_organization_name, educational_organization_name, scientific_institution_name


def find_institution_url():
    url = 'https://www.wtc.edu.cn/410/list.htm'
    resp = requests.get(url)
    resp.encoding = 'utf-8'
    resp_text = etree.HTML(resp.text)

    government_organization_url = resp_text.xpath("//div[@id='l-container']//p[2]/a/@href")
    educational_organization_url = resp_text.xpath("//div[@id='l-container']//p[6]/a/@href")
    scientific_institution_url = resp_text.xpath("//p[10]/a//@href")
    return government_organization_url, educational_organization_url, scientific_institution_url


def find_small_title_name(basic_url):
    try:
        resp = requests.get(basic_url)
        resp.encoding = 'utf-8'
        resp_text = etree.HTML(resp.text)
        return resp_text.xpath('//span[@class="title"]/text()')
    except Exception as e:
        print(f"Error fetching titles: {e}")
        return []


def find_small_title_url(basic_url):
    try:
        resp = requests.get(basic_url)
        resp.encoding = 'utf-8'
        resp_text = etree.HTML(resp.text)
        return resp_text.xpath('//div[@class="more_btn"]/a/@href')
    except Exception as e:
        print(f"Error fetching URLs: {e}")
        return []


def deal_small_title_url(url_set):
    return [i.split('/')[-2] for i in url_set]


def find_num(url):
    try:
        resp = requests.get(url)
        resp.encoding = 'utf-8'
        resp_text = etree.HTML(resp.text)
        sum_num = resp_text.xpath('//em[@class="all_pages"]/text()')
        return sum_num[0] if sum_num else "0"
    except Exception as e:
        print(f"Error fetching page number: {e}")
        return "0"


def get_download_url(url):
    try:
        resp = requests.get(url, headers=headers)
        resp.encoding = 'utf-8'
        url_text = etree.HTML(resp.text)
        if url_text.xpath('//span[@class="Article_Title"]/a/@href'):
            return url_text.xpath('//span[@class="Article_Title"]/a/@href')
        elif url_text.xpath('//span[@class="news_title"]/a/@href'):
            return url_text.xpath('//span[@class="news_title"]/a/@href')
    except Exception as e:
        print(f"Error fetching download URLs: {e}")
        return []


def download_articles(big_institution_name, organization_name, small_title_name, basic_url, middle_url):
    try:
        dir_path = f"./{big_institution_name}/{organization_name}/{small_title_name}"
        print(dir_path)
        os.makedirs(dir_path, exist_ok=True)
        base_url = f'{basic_url}/{middle_url}/list.htm'
        print(base_url)
        title_index = find_num(base_url)
        print(title_index)
        for i in range(1, int(title_index) + 1):
            url = f'{basic_url}/{middle_url}/list{i}.htm'
            content_url = get_download_url(url)
            for text_url in content_url:
                answer_url = basic_url + text_url
                print(answer_url)
                resp = requests.get(answer_url, headers=headers)
                resp.encoding = 'utf-8'
                url_text = etree.HTML(resp.text)
                if url_text.xpath('//h1[@class="arti_title"]/text()'):
                    title = url_text.xpath('//h1[@class="arti_title"]/text()')
                elif url_text.xpath('//p[@class="arti_title"]/text()'):
                    title = url_text.xpath('//p[@class="arti_title"]/text()')
                if title:
                    title = title[0].strip()
                    content = url_text.xpath('//div[@class="wp_articlecontent"]//text()')
                    filename = title.replace('/', '').replace('\\', '').replace(':', '').replace('*', '').replace('?',
                                                                                                                  '').replace(
                        '"', '').replace('<', '').replace('>', '').replace('|', '')

                    with open(f"{dir_path}/{filename}.txt", 'w', encoding='utf-8') as f:
                        f.write(title + '\n')
                        for line in content:
                            f.write(line.strip() + '\n')
                    print(f'Article "{title}" downloaded successfully.')
    except Exception as e:
        print(f"Error during downloading articles: {e}")


def process_organization(big_institution_name, organization_name, organization_url):
    set_small_title_name = find_small_title_name(organization_url)
    set_small_title_url = find_small_title_url(organization_url)
    set_small_title_url = deal_small_title_url(set_small_title_url)

    for a, b in zip(set_small_title_name, set_small_title_url):
        download_articles(big_institution_name, organization_name, a, organization_url, b)


if __name__ == '__main__':
    big_institution_name, government_organization_name, educational_organization_name, scientific_institution_name = find_institution_name()
    government_organization_url, educational_organization_url, scientific_institution_url = find_institution_url()
    #print(educational_organization_name)
    #print(educational_organization_url)
    with ProcessPoolExecutor() as executor:
        futures = []
        #Download government organizations
    
        # Download educational organizations
        organization_name = educational_organization_name[5]
        organization_url = educational_organization_url[5]
        organization_url = organization_url.replace('main.htm','')
        futures.append(
            executor.submit(process_organization, big_institution_name[1], organization_name, organization_url))

        # Download scientific institutions
        
        # Wait for all futures to complete
        for future in as_completed(futures):
            future.result()  # This will raise exceptions if any occurred
