from bs4 import BeautifulSoup
import json
import os
import re
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
def get_html(url):
        options = Options()
        driver = webdriver.Chrome(options = options)
        driver.get(url)
        html = driver.page_source
        driver.quit()
        return html
def get_main_div(soup):
        problem_div = None
        for div in soup.find_all("div", class_ = "problemindexholder"):
                if div.get("problemindex"):
                        problem_div = div
                        break
        typography_div = problem_div.find("div", class_ = "ttypography")
        problem_statement_div = typography_div.find("div", class_ = "problem-statement")
        main_div = problem_statement_div.find("div", class_ = "header")
        return main_div
def get_time_limit(main_div):
        time_limit_div = main_div.find("div", class_ = "time-limit")
        return time_limit_div.get_text(" ", strip = True)[20:]
def get_memory_limit(main_div):
        memory_limit_div = main_div.find("div", class_ = "memory-limit")
        return memory_limit_div.get_text(" ", strip = True)[22:]
def get_statement(main_div):
        statement_parts = []
        for sibling in main_div.find_next_siblings():
                if sibling.get("class") and "input-specification" in sibling.get("class"):
                        break
                temp_soup = BeautifulSoup(str(sibling), "html.parser")
                for img in temp_soup.find_all("img"):
                        img.replace_with(handle_image(img))
                for math_script in temp_soup.find_all("script", {"type": re.compile(r"math/tex")}):
                        math_script.replace_with(handle_latex(math_script.string))
                for duplicate_span in temp_soup.find_all(class_ = re.compile(r"MathJax")):
                        duplicate_span.decompose()
                text_part = temp_soup.get_text(" ", strip = True)
                statement_parts.append(text_part)
        statement = " ".join(statement_parts).strip()
        return statement
def get_input_format(main_div):
        input_format_parts = []
        for sibling in main_div.find_next_siblings():
                if sibling.get("class") and "input-specification" in sibling.get("class"):
                        temp_soup = BeautifulSoup(str(sibling), "html.parser")
                        for img in temp_soup.find_all("img"):
                                img.replace_with(handle_image(img))
                        for math_script in temp_soup.find_all("script", {"type": re.compile(r"math/tex")}):
                                math_script.replace_with(handle_latex(math_script.string))
                        for duplicate_span in temp_soup.find_all(class_ = re.compile(r"MathJax")):
                                duplicate_span.decompose()
                        text_part = temp_soup.get_text(" ", strip = True)
                        input_format_parts.append(text_part)
        input_format = " ".join(input_format_parts).strip()
        return input_format[6:]
def get_output_format(main_div):
        output_format_parts = []
        for sibling in main_div.find_next_siblings():
                if sibling.get("class") and "output-specification" in sibling.get("class"):
                        temp_soup = BeautifulSoup(str(sibling), "html.parser")
                        for img in temp_soup.find_all("img"):
                                img.replace_with(handle_image(img))
                        for math_script in temp_soup.find_all("script", {"type": re.compile(r"math/tex")}):
                                math_script.replace_with(handle_latex(math_script.string))
                        for duplicate_span in temp_soup.find_all(class_ = re.compile(r"MathJax")):
                                duplicate_span.decompose()
                        text_part = temp_soup.get_text(" ", strip = True)
                        output_format_parts.append(text_part)
        output_format = " ".join(output_format_parts).strip()
        return output_format[7:]
def get_examples(main_div):
        examples = []
        for sibling in main_div.find_next_siblings():
                if sibling.get("class") and "sample-tests" in sibling.get("class"):
                        sample_test_divs = sibling.find_all("div", class_ = "sample-test")
                        for sample_test in sample_test_divs:
                                input_divs = sample_test.find_all("div", class_ = "input")
                                output_divs = sample_test.find_all("div", class_ = "output")
                                for input_div, output_div in zip(input_divs, output_divs):
                                        input_text = input_div.pre.get_text(" ", strip = True).replace("\n", " ")
                                        output_text = output_div.pre.get_text(" ", strip = True).replace("\n", " ")
                                        examples.append({"input": input_text, "output": output_text})
        return examples
