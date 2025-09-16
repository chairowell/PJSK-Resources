#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量下载世界计划彩色舞台漫画图片
功能：批量下载 https://storage.sekai.best/sekai-cn-assets/comic/one_frame/comic_00${mangaId}.png 格式的图片，其中mangaId从1到68
"""

import os
import requests
import argparse
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

class SekaiComicDownloader:
    def __init__(self, output_dir="./images", max_workers=5, start_id=1, end_id=68):
        """初始化下载器
        
        Args:
            output_dir: 图片保存目录
            max_workers: 最大线程数
            start_id: 起始漫画ID
            end_id: 结束漫画ID
        """
        self.output_dir = output_dir
        self.max_workers = max_workers
        self.start_id = start_id
        self.end_id = end_id
        self.session = requests.Session()
        
        # 设置请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
        }
        
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
    
    def get_image_url(self, manga_id):
        """根据漫画ID生成图片URL
        
        Args:
            manga_id: 漫画ID
            
        Returns:
            str: 完整的图片URL
        """
        # 格式化ID为3位数字，前面补0
        formatted_id = f"{manga_id:03d}"
        return f"https://storage.sekai.best/sekai-cn-assets/comic/one_frame/comic_0{formatted_id}.png"
    
    def get_save_path(self, manga_id):
        """根据漫画ID生成保存路径
        
        Args:
            manga_id: 漫画ID
            
        Returns:
            str: 完整的保存路径
        """
        # 格式化ID为4位数字，前面补0
        formatted_id = f"{manga_id:04d}"
        filename = f"{formatted_id}.png"
        return os.path.join(self.output_dir, filename)
    
    def download_image(self, manga_id):
        """下载单个图片
        
        Args:
            manga_id: 漫画ID
            
        Returns:
            tuple: (是否成功, 漫画ID)
        """
        try:
            url = self.get_image_url(manga_id)
            save_path = self.get_save_path(manga_id)
            
            # 检查文件是否已存在
            if os.path.exists(save_path):
                print(f"文件已存在，跳过下载: {save_path}")
                return True, manga_id
            
            response = self.session.get(url, headers=self.headers, stream=True, timeout=30)
            response.raise_for_status()
            
            # 检查响应是否为图片
            content_type = response.headers.get('Content-Type', '')
            if not content_type.startswith('image/'):
                print(f"警告: {url} 不是有效图片")
                return False, manga_id
            
            # 保存图片
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # 过滤掉保持连接的空块
                        f.write(chunk)
            
            print(f"已下载图片: {os.path.basename(save_path)} (ID: {manga_id})")
            return True, manga_id
            
        except Exception as e:
            print(f"下载图片(ID: {manga_id})时出错: {str(e)}")
            return False, manga_id
    
    def download_all_images(self):
        """批量下载所有图片
        
        Returns:
            int: 成功下载的图片数量
        """
        print(f"开始下载漫画图片，范围：{self.start_id} 到 {self.end_id}")
        print(f"保存目录：{self.output_dir}")
        print(f"使用线程数：{self.max_workers}")
        
        # 使用线程池并行下载
        success_count = 0
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_id = {
                executor.submit(self.download_image, manga_id): manga_id
                for manga_id in range(self.start_id, self.end_id + 1)
            }
            
            # 处理完成的任务
            for future in as_completed(future_to_id):
                manga_id = future_to_id[future]
                try:
                    success, _ = future.result()
                    if success:
                        success_count += 1
                except Exception as e:
                    print(f"处理图片(ID: {manga_id})时发生异常: {str(e)}")
            
        print(f"所有图片下载任务已完成，共成功下载{success_count}张图片")
        return success_count

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='批量下载世界计划彩色舞台漫画图片')
    parser.add_argument('--output-dir', type=str, 
                        default=r'c:\Users\Administrator\Desktop\Project\pjsk-manga\images',
                        help='图片保存目录')
    parser.add_argument('--threads', type=int, default=5, help='线程数')
    parser.add_argument('--start-id', type=int, default=1, help='起始漫画ID')
    parser.add_argument('--end-id', type=int, default=68, help='结束漫画ID')
    
    args = parser.parse_args()
    
    # 创建下载器实例
    downloader = SekaiComicDownloader(
        output_dir=args.output_dir,
        max_workers=args.threads,
        start_id=args.start_id,
        end_id=args.end_id
    )
    
    # 开始下载
    start_time = time.time()
    success_count = downloader.download_all_images()
    end_time = time.time()
    
    print(f"总耗时: {end_time - start_time:.2f}秒")
    print(f"最终成功下载{success_count}张图片")

if __name__ == '__main__':
    main()