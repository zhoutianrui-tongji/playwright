# Author: Tianrui Zhou
# Emial: skychou@tongji.edu.cn
# Date: 2023/12/21 
# Project: Download_Crost.py
# Description: Brief description of the project

import os
import pickle
import time

from playwright.sync_api import sync_playwright
from playwright.sync_api._generated import Browser, Page, Playwright
from playwright_stealth import stealth_sync  # type: ignore[import]
from tqdm import tqdm

start_time = time.time()
## 参数设置
target_path = '/Users/skychou/Downloads'  # 下载路径
pkl_file = "crost_data.pkl"  # 数据表格文件
errors_pkl = "./errors.pkl"  # 下载失败的文件


def initialise_playwright_browsercontroller(
        start_url: str,
        browsertype: str,
        headless: bool,
        stealthmode: bool,
) -> tuple[Playwright, Page]:
    """
    Creates a Playwright browser, opens a new page, and navigates to a
    specified URL.

    Important, call playwright.stop() once you are done.

    Returns:
        tuple[Browser, Page]: A tuple containing the browser and page objects.
    """

    playwright: Playwright = sync_playwright().start()
    if browsertype == "firefox":
        browser: Browser = playwright.firefox.launch(headless=headless)
    if browsertype == "chromium":
        browser: Browser = playwright.chromium.launch(headless=headless)
    if browsertype == "safari":
        raise NotImplementedError("Error, did not implement webkit launch.")

    page: Page = browser.new_page()

    if stealthmode:
        stealth_sync(page)

    js = """
    Object.defineProperties(navigator, {webdriver:{get:()=>undefined}});
    """
    page.add_init_script(js)
    page.goto(start_url)
    return playwright, page


try:
    playwright, page = initialise_playwright_browsercontroller(
        start_url="https://ngdc.cncb.ac.cn/crost/download",
        browsertype="chromium",
        headless=True,
        stealthmode=True,
    )

    page.locator(".v-field__append-inner > .mdi-menu-down").first.click()
    page.get_by_text("All", exact=True).click()
    page.wait_for_selector("thead")  # 等待表头加载，确保表格已经渲染

    if not os.path.exists(pkl_file):
        # rows = page.query_selector_all(
        #         "#app > div > div > main > div > div > div:nth-child(2) > div.v-table.v-table--fixed-header.v-table--has-bottom.v-theme--light.v-table--density-compact.v-data-table.data-table-style.mt-2 > div.v-table__wrapper > table > tbody > tr")
        ##获得表格内容和表头（list）
        table_selector = "#app > div > div > main > div > div > div:nth-child(2) > div.v-table.v-table--fixed-header.v-table--has-bottom.v-theme--light.v-table--density-compact.v-data-table.data-table-style.mt-2 > div.v-table__wrapper > table"
        table = page.query_selector(table_selector)
        table_text = table.inner_text()
        data_list = table_text.split('\n')
        split_index = data_list.index("")
        table_header = data_list[:split_index]
        table_header = [i for i in table_header if i != "\t"]
        table_content = data_list[split_index + 1:]
        print("table---success！\n")
        # 创建一个空列表，用于存储四元组
        res_list = []
        for i in range(0, len(table_content)):
            temp = table_content[i].split()
            res_list.append((temp[0], temp[1], temp[-3], temp[-2]))

        tempres = []
        for i in res_list:
            if i[0] not in tempres:
                tempres.append(i[0])

        with open(pkl_file, 'wb') as file:
            pickle.dump(res_list, file)
        print(f"数据已保存到 {pkl_file}")

    else:
        with open(pkl_file, 'rb') as file:
            res_list = pickle.load(file)
        print(f"数据已加载 {pkl_file}")

    # 测试
    # res_list = res_list[0:10]

    errors = []

    for tp in tqdm(res_list, desc="处理进度", unit="files"):
        try:
            # table_html = table.inner_html()
            # soup = BeautifulSoup(table_html, 'html.parser')
            if not os.path.exists(os.path.join(target_path, tp[0])):
                os.makedirs(os.path.join(target_path, tp[0]))

            with page.expect_download() as download_info:
                page.get_by_text(tp[2]).click()

            download = download_info.value
            # 等待下载完成
            path = download.path()
            print(f'Suggested filename: {download.suggested_filename}')
            # 等待下载文件可用
            print(f'Download path: {path}')
            # 将下载的文件重命名为建议的文件名
            os.rename(path, os.path.join(target_path, download.suggested_filename))
            print(f"文件已保存到: {target_path}")
        except Exception as e:
            errors.append(tp)
            continue

    if errors:
        with open(errors_pkl, 'wb') as file:
            pickle.dump(errors, file)
        print(f"未成功数据已保存到 {errors_pkl}")

finally:
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"运行时间：{elapsed_time} 秒")
    playwright.stop()