def get_note(main_div):
        note_parts = []
        for sibling in main_div.find_next_siblings():
                if sibling.get("class") and "note" in sibling.get("class"):
                        temp_soup = BeautifulSoup(str(sibling), "html.parser")
                        for img in temp_soup.find_all("img"):
                                img.replace_with(handle_image(img))
                        for math_script in temp_soup.find_all("script", {"type": re.compile(r"math/tex")}):
                                math_script.replace_with(handle_latex(math_script.string))
                        for duplicate_span in temp_soup.find_all(class_ = re.compile(r"MathJax")):
                                duplicate_span.decompose()
                        text_part = temp_soup.get_text(" ", strip = True)
                        note_parts.append(text_part)
        note = " ".join(note_parts).strip()
        return note[5:]
def download_image(url, folder = "images"):
        if not os.path.exists(folder):
                os.makedirs(folder)
        filename = url.split("/")[-1]
        path = os.path.join(folder, filename)
        resp = requests.get(url)
        resp.raise_for_status()
        with open(path, "wb") as f:
                f.write(resp.content)
        return filename
def handle_image(img):
        src = img.get("src")
        if src.startswith("//"):
                src = "https:" + src
        elif src.startswith("/"):
                src = f"https://codeforces.com{src}"
        filename = download_image(src)
        return f"[IMAGE: images/{filename}]"
def handle_latex(latex):
        latex = latex.strip()
        latex = latex.replace("\n", " ")
        return f"$ {latex} $"
def parse_problem(contest_id, index):
        html = get_html(f"https://codeforces.com/contest/{contest_id}/problem/{index}")
        soup = BeautifulSoup(html, "html.parser")
        main_div = get_main_div(soup)
        time_limit = get_time_limit(main_div)
        memory_limit = get_memory_limit(main_div)
        statement = get_statement(main_div)
        input_format = get_input_format(main_div)
        output_format = get_output_format(main_div)
        examples = get_examples(main_div)
        note = get_note(main_div)
        return {
                "time_limit": time_limit,
                "memory_limit": memory_limit,
                "statement": statement,
                "input_format": input_format,
                "output_format": output_format,
                "examples": examples,
                "note": note,
        }
def parse_blogs(contest_id):
        url = f"https://codeforces.com/contest/{contest_id}"
        html = get_html(url)
        soup = BeautifulSoup(html, "html.parser")
        blog_entries = []
        sidebar_menu = soup.select_one("div.sidebar-menu ul")
        for li in sidebar_menu.find_all("li"):
                a_tag = li.find("a")
                title = a_tag.get_text(" ", strip=True)
                href = a_tag.get("href")
                if href.startswith("/"):
                        href = "https://codeforces.com" + href
                blog_entries.append({"title": title, "url": href})
        return blog_entries
def main():
        statements = "statements.json"
        if os.path.exists(statements):
                with open(statements, "r") as f:
                        s_json = json.load(f)
        else:
                s_json = {}
        blogs = "blogs.json"
        if os.path.exists(blogs):
                with open(blogs, "r") as f:
                        b_json = json.load(f)
                # Normalize keys to integers
                b_json = {int(k): v for k, v in b_json.items()}
        else:
                b_json = {}
        content = open("problems.json").read()
        problems = json.loads(content)
        problems = sorted(problems, key = lambda p: (p['contestId'], p['index']))
        with open("problems.json", "w") as f:
                json.dump(problems, f, indent = 8)
        for problem in problems:
                key = f"{problem['contestId']}{problem['index']}"
                if key not in s_json and key == "1776A":
                        try:
                                parsed = parse_problem(problem["contestId"], problem["index"])
                                s_json[key] = parsed
                                s_json = dict(sorted(s_json.items()))
                                with open(statements, "w") as f:
                                        json.dump(s_json, f, indent = 8)
                        except Exception as e:
                                # print(f"Problem {key}: Error - {e}\n")
                                raise e
                # id = int(problem["contestId"])
                # if id not in b_json:
                #         try:
                #                 parsed = parse_blogs(id)
                #                 b_json[id] = parsed
                #                 b_json = dict(sorted(b_json.items(), key=lambda item: int(item[0])))
                #                 with open(blogs, "w") as f:
                #                         json.dump(b_json, f, indent = 8)
                #         except Exception as e:
                #                 with open("errors.txt", "a") as f:
                #                         f.write(f"Contest {problem['contestId']}: Error - {e}\n")
main()