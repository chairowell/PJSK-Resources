#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
B站UP主内容批量下载器
功能：批量下载B站UP主的专栏文章和空间图文，支持筛选特定标题/内容的内容，支持下载并保存图片
作者：Auto-Generated
时间：2024
"""

import requests
import json
import os
import re
import time
import argparse
from urllib.parse import urlparse, parse_qs, urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed

class BilibiliArticleDownloader:
    def __init__(self, cookies=None, output_dir="./output", max_workers=5, disable_image_download=False):
        """初始化下载器
        
        Args:
            cookies: cookies字符串或字典，用于API认证
            output_dir: 输出目录
            max_workers: 最大线程数
            disable_image_download: 是否禁用图片下载，默认为False
        """
        self.session = requests.Session()
        self.output_dir = output_dir
        self.max_workers = max_workers
        self.disable_image_download = disable_image_download
        
        # 设置请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://www.bilibili.com/'
        }
        
        # 设置cookies
        if cookies:
            if isinstance(cookies, str):
                self.session.headers['Cookie'] = cookies
            elif isinstance(cookies, dict):
                self.session.cookies.update(cookies)
        
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
        
        # API接口
        self.api_urls = {
            # 获取UP主专栏列表
            'article_list': 'https://api.bilibili.com/x/space/article',
            # 获取文章详情
            'article_detail': 'https://api.bilibili.com/x/article/view',
            # 获取用户空间图文
            'opus_feed': 'https://api.bilibili.com/x/polymer/web-dynamic/v1/opus/feed/space'
        }
    
    def get_article_list(self, mid, keyword=None):
        """获取UP主的文章列表
        
        Args:
            mid: UP主的用户ID
            keyword: 筛选关键词，可选
        
        Returns:
            list: 文章列表
        """
        articles = []
        page = 1
        has_more = True
        
        print(f"正在获取UP主(mid={mid})的文章列表...")
        
        while has_more:
            params = {
                'mid': mid,
                'pn': page,
                'ps': 30,  # 每页30条
                'sort': 'pubdate'
            }
            
            try:
                response = self.session.get(self.api_urls['article_list'], 
                                           headers=self.headers, 
                                           params=params)
                response.raise_for_status()
                data = response.json()
                
                if data.get('code') != 0:
                    print(f"获取第{page}页文章列表失败: {data.get('message', '未知错误')}")
                    break
                
                page_data = data.get('data', {})
                articles.extend(page_data.get('articles', []))
                
                # 检查是否还有更多页
                has_more = page_data.get('has_more', False)
                total = page_data.get('total', 0)
                
                print(f"已获取第{page}页，共{len(articles)}/{total}篇文章")
                
                page += 1
                # 避免请求过于频繁
                time.sleep(1)
                
            except Exception as e:
                print(f"获取文章列表时出错: {str(e)}")
                break
        
        # 筛选含有特定关键词的文章
        if keyword:
            filtered_articles = [article for article in articles 
                                if keyword.lower() in article.get('title', '').lower()]
            print(f"筛选后共{len(filtered_articles)}篇文章含有关键词'{keyword}'")
            return filtered_articles
        
        return articles
        
    def get_opus_list(self, mid, keyword=None, opus_type='all'):
        """获取UP主的空间图文列表
        
        Args:
            mid: UP主的用户ID
            keyword: 筛选关键词，可选
            opus_type: 内容类型，可选值：all(全部)、article(专栏)、dynamic(动态)
        
        Returns:
            list: 图文列表
        """
        opuses = []
        has_more = True
        offset = ''
        page = 1
        
        print(f"正在获取UP主(mid={mid})的空间图文列表...")
        
        while has_more:
            params = {
                'host_mid': mid,
                'offset': offset,
                'type': opus_type,
                'web_location': '333.1387'
            }
            
            try:
                response = self.session.get(self.api_urls['opus_feed'], 
                                           headers=self.headers, 
                                           params=params)
                response.raise_for_status()
                data = response.json()
                
                if data.get('code') != 0:
                    print(f"获取第{page}页图文列表失败: {data.get('message', '未知错误')}")
                    break
                
                page_data = data.get('data', {})
                items = page_data.get('items', [])
                opuses.extend(items)
                
                # 检查是否还有更多页
                has_more = page_data.get('has_more', False)
                offset = page_data.get('offset', '')
                
                print(f"已获取第{page}页，共{len(opuses)}条图文")
                
                page += 1
                # 避免请求过于频繁
                time.sleep(1)
                
                # 如果没有更多偏移量，停止请求
                if not offset:
                    break
                    
            except Exception as e:
                print(f"获取图文列表时出错: {str(e)}")
                break
        
        # 筛选含有特定关键词的图文
        if keyword:
            filtered_opuses = [opus for opus in opuses 
                              if keyword.lower() in opus.get('content', '').lower()]
            print(f"筛选后共{len(filtered_opuses)}条图文含有关键词'{keyword}'")
            return filtered_opuses
        
        return opuses
    
    def get_article_detail(self, article_id):
        """获取文章详情
        
        Args:
            article_id: 文章ID
        
        Returns:
            dict: 文章详情
        """
        try:
            params = {'id': article_id}
            response = self.session.get(self.api_urls['article_detail'], 
                                       headers=self.headers, 
                                       params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('code') != 0:
                print(f"获取文章{article_id}详情失败: {data.get('message', '未知错误')}")
                return None
            
            return data.get('data', {})
            
        except Exception as e:
            print(f"获取文章{article_id}详情时出错: {str(e)}")
            return None
            
    def download_image(self, image_url, save_dir, base_filename, index):
        """下载图片并保存到本地
        
        Args:
            image_url: 图片URL
            save_dir: 保存目录
            base_filename: 基础文件名（不含扩展名）
            index: 图片索引，用于多图时的顺序后缀
        
        Returns:
            str: 保存的图片文件名，如果下载失败则返回None
        """
        try:
            # 获取图片扩展名
            parsed_url = urlparse(image_url)
            path = parsed_url.path
            _, ext = os.path.splitext(path)
            if not ext:
                ext = '.jpg'  # 默认使用jpg扩展名
            
            # 构建保存的文件名
            if index > 0:
                image_filename = f"{base_filename}_{index}{ext}"
            else:
                image_filename = f"{base_filename}{ext}"
            
            # 构建完整的保存路径
            save_path = os.path.join(save_dir, image_filename)
            
            # 下载图片
            response = self.session.get(image_url, stream=True)
            response.raise_for_status()
            
            # 保存图片
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"已下载图片: {image_filename}")
            return image_filename
            
        except Exception as e:
            print(f"下载图片{image_url}时出错: {str(e)}")
            return None
            
    def get_opus_detail(self, opus):
        """处理单个空间图文数据
        
        Args:
            opus: 图文数据对象
        
        Returns:
            dict: 格式化的图文详情
        """
        try:
            # 提取图文信息
            content = opus.get('content', '无内容')
            opus_id = opus.get('opus_id', 'unknown')
            jump_url = opus.get('jump_url', '')
            
            # 提取统计信息
            stat = opus.get('stat', {})
            like_count = stat.get('like', '0')
            view_count = stat.get('view', '0')
            
            # 提取封面信息
            cover = opus.get('cover', {})
            cover_url = cover.get('url', '') if cover else ''
            
            # 格式化图文详情
            detail = {
                'title': f"图文动态_{opus_id}",
                'content': content,
                'opus_id': opus_id,
                'jump_url': jump_url,
                'like_count': like_count,
                'view_count': view_count,
                'cover_url': cover_url
            }
            
            return detail
            
        except Exception as e:
            print(f"处理图文{opus.get('opus_id', 'unknown')}时出错: {str(e)}")
            return None
    
    def save_article(self, article_detail):
        """保存文章到本地，并下载所有图片
        
        Args:
            article_detail: 文章详情
        
        Returns:
            str: 保存的文件路径
        """
        if not article_detail:
            return None
        
        try:
            # 获取文章标题和内容
            title = article_detail.get('title', '未知标题')
            content = article_detail.get('content', '')
            author_name = article_detail.get('author_name', '未知作者')
            
            # 清理标题中的特殊字符
            safe_title = re.sub(r'[\\/:*?"<>|]', '_', title)
            
            # 创建作者目录
            author_dir = os.path.join(self.output_dir, author_name, 'articles')
            os.makedirs(author_dir, exist_ok=True)
            
            # 保存为HTML文件
            file_path = os.path.join(author_dir, f"{safe_title}.html")
            
            # 提取并下载图片
            # 基础文件名（不含扩展名）
            base_filename = safe_title
            
            # 提取所有图片URL
            image_urls = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', content)
            
            # 下载图片并更新内容中的图片引用（如果不禁用图片下载）
            if image_urls and not self.disable_image_download:
                print(f"开始下载文章《{title}》中的{len(image_urls)}张图片...")
                
                # 用于保存下载的图片文件名
                local_image_filenames = []
                
                # 下载每张图片
                for i, image_url in enumerate(image_urls):
                    # 确保URL是完整的
                    if not image_url.startswith(('http://', 'https://')):
                        # 如果是相对URL，尝试构建完整URL
                        image_url = urljoin('https://www.bilibili.com', image_url)
                    
                    # 下载图片
                    local_filename = self.download_image(image_url, author_dir, base_filename, i)
                    if local_filename:
                        local_image_filenames.append(local_filename)
                        # 更新内容中的图片引用
                        content = content.replace(image_url, local_filename)
                
                print(f"图片下载完成，共成功下载{len(local_image_filenames)}张图片")
            elif self.disable_image_download:
                print(f"已禁用图片下载功能，将保留原始图片链接")
            
            # 构建完整的HTML内容
            html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ font-family: 'Microsoft YaHei', sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #333; }}
        .article-info {{ color: #666; margin-bottom: 20px; }}
        .article-content {{ line-height: 1.6; }}
        .article-content img {{ max-width: 100%; height: auto; margin: 10px 0; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <div class="article-info">作者: {author_name}</div>
    <div class="article-content">
        {content}
    </div>
</body>
</html>"""
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"已保存文章: {title}")
            return file_path
            
        except Exception as e:
            print(f"保存文章{title}时出错: {str(e)}")
            return None
    
    def save_opus(self, opus_detail, author_name='未知作者'):
        """保存空间图文到本地，并下载所有图片
        
        Args:
            opus_detail: 图文详情
            author_name: 作者名称
        
        Returns:
            str: 保存的文件路径
        """
        if not opus_detail:
            return None
        
        try:
            # 获取图文信息
            title = opus_detail.get('title', '未知标题')
            content = opus_detail.get('content', '')
            opus_id = opus_detail.get('opus_id', 'unknown')
            cover_url = opus_detail.get('cover_url', '')
            like_count = opus_detail.get('like_count', '0')
            
            # 清理标题中的特殊字符
            safe_title = re.sub(r'[\\/:*?"<>|]', '_', title)
            
            # 创建作者目录
            author_dir = os.path.join(self.output_dir, author_name, 'opuses')
            os.makedirs(author_dir, exist_ok=True)
            
            # 保存为HTML文件
            file_path = os.path.join(author_dir, f"{safe_title}.html")
            
            # 基础文件名（不含扩展名）
            base_filename = safe_title
            
            # 提取并下载所有图片
            image_urls = []
            
            # 添加封面图片（如果有）
            if cover_url:
                image_urls.append(cover_url)
            
            # 提取内容中的图片URL
            content_image_urls = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', content)
            image_urls.extend(content_image_urls)
            
            # 下载图片并更新引用（如果不禁用图片下载）
            if image_urls and not self.disable_image_download:
                print(f"开始下载图文《{title}》中的{len(image_urls)}张图片...")
                
                # 用于保存下载的图片文件名
                local_image_filenames = []
                
                # 下载每张图片
                for i, image_url in enumerate(image_urls):
                    # 确保URL是完整的
                    if not image_url.startswith(('http://', 'https://')):
                        # 如果是相对URL，尝试构建完整URL
                        image_url = urljoin('https://www.bilibili.com', image_url)
                    
                    # 下载图片
                    local_filename = self.download_image(image_url, author_dir, base_filename, i)
                    if local_filename:
                        local_image_filenames.append(local_filename)
                        # 更新引用
                        if i == 0 and cover_url == image_url:
                            # 更新封面图片引用
                            cover_url = local_filename
                        else:
                            # 更新内容中的图片引用
                            content = content.replace(image_url, local_filename)
                
                print(f"图片下载完成，共成功下载{len(local_image_filenames)}张图片")
            elif self.disable_image_download:
                print(f"已禁用图片下载功能，将保留原始图片链接")
            
            # 构建封面HTML（如果有封面）
            cover_html = f'<img src="{cover_url}" style="max-width: 100%; margin: 10px 0;" />' if cover_url else ''
            
            # 构建完整的HTML内容
            html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ font-family: 'Microsoft YaHei', sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #333; }}
        .opus-info {{ color: #666; margin-bottom: 20px; }}
        .opus-content {{ line-height: 1.6; white-space: pre-wrap; }}
        img {{ max-width: 100%; height: auto; margin: 10px 0; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <div class="opus-info">作者: {author_name} | 点赞数: {like_count}</div>
    {cover_html}
    <div class="opus-content">
        {content}
    </div>
</body>
</html>"""
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"已保存图文: {title}")
            return file_path
            
        except Exception as e:
            print(f"保存图文{title}时出错: {str(e)}")
            return None
            
    def download_articles(self, mid, keyword=None):
        """批量下载文章
        
        Args:
            mid: UP主的用户ID
            keyword: 筛选关键词，可选
        
        Returns:
            list: 成功下载的文件路径列表
        """
        # 获取文章列表
        articles = self.get_article_list(mid, keyword)
        
        if not articles:
            print("未找到符合条件的文章")
            return []
        
        downloaded_files = []
        
        print(f"开始下载{len(articles)}篇文章...")
        
        # 使用线程池并发下载
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_article = {
                executor.submit(self.get_article_detail, article.get('id')): article 
                for article in articles
            }
            
            # 处理完成的任务
            for future in as_completed(future_to_article):
                article = future_to_article[future]
                try:
                    article_detail = future.result()
                    if article_detail:
                        file_path = self.save_article(article_detail)
                        if file_path:
                            downloaded_files.append(file_path)
                except Exception as e:
                    print(f"处理文章{article.get('title', '未知')}时出错: {str(e)}")
        
        print(f"下载完成，共成功下载{len(downloaded_files)}篇文章")
        return downloaded_files
        
    def download_opuses(self, mid, keyword=None, opus_type='all'):
        """批量下载空间图文
        
        Args:
            mid: UP主的用户ID
            keyword: 筛选关键词，可选
            opus_type: 内容类型，可选值：all(全部)、article(专栏)、dynamic(动态)
        
        Returns:
            list: 成功下载的文件路径列表
        """
        # 获取图文列表
        opuses = self.get_opus_list(mid, keyword, opus_type)
        
        if not opuses:
            print("未找到符合条件的图文")
            return []
        
        downloaded_files = []
        
        print(f"开始处理{len(opuses)}条图文...")
        
        # 使用线程池并发处理
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_opus = {
                executor.submit(self.get_opus_detail, opus): opus 
                for opus in opuses
            }
            
            # 处理完成的任务
            for future in as_completed(future_to_opus):
                opus = future_to_opus[future]
                try:
                    opus_detail = future.result()
                    if opus_detail:
                        # 对于空间图文，我们没有直接的作者名称，使用mid作为标识
                        file_path = self.save_opus(opus_detail, author_name=f"UP主_{mid}")
                        if file_path:
                            downloaded_files.append(file_path)
                except Exception as e:
                    opus_id = opus.get('opus_id', 'unknown')
                    print(f"处理图文{opus_id}时出错: {str(e)}")
        
        print(f"处理完成，共成功保存{len(downloaded_files)}条图文")
        return downloaded_files
        
    def download_all(self, mid, keyword=None, include_articles=True, include_opuses=True, opus_type='all'):
        """批量下载UP主的所有内容（文章和图文）
        
        Args:
            mid: UP主的用户ID
            keyword: 筛选关键词，可选
            include_articles: 是否包含专栏文章
            include_opuses: 是否包含空间图文
            opus_type: 图文类型，可选值：all(全部)、article(专栏)、dynamic(动态)
        
        Returns:
            list: 成功下载的文件路径列表
        """
        all_downloaded_files = []
        
        # 下载专栏文章
        if include_articles:
            article_files = self.download_articles(mid, keyword)
            all_downloaded_files.extend(article_files)
            
        # 下载空间图文
        if include_opuses:
            opus_files = self.download_opuses(mid, keyword, opus_type)
            all_downloaded_files.extend(opus_files)
            
        print(f"所有内容下载完成，共成功下载{len(all_downloaded_files)}个文件")
        return all_downloaded_files
    
    def get_mid_from_url(self, url):
        """从UP主空间URL中提取mid
        
        Args:
            url: UP主空间URL
        
        Returns:
            str: mid
        """
        parsed_url = urlparse(url)
        if 'space.bilibili.com' in parsed_url.netloc:
            # 从URL路径中提取mid
            path_parts = parsed_url.path.strip('/').split('/')
            if path_parts and path_parts[0].isdigit():
                return path_parts[0]
            
            # 尝试从查询参数中提取
            query_params = parse_qs(parsed_url.query)
            if 'mid' in query_params:
                return query_params['mid'][0]
        
        return None

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='B站UP主内容批量下载器')
    parser.add_argument('--mid', type=str, help='UP主的mid')
    parser.add_argument('--url', type=str, help='UP主空间URL')
    parser.add_argument('--keyword', type=str, help='筛选关键词')
    parser.add_argument('--cookies', type=str, help='Cookies字符串')
    parser.add_argument('--output', type=str, default='./output', help='输出目录')
    parser.add_argument('--threads', type=int, default=5, help='线程数')
    parser.add_argument('--type', type=str, default='all', choices=['articles', 'opuses', 'all'],
                        help='下载类型: articles(仅文章), opuses(仅图文), all(全部)')
    parser.add_argument('--opus-type', type=str, default='all', choices=['all', 'article', 'dynamic'],
                        help='图文类型: all(全部), article(专栏), dynamic(动态)')
    parser.add_argument('--no-images', action='store_true', help='禁用图片下载，保留原始图片链接')
    
    args = parser.parse_args()
    
    # 获取mid
    mid = args.mid
    if args.url:
        downloader = BilibiliArticleDownloader()
        mid_from_url = downloader.get_mid_from_url(args.url)
        if mid_from_url:
            mid = mid_from_url
        else:
            print("无法从URL中提取mid")
            return
    
    if not mid:
        print("请提供UP主的mid或URL")
        parser.print_help()
        return
    
    # 创建下载器实例
    downloader = BilibiliArticleDownloader(
        cookies=args.cookies,
        output_dir=args.output,
        max_workers=args.threads,
        disable_image_download=args.no_images
    )
    
    # 根据下载类型执行不同的下载方法
    if args.type == 'articles':
        # 仅下载专栏文章
        downloader.download_articles(mid, args.keyword)
    elif args.type == 'opuses':
        # 仅下载空间图文
        downloader.download_opuses(mid, args.keyword, args.opus_type)
    else:
        # 下载所有内容
        downloader.download_all(mid, args.keyword, include_articles=True, 
                               include_opuses=True, opus_type=args.opus_type)

if __name__ == '__main__':
    main()