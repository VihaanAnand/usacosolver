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
def parse_blog(blog_id):
        url = f"https://codeforces.com/blog/entry/{blog_id}"
        html = get_html(url)
        soup = BeautifulSoup(html, "html.parser")
        main = soup.select_one("div.ttypography")

        content_parts = []

        def process(elem):
                if elem.name == "img":
                        return handle_image(elem) + "\n"
                elif elem.name == "script" and elem.get("type", "").startswith("math/tex"):
                        return handle_latex(elem.string or "") + "\n"
                elif elem.name == "pre" or elem.name == "code":
                        code_text = elem.get_text()
                        return f"```\n{code_text.strip()}\n```"
                elif elem.name in ["br"]:
                        return "\n"
                elif elem.name in ["p", "div", "h1", "h2", "h3", "h4", "h5", "h6"]:
                        inner = "".join(process(child) if hasattr(child, 'name') else str(child) for child in elem.children)
                        return inner.strip() + "\n"
                elif isinstance(elem, str):
                        return elem.strip() + "\n"
                else:
                        return elem.get_text().strip() + "\n"

        for elem in main.children:
                out = process(elem)
                if out:
                        content_parts.append(out)

        content = "\n".join(content_parts)
        content = re.sub(r"\n{3,}", "\n\n", content)
        return html, content.strip()
def main():
        count = 0
        file = "blogcontent.json"
        if os.path.exists(file):
                with open(file, "r") as f:
                        jsonobject = json.load(f)
        else:
                jsonobject = {}
        content = open("blogs.json").read()
        blogs = json.loads(content)
        blogs = dict(sorted(blogs.items()))
        with open("blogs.json", "w") as f:
                json.dump(blogs, f, indent = 8)
        for _, contest in blogs.items():
                for blog in contest:
                        id = blog["url"].split("/")[-1]
                        stuff = "happy happy happy"
                        if id not in jsonobject:
                                try:
                                        stuff = parse_blog(id)
                                        parsed = stuff[1]
                                        count += 1
                                        if "#include" in parsed:
                                                jsonobject[id] = parsed
                                                jsonobject = dict(sorted(jsonobject.items()))
                                                with open(file, "w") as f:
                                                        json.dump(jsonobject, f, indent = 8)
                                        else:
                                                with open("htmls/" + id + ".html", "w") as f:
                                                        f.write(stuff[0])
                                                with open("errors.txt", "a") as f:
                                                        f.write(f"Blog {id}: No #include found\n")
                                except Exception as e:
                                        with open("htmls/" + id + ".html", "w") as f:
                                                f.write(stuff[0])
                                        with open("errors.txt", "a") as f:
                                                f.write(f"Blog {id}: Error - {e}\n")
main()