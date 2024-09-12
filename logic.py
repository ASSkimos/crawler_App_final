import aiohttp
import asyncio
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import urllib.robotparser
import tkinter as tk
import re

visited_urls = set()


async def fetch(session, url):
    try:
        async with session.get(url) as response:
            response.raise_for_status()  # Проверка на ошибки HTTP
            return await response.text()
    except aiohttp.ClientError as e:
        return None


def check_robots_txt(url, user_agent='*'):
    parsed_url = urlparse(url)
    robots_url = urljoin(f"{parsed_url.scheme}://{parsed_url.netloc}", '/robots.txt')
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_url)
    rp.read()
    return rp.can_fetch(user_agent, url)


async def save_page(directory, url, content):
    # Очищаем URL от недопустимых символов для имени файла
    filename = re.sub(r'[^a-zA-Z0-9_\-]', '_',
                      url.replace('http://', '').replace('https://', '').replace('/', '_')) + '.html'

    # Формируем полный путь к файлу
    filepath = os.path.join(directory, filename)

    # Открываем файл в режиме записи (если файл существует, он будет перезаписан)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


def is_valid_url(url):
    disallowed_extensions = ['.jpg', '.png', '.gif', '.css', '.js']
    return not any(url.endswith(ext) for ext in disallowed_extensions)


async def crawl(session, url, depth, base_domain, output, directory):
    if depth == 0 or url in visited_urls or not is_valid_url(url):
        return

    visited_urls.add(url)  # Добавляем текущий URL в множество посещенных
    html_content = await fetch(session, url)

    if html_content is None:
        return

    await save_page(directory, url, html_content)  # Сохранение контента страницы
    output.insert(tk.END, f"Глубина {depth}: {url}\n")
    output.see(tk.END)

    soup = BeautifulSoup(html_content, 'html.parser')
    links = soup.find_all('a', href=True)
    tasks = []

    for link in links:
        full_url = urljoin(url, link['href'])
        parsed_link = urlparse(full_url)

        if parsed_link.netloc == base_domain and full_url not in visited_urls:
            tasks.append(crawl(session, full_url, depth - 1, base_domain, output, directory))

    if tasks:
        await asyncio.gather(*tasks)  # Асинхронно ждем выполнения всех задач


async def main(start_url, max_depth, output, directory):
    parsed_start_url = urlparse(start_url)
    base_domain = parsed_start_url.netloc

    can_crawl = check_robots_txt(start_url)
    if not can_crawl:
        output.insert(tk.END, f"Сайт {base_domain} запрещает краулинг в robots.txt\n")
        return

    async with aiohttp.ClientSession() as session:
        await crawl(session, start_url, max_depth, base_domain, output, directory)
        output.insert(tk.END, "Краулинг завершен!\n")
