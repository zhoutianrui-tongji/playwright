# Author: Tianrui Zhou
# Emial: skychou@tongji.edu.cn
# Date: 2023/12/13 
# Project: TJ_PJ.py
# Description: 1.Tj jiaoxuepingjia

from playwright.sync_api import sync_playwright

def do(page):
    page.locator("label:nth-child(2)").first.click()
    page.locator("div:nth-child(2) > .question-row > .el-radio-group > label:nth-child(2)").click()
    page.locator("div:nth-child(3) > .question-row > .el-radio-group > label:nth-child(2)").click()
    page.locator("div:nth-child(4) > .question-row > .el-radio-group > label:nth-child(2)").click()
    page.locator("div:nth-child(5) > .question-row > .el-radio-group > label:nth-child(2)").click()
    page.locator("div:nth-child(6) > .question-row > .el-radio-group > label:nth-child(2)").click()
    page.locator("div:nth-child(7) > .question-row > .el-radio-group > label:nth-child(2)").click()
    page.locator("div:nth-child(8) > .question-row > .el-radio-group > label:nth-child(2)").click()
    page.get_by_role("radio", name="B.明确 Good").click()
    page.locator("div:nth-child(10) > .question-row > .el-radio-group > label:nth-child(2)").click()
    page.get_by_role("button", name="提交").click()
    page.get_by_role("button", name="确定").click()


def run(playwright):
    browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://1.tongji.edu.cn/questionnaireWriteOfStu")

    page.get_by_placeholder("用户名").click()
    page.get_by_placeholder("用户名").fill("2311471")
    page.get_by_placeholder("口令").click()
    page.get_by_placeholder("口令").fill("200073zhou")
    page.get_by_role("button", name="Login").click()

    input("login")

    page.locator(".show-menus-btn").click()
    page.get_by_text("我的教学评价").click()

    # 等待表格加载完成
    page.wait_for_selector(".el-table__body")

    page.get_by_role("textbox", name="请选择").click()
    page.get_by_text("1000条/页").nth(1).click()

    # 在特定的 div 区域内滚动
    page.evaluate("""() => {
           const scrollableSection = document.querySelector('.el-card__body .question-title-container');
           scrollableSection.scrollTop += 5000;  // 垂直向下滚动 500 像素
       }""")
    # 获取表格行数
    row_count = page.locator(".el-table__body tr").count()

    print(f"一共{row_count}条。")

    for i in range(1, row_count + 1):
        page.wait_for_selector(".el-table__body")

        page.get_by_role("textbox", name="请选择").click()
        page.get_by_text("1000条/页").nth(1).click()
        # 在特定的 div 区域内滚动
        page.evaluate("""() => {
                   const scrollableSection = document.querySelector('.el-card__body .question-title-container');
                   scrollableSection.scrollTop += 5000;  // 垂直向下滚动 500 像素
               }""")

        print(f"page {i}!")
        # 构建当前行的按钮选择器
        button_selector = f"tr:nth-child({i}) button"

        # 检查当前行是否有按钮
        if page.locator(button_selector).count() > 0:

            # 获取按钮文本
            button_text = page.locator(button_selector).text_content().strip()

            # 如果按钮文本是“评教”，则点击
            if button_text == "评教":
                page.locator(button_selector).click()
                do(page)
                print(f"finished {i}!")

    input("Press Enter to close the browser...")  # 完成操作后关闭浏览器
    browser.close()



    # page.locator("tr:nth-child(25) > .el-table_4_column_24 > .cell > .el-button").click()



with sync_playwright() as playwright:
    run(playwright)

