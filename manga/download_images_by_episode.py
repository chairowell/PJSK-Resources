#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从HTML文件中提取图片并按话数重命名下载
功能：遍历指定目录中的HTML文件，提取图片URL和文章话数，下载图片并重命名为0xxx.png格式
"""

import os
import re
import requests
from bs4 import BeautifulSoup
import argparse
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

class ImageDownloaderByEpisode:
    def __init__(self, input_dir, output_dir=None, max_workers=5):
        """初始化下载器
        
        Args:
            input_dir: 包含HTML文件的输入目录
            output_dir: 图片保存目录，如果为None则在input_dir下创建images子目录
            max_workers: 最大线程数
        """
        self.input_dir = input_dir
        # 如果未指定输出目录，则在输入目录下创建images子目录
        self.output_dir = output_dir if output_dir else os.path.join(input_dir, 'images')
        self.max_workers = max_workers
        self.session = requests.Session()
        
        # 设置请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Referer': 'https://www.bilibili.com/'
        }
        
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 用于记录已处理的话数，避免重复下载
        self.processed_episodes = set()
    
    def extract_episode_number(self, content):
        """从HTML内容中提取话数（如第235话）
        
        Args:
            content: HTML内容字符串
            
        Returns:
            str: 格式化的话数字符串（如0235），如果未找到则返回None
        """
        # 匹配中文数字+"话"的模式，例如"第235话"、"第12话"等
        match = re.search(r'第(\d+)话', content)
        if match:
            # 提取数字部分并格式化为4位数字，前面补0
            episode_num = match.group(1)
            return episode_num.zfill(4)
        return None
    
    def extract_image_urls(self, html_content):
        """从HTML内容中提取所有图片URL
        
        Args:
            html_content: HTML内容字符串
            
        Returns:
            list: 图片URL列表
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        img_tags = soup.find_all('img')
        image_urls = [img.get('src') for img in img_tags if img.get('src')]
        return image_urls
    
    def download_image(self, image_url, save_path):
        """下载图片并保存到指定路径
        
        Args:
            image_url: 图片URL
            save_path: 保存路径
            
        Returns:
            bool: 下载是否成功
        """
        try:
            # 如果URL不完整，补充协议
            if not image_url.startswith(('http://', 'https://')):
                image_url = 'https://' + image_url
                
            response = self.session.get(image_url, headers=self.headers, stream=True, timeout=30)
            response.raise_for_status()
            
            # 检查响应是否为图片
            content_type = response.headers.get('Content-Type', '')
            if not content_type.startswith('image/'):
                print(f"警告: {image_url} 不是有效图片")
                return False
            
            # 保存图片
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # 过滤掉保持连接的空块
                        f.write(chunk)
            
            print(f"已下载图片: {os.path.basename(save_path)}")
            return True
            
        except Exception as e:
            print(f"下载图片{image_url}时出错: {str(e)}")
            return False
    
    def process_html_file(self, html_file):
        """处理单个HTML文件
        
        Args:
            html_file: HTML文件路径
            
        Returns:
            tuple: (是否成功, 处理的话数)
        """
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 提取话数
            episode_num = self.extract_episode_number(content)
            if not episode_num:
                print(f"警告: 在文件{html_file}中未找到话数信息")
                return False, None
            
            # 检查是否已经处理过这个话数
            if episode_num in self.processed_episodes:
                print(f"警告: 话数{episode_num}已经处理过，跳过重复下载")
                return False, episode_num
            
            # 提取图片URL
            image_urls = self.extract_image_urls(content)
            if not image_urls:
                print(f"警告: 在文件{html_file}中未找到图片")
                return False, episode_num
            
            # 构建保存路径（只下载第一张图片，因为需求中似乎每个HTML文件对应一个图片）
            image_url = image_urls[0]
            save_filename = f"{episode_num}.png"
            save_path = os.path.join(self.output_dir, save_filename)
            
            # 下载图片
            success = self.download_image(image_url, save_path)
            if success:
                self.processed_episodes.add(episode_num)
                return True, episode_num
            
            return False, episode_num
            
        except Exception as e:
            print(f"处理文件{html_file}时出错: {str(e)}")
            return False, None
    
    def download_all_images(self):
        """批量处理所有HTML文件并下载图片
        
        Returns:
            int: 成功下载的图片数量
        """
        # 获取输入目录中的所有HTML文件
        html_files = []
        for filename in os.listdir(self.input_dir):
            if filename.endswith('.html'):
                html_files.append(os.path.join(self.input_dir, filename))
        
        print(f"找到{len(html_files)}个HTML文件需要处理")
        
        # 使用线程池并行处理
        success_count = 0
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_file = {
                executor.submit(self.process_html_file, html_file): html_file
                for html_file in html_files
            }
            
            # 处理完成的任务
            for future in as_completed(future_to_file):
                html_file = future_to_file[future]
                try:
                    success, episode_num = future.result()
                    if success:
                        success_count += 1
                except Exception as e:
                    print(f"处理文件{html_file}时发生异常: {str(e)}")
            
        print(f"所有图片下载任务已完成，共成功下载{success_count}张图片")
        return success_count

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='从HTML文件中提取图片并按话数重命名下载')
    parser.add_argument('--input-dir', type=str, 
                        default=r'c:\Users\Administrator\Desktop\Project\pjsk-4koman\output\UP主_13148307\opuses',
                        help='包含HTML文件的输入目录')
    parser.add_argument('--output-dir', type=str, help='图片保存目录，默认在输入目录下创建images子目录')
    parser.add_argument('--threads', type=int, default=5, help='线程数')
    
    args = parser.parse_args()
    
    # 创建下载器实例
    downloader = ImageDownloaderByEpisode(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        max_workers=args.threads
    )
    
    # 开始下载
    start_time = time.time()
    success_count = downloader.download_all_images()
    end_time = time.time()
    
    print(f"总耗时: {end_time - start_time:.2f}秒")
    print(f"最终成功下载{success_count}张图片")

if __name__ == '__main__':
    main()