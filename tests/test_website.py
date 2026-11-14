"""
quanrule-website 自动化测试套件（无需第三方依赖，Python 标准库）。

运行方式（在项目根目录）：
    python tests/test_website.py

全部通过时退出码为 0，任一断言失败时退出码为 1。
"""
import os
import sys
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def path(*parts):
    return os.path.join(ROOT, *parts)


def test_required_files_exist():
    """项目关键文件必须存在。"""
    required = [
        "index.html",
        "config.js",
        "netlify.toml",
        "robots.txt",
        "sitemap.xml",
        "LICENSE",
        "README.md",
        "netlify/edge-functions/sb.js",
    ]
    for f in required:
        assert os.path.isfile(path(f)), "缺少必需文件: " + f


def test_index_html_structure():
    """index.html 必须具备基本 HTML 结构。"""
    html = open(path("index.html"), encoding="utf-8").read()
    assert re.search(r"<!DOCTYPE html>", html, re.IGNORECASE), "缺少 DOCTYPE"
    assert "<html" in html.lower(), "缺少 <html> 标签"
    assert "<head" in html.lower(), "缺少 <head> 标签"
    assert "<body" in html.lower(), "缺少 <body> 标签"
    assert "<title" in html.lower(), "缺少 <title> 标签"


def test_assets_referenced_exist():
    """index.html 中以相对路径引用的本地资源必须真实存在。"""
    html = open(path("index.html"), encoding="utf-8").read()
    refs = re.findall(r'(?:src|href)\s*=\s*["\'](?!https?://|#|/|mailto:|data:)([^"\']+)["\']', html)
    for ref in refs:
        ref = ref.split("?")[0]
        assert os.path.exists(path(ref)), "引用的本地资源不存在: " + ref


def test_license_is_apache():
    """许可证文件必须是 Apache-2.0。"""
    lic = open(path("LICENSE"), encoding="utf-8").read()
    assert "Apache License" in lic and "Version 2.0" in lic, "许可证不是 Apache-2.0"


def test_no_service_role_key():
    """源码中不得出现 Supabase 高危 service_role 密钥。"""
    for dirpath, _dirs, files in os.walk(ROOT):
        if ".git" in dirpath or "_backup" in dirpath or "tests" in dirpath:
            continue
        for name in files:
            if not name.endswith((".js", ".html", ".py", ".json", ".toml")):
                continue
            text = open(os.path.join(dirpath, name), encoding="utf-8", errors="ignore").read()
            assert "service_role" not in text, "发现 service_role 标记: " + name


TESTS = [
    test_required_files_exist,
    test_index_html_structure,
    test_assets_referenced_exist,
    test_license_is_apache,
    test_no_service_role_key,
]


def main():
    failed = 0
    for test in TESTS:
        try:
            test()
            print("PASS " + test.__name__)
        except AssertionError as e:
            failed += 1
            print("FAIL " + test.__name__ + " -> " + str(e))
    print("------------------------------")
    print("通过 %d/%d" % (len(TESTS) - failed, len(TESTS)))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
