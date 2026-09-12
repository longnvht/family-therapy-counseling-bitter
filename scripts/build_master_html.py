"""
Script gộp toàn bộ các chương đã dịch thành một file HTML duy nhất: toan_bo_sach.html
Thuận tiện cho việc in ấn trọn bộ hoặc tìm kiếm offline toàn văn.
"""

from pathlib import Path
import re
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).resolve().parent.parent
CHAPTERS_DIR = BASE_DIR / "chapters"
OUTPUT_FILE = BASE_DIR / "toan_bo_sach.html"

def build_master():
    chapter_files = sorted(list(CHAPTERS_DIR.glob("*.html")))
    if not chapter_files:
        print("Chưa có chương nào được tạo!")
        return

    combined_body = []
    
    for ch_file in chapter_files:
        content = ch_file.read_text(encoding="utf-8")
        # Trích xuất nội dung bên trong <article class="content-article">...</article>
        m = re.search(r'<article class="content-article">(.*?)</article>', content, re.DOTALL)
        if m:
            article_content = m.group(1)
            # Bỏ phần nav cuối chương
            article_content = re.sub(r'<nav class="chapter-nav">.*?</nav>', '', article_content, flags=re.DOTALL)
            combined_body.append(f'<section class="book-chapter-section" id="{ch_file.stem}">\n{article_content}\n</section>\n<div class="chapter-divider"></div>')

    all_sections = "\n".join(combined_body)

    master_html = f'''<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Toàn Bộ Sách: Lý Thuyết Và Thực Hành Trị Liệu Gia Đình | James Robert Bitter</title>
  <link rel="stylesheet" href="style.css">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Merriweather:ital,wght@0,300;0,400;0,700;1,300;1,400&display=swap" rel="stylesheet">
  <style>
    .chapter-divider {{
      height: 3px;
      background: linear-gradient(to right, transparent, var(--border-color), transparent);
      margin: 4rem 0;
      page-break-after: always;
    }}
    .master-cover {{
      text-align: center;
      padding: 5rem 1rem;
      border-bottom: 3px double var(--border-color);
      margin-bottom: 4rem;
    }}
    .master-cover h1 {{
      font-size: 2.8rem;
      color: var(--accent-color);
      margin-bottom: 1rem;
    }}
    .master-cover .author-line {{
      font-size: 1.3rem;
      margin-bottom: 2rem;
    }}
  </style>
</head>
<body>
  <header class="top-toolbar">
    <div class="toolbar-left">
      <a href="index.html" class="btn-tool">&#127968; Trang chủ</a>
      <span class="book-badge">Bản Toàn Văn</span>
      <span class="book-title-mini">Lý Thuyết Và Thực Hành Trị Liệu Gia Đình (Bản In)</span>
    </div>
    <div class="toolbar-right">
      <button class="btn-tool" id="btn-font-dec">A-</button>
      <button class="btn-tool" id="btn-font-inc">A+</button>
      <button class="btn-tool" id="btn-theme"><span>☀️ Sáng</span></button>
      <button class="btn-tool" id="btn-print">&#128438; In / Xuất PDF</button>
    </div>
  </header>

  <div class="main-wrapper full-width">
    <div class="content-article" style="max-width: 900px;">
      <div class="master-cover">
        <h1>LÝ THUYẾT VÀ THỰC HÀNH TRỊ LIỆU GIA ĐÌNH</h1>
        <div style="font-size: 1.2rem; font-style: italic; color: var(--text-secondary); margin-bottom: 1rem;">
          Theory and Practice of Family Therapy and Counseling (2009)
        </div>
        <div class="author-line">
          <strong>James Robert Bitter, Ed.D.</strong>
        </div>
        <div style="color: var(--text-secondary); font-size: 0.95rem;">
          Bản Dịch Tiếng Việt Học Thuật &bull; Định Dạng HTML E-Book Chuyên Biệt
        </div>
      </div>

      {all_sections}
    </div>
  </div>

  <button class="btn-back-to-top" id="btn-back-to-top">&uarr;</button>
  <script src="reader.js"></script>
</body>
</html>'''

    OUTPUT_FILE.write_text(master_html, encoding="utf-8")
    print(f"-> Đã tạo file toàn văn tổng hợp: {OUTPUT_FILE} ({len(chapter_files)} chương)")

if __name__ == "__main__":
    build_master()

