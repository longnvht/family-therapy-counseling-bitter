# -*- coding: utf-8 -*-
"""
PIPELINE TRÍCH XUẤT VÀ CHUYỂN NGỮ SÁCH:
Theory and Practice of Family Therapy and Counseling (2009)
Tác giả: James Robert Bitter, Ed.D.
"""

import os
import sys
import json
import re
import time
import hashlib
import urllib.request
import urllib.parse
from pathlib import Path
import pymupdf
from bs4 import BeautifulSoup

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).resolve().parent.parent
PDF_PATH = BASE_DIR.parent / "tri_lieu" / "James Robert Bitter (2009) - Theory and Practice of Family Therapy and Counseling.pdf"
CACHE_FILE = BASE_DIR / "cache_dich.json"
CHAPTERS_DIR = BASE_DIR / "chapters"
CHAPTERS_DIR.mkdir(parents=True, exist_ok=True)

GLOSSARY_REPLACEMENTS = [
    (r"\bkhách hàng\b", "thân chủ"),
    (r"\bKhách hàng\b", "Thân chủ"),
    (r"\bbác sĩ trị liệu\b", "nhà trị liệu"),
    (r"\bBác sĩ trị liệu\b", "Nhà trị liệu"),
    (r"\bliệu pháp gia đình\b", "trị liệu gia đình"),
    (r"\bLiệu pháp gia đình\b", "Trị liệu gia đình"),
    (r"\btư vấn gia đình\b", "tham vấn gia đình"),
    (r"\bTư vấn gia đình\b", "Tham vấn gia đình"),
    (r"\bngười hành nghề gia đình\b", "nhà thực hành gia đình"),
    (r"\bNgười hành nghề gia đình\b", "Nhà thực hành gia đình"),
    (r"\bở đây và bây giờ\b", "tại đây-và-ngay lúc này"),
    (r"\btại đây và bây giờ\b", "tại đây-và-ngay lúc này"),
    (r"\bTại đây và bây giờ\b", "Tại đây-và-ngay lúc này"),
    (r"\bphân biệt bản thân\b", "biệt hóa bản thân (differentiation of self)"),
    (r"\bPhân biệt bản thân\b", "Biệt hóa bản thân (differentiation of self)"),
    (r"\btam giác hóa\b", "tam giác hóa (triangulation)"),
    (r"\bTam giác hóa\b", "Tam giác hóa (triangulation)"),
    (r"\bcây phả hệ\b", "sơ đồ phả hệ (genogram)"),
    (r"\bCây phả hệ\b", "Sơ đồ phả hệ (genogram)"),
    (r"\bban hành\b", "dàn dựng tương tác (enactment)"),
    (r"\bBan hành\b", "Dàn dựng tương tác (enactment)"),
    (r"\btái cấu trúc\b", "tái đóng khung (reframing)"),
    (r"\btái định hình\b", "tái đóng khung (reframing)"),
    (r"\bcâu hỏi kỳ diệu\b", "câu hỏi phép màu (miracle question)"),
    (r"\bCâu hỏi kỳ diệu\b", "Câu hỏi phép màu (miracle question)"),
]

CHAPTER_METADATA = [
    {
        "id": "00_loi_tua_va_loi_mo_dau",
        "num": 0,
        "label": "Lời tựa & Lời mở đầu",
        "title_en": "FOREWORD BY GERALD COREY & PREFACE",
        "title_vi": "Lời Tựa của Gerald Corey & Lời Mở Đầu",
        "start_page": 25,
        "end_page": 36,
        "filename": "00_loi_tua_va_loi_mo_dau.html"
    },
    {
        "id": "01_gioi_thieu_tong_quan",
        "num": 1,
        "label": "Chương 1",
        "title_en": "INTRODUCTION AND OVERVIEW",
        "title_vi": "Giới Thiệu và Tổng Quan Về Trị Liệu Gia Đình",
        "start_page": 37,
        "end_page": 55,
        "filename": "01_gioi_thieu_tong_quan.html"
    },
    {
        "id": "02_nha_thuc_hanh_gia_dinh",
        "num": 2,
        "label": "Chương 2",
        "title_en": "THE FAMILY PRACTITIONER AS PERSON AND PROFESSIONAL",
        "title_vi": "Nhà Thực Hành Gia Đình: Phương Diện Cá Nhân và Nghề Nghiệp",
        "start_page": 56,
        "end_page": 74,
        "filename": "02_nha_thuc_hanh_gia_dinh.html"
    },
    {
        "id": "03_dao_duc_va_phap_ly",
        "num": 3,
        "label": "Chương 3",
        "title_en": "VIRTUE, ETHICS, AND LEGALITY IN FAMILY PRACTICE",
        "title_vi": "Đạo Đức, Phẩm Hạnh và Pháp Lý Trong Thực Hành Gia Đình",
        "start_page": 75,
        "end_page": 103,
        "filename": "03_dao_duc_va_phap_ly.html"
    },
    {
        "id": "04_tri_lieu_gia_dinh_da_the_he_bowen",
        "num": 4,
        "label": "Chương 4",
        "title_en": "MULTIGENERATIONAL FAMILY THERAPY",
        "title_vi": "Trị Liệu Gia Đình Đa Thế Hệ (Murray Bowen)",
        "start_page": 104,
        "end_page": 128,
        "filename": "04_tri_lieu_gia_dinh_da_the_he_bowen.html"
    },
    {
        "id": "05_tri_lieu_gia_dinh_adler",
        "num": 5,
        "label": "Chương 5",
        "title_en": "ADLERIAN FAMILY THERAPY",
        "title_vi": "Trị Liệu Gia Đình Theo Thuyết Adler",
        "start_page": 129,
        "end_page": 152,
        "filename": "05_tri_lieu_gia_dinh_adler.html"
    },
    {
        "id": "06_mo_hinh_xac_thuc_con_nguoi_satir",
        "num": 6,
        "label": "Chương 6",
        "title_en": "HUMAN VALIDATION PROCESS MODEL",
        "title_vi": "Mô Hình Tiến Trình Xác Thực Con Người (Virginia Satir)",
        "start_page": 153,
        "end_page": 176,
        "filename": "06_mo_hinh_xac_thuc_con_nguoi_satir.html"
    },
    {
        "id": "07_tri_lieu_bieu_tuong_trai_nghiem_whitaker",
        "num": 7,
        "label": "Chương 7",
        "title_en": "SYMBOLIC-EXPERIENTIAL FAMILY THERAPY",
        "title_vi": "Trị Liệu Gia Đình Biểu Tượng - Trải Nghiệm (Carl Whitaker)",
        "start_page": 177,
        "end_page": 197,
        "filename": "07_tri_lieu_bieu_tuong_trai_nghiem_whitaker.html"
    },
    {
        "id": "08_tri_lieu_gia_dinh_cau_truc_minuchin",
        "num": 8,
        "label": "Chương 8",
        "title_en": "STRUCTURAL FAMILY THERAPY",
        "title_vi": "Trị Liệu Gia Đình Cấu Trúc (Salvador Minuchin)",
        "start_page": 198,
        "end_page": 220,
        "filename": "08_tri_lieu_gia_dinh_cau_truc_minuchin.html"
    },
    {
        "id": "09_tri_lieu_gia_dinh_chien_luoc",
        "num": 9,
        "label": "Chương 9",
        "title_en": "STRATEGIC FAMILY THERAPY",
        "title_vi": "Trị Liệu Gia Đình Chiến Lược (MRI, Milan, Washington)",
        "start_page": 221,
        "end_page": 248,
        "filename": "09_tri_lieu_gia_dinh_chien_luoc.html"
    },
    {
        "id": "10_tri_lieu_tap_trung_giai_phap_sfbt",
        "num": 10,
        "label": "Chương 10",
        "title_en": "SOLUTION-FOCUSED AND SOLUTION-ORIENTED THERAPY",
        "title_vi": "Trị Liệu Tập Trung Vào Giải Pháp và Định Hướng Giải Pháp",
        "start_page": 249,
        "end_page": 270,
        "filename": "10_tri_lieu_tap_trung_giai_phap_sfbt.html"
    },
    {
        "id": "11_hau_hien_dai_va_tri_lieu_tuong_thuat",
        "num": 11,
        "label": "Chương 11",
        "title_en": "POSTMODERNISM, SOCIAL CONSTRUCTION, AND NARRATIVES IN FAMILY THERAPY",
        "title_vi": "Hậu Hiện Đại, Kiến Tạo Xã Hội và Liệu Pháp Tường Thuật",
        "start_page": 271,
        "end_page": 299,
        "filename": "11_hau_hien_dai_va_tri_lieu_tuong_thuat.html"
    },
    {
        "id": "12_tri_lieu_gia_dinh_nu_quyen",
        "num": 12,
        "label": "Chương 12",
        "title_en": "FEMINIST FAMILY THERAPY",
        "title_vi": "Trị Liệu Gia Đình Nữ Quyền",
        "start_page": 300,
        "end_page": 331,
        "filename": "12_tri_lieu_gia_dinh_nu_quyen.html"
    },
    {
        "id": "13_tri_lieu_gia_dinh_nhan_thuc_hanh_vi",
        "num": 13,
        "label": "Chương 13",
        "title_en": "COGNITIVE-BEHAVIORAL FAMILY THERAPY",
        "title_vi": "Trị Liệu Gia Đình Nhận Thức - Hành Vi",
        "start_page": 332,
        "end_page": 359,
        "filename": "13_tri_lieu_gia_dinh_nhan_thuc_hanh_vi.html"
    },
    {
        "id": "14_nuoi_day_con_the_ky_21",
        "num": 14,
        "label": "Chương 14",
        "title_en": "PARENTING FOR THE 21ST CENTURY",
        "title_vi": "Nuôi Dạy Con Trong Thế Kỷ 21",
        "start_page": 360,
        "end_page": 390,
        "filename": "14_nuoi_day_con_the_ky_21.html"
    },
    {
        "id": "15_tich_hop_1_tu_kham_pha_den_danh_gia",
        "num": 15,
        "label": "Chương 15",
        "title_en": "INTEGRATION I: FROM SELF-DISCOVERY TO FAMILY PRACTICE",
        "title_vi": "Tích Hợp I: Từ Khám Phá Bản Thân Đến Thiết Lập Quan Hệ & Đánh Giá",
        "start_page": 391,
        "end_page": 409,
        "filename": "15_tich_hop_1_tu_kham_pha_den_danh_gia.html"
    },
    {
        "id": "16_tich_hop_2_y_nghia_va_can_thiep",
        "num": 16,
        "label": "Chương 16",
        "title_en": "INTEGRATION II: SHARED MEANING, FACILITATING CHANGE, AND TAILORING INTERVENTIONS",
        "title_vi": "Tích Hợp II: Kiến Tạo Ý Nghĩa Chung, Thúc Đẩy Thay Đổi & Tinh Chỉnh Can Thiệp",
        "start_page": 410,
        "end_page": 422,
        "filename": "16_tich_hop_2_y_nghia_va_can_thiep.html"
    },
    {
        "id": "17_phu_luc_tong_ket_cac_mo_hinh",
        "num": 17,
        "label": "Phụ lục",
        "title_en": "APPENDIX: SUMMARY AND REVIEW OF FAMILY MODELS",
        "title_vi": "Phụ Lục: Tổng Kết và Đối Chiếu Các Mô Hình Trị Liệu Gia Đình",
        "start_page": 423,
        "end_page": 442,
        "filename": "17_phu_luc_tong_ket_cac_mo_hinh.html"
    }
]

class TranslationCache:
    def __init__(self, cache_file):
        self.cache_file = cache_file
        self.cache = {}
        self.load()

    def load(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    self.cache = json.load(f)
            except Exception as e:
                print(f"[Cache] Lỗi khi tải cache: {e}", flush=True)
                self.cache = {}

    def save(self):
        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[Cache] Lỗi khi ghi cache: {e}", flush=True)

    def get(self, text):
        h = hashlib.sha256(text.strip().encode("utf-8")).hexdigest()
        return self.cache.get(h)

    def set(self, text, translated_text):
        h = hashlib.sha256(text.strip().encode("utf-8")).hexdigest()
        self.cache[h] = translated_text


translation_cache = TranslationCache(CACHE_FILE)


def translate_chunk_google(text, retries=4, delay=2.0):
    text = text.strip()
    if not text:
        return ""

    cached = translation_cache.get(text)
    if cached:
        return cached

    # Nếu văn bản quá dài (> 2000 ký tự), chia thành các câu để dịch
    if len(text) > 2000:
        sentences = re.split(r'(?<=[.!?])\s+', text)
        translated_parts = []
        cur_chunk = ""
        for s in sentences:
            if len(cur_chunk) + len(s) < 1800:
                cur_chunk += (" " if cur_chunk else "") + s
            else:
                translated_parts.append(translate_chunk_google(cur_chunk))
                cur_chunk = s
        if cur_chunk:
            translated_parts.append(translate_chunk_google(cur_chunk))
        full_res = " ".join(translated_parts)
        translation_cache.set(text, full_res)
        return full_res

    # Phương pháp 1: Mobile Web endpoint (rất ổn định, không bị chặn 429)
    for attempt in range(retries):
        try:
            url_m = "https://translate.google.com/m?sl=en&tl=vi&q=" + urllib.parse.quote(text)
            req_m = urllib.request.Request(
                url_m,
                headers={"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15"}
            )
            with urllib.request.urlopen(req_m, timeout=12) as resp:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(resp.read().decode("utf-8"), "html.parser")
                res = soup.find("div", class_="result-container")
                if res and res.text:
                    translated = res.text.strip()
                    for pat, repl in GLOSSARY_REPLACEMENTS:
                        translated = re.sub(pat, repl, translated)
                    translation_cache.set(text, translated)
                    time.sleep(0.35)
                    return translated
        except Exception as e_m:
            # Phương pháp 2: API fallback
            try:
                url_api = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=vi&dt=t"
                post_data = urllib.parse.urlencode({"q": text}).encode("utf-8")
                req_api = urllib.request.Request(
                    url_api,
                    data=post_data,
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                )
                with urllib.request.urlopen(req_api, timeout=12) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    translated = "".join([s[0] for s in data[0] if s and s[0]])
                    for pat, repl in GLOSSARY_REPLACEMENTS:
                        translated = re.sub(pat, repl, translated)
                    translation_cache.set(text, translated)
                    time.sleep(0.35)
                    return translated
            except Exception as e_api:
                sleep_time = delay * (attempt + 1)
                print(f"[Dịch] Thử lại ({attempt + 1}/{retries}) cho đoạn ({len(text)} ký tự), tạm nghỉ {sleep_time}s: {e_m} | {e_api}", flush=True)
                time.sleep(sleep_time)

    return text


def clean_paragraph_text(raw_text):
    # Nối các từ bị gạch nối ở cuối dòng (e.g. psycho- therapy -> psychotherapy)
    t = re.sub(r"(\b\w+)-\s*\n\s*(\w+\b)", r"\1\2", raw_text)
    # Nối các dòng ngắt giữa câu
    t = re.sub(r"\s*\n\s*", " ", t)
    # Chuẩn hóa khoảng trắng
    t = re.sub(r"\s+", " ", t).strip()
    return t


def extract_chapter_content(doc, start_page, end_page):
    """
    Trích xuất các khối văn bản từ trang start_page đến end_page.
    Phân loại: heading_2, heading_3, paragraph, case_study, list_item.
    """
    elements = []
    in_case_study = False
    current_case_blocks = []

    for page_num in range(start_page - 1, end_page):
        page = doc[page_num]
        raw_blocks = page.get_text("blocks")

        for b in raw_blocks:
            t = b[4].strip()
            if not t:
                continue

            # Bỏ qua số trang đứng riêng
            if re.match(r"^\d+$", t):
                continue
            
            # Bỏ qua running header
            if ("THE THEORY AND PRACTICE OF GROUP PSYCHOTHERAPY" in t or 
                "THE THERAPEUTIC FACTORS" in t or
                "INTERPERSONAL LEARNING" in t or
                "GROUP COHESIVENESS" in t) and len(t) < 80:
                continue

            # Bỏ qua tên chương ở đầu nếu trùng tiêu đề
            if re.match(r"^-\s*\d+\s*-$", t):
                continue

            # Xử lý case study vignette bắt đầu bằng > và kết thúc bằng <<
            if t.startswith(">"):
                in_case_study = True
                cleaned = clean_paragraph_text(t.lstrip(">").strip())
                if "<<" in cleaned:
                    cleaned = cleaned.replace("<<", "").strip()
                    elements.append({"type": "case_study", "text": [cleaned], "page": page_num + 1})
                    in_case_study = False
                else:
                    current_case_blocks = [cleaned]
                continue

            if in_case_study:
                cleaned = clean_paragraph_text(t)
                if "<<" in cleaned:
                    cleaned = cleaned.replace("<<", "").strip()
                    current_case_blocks.append(cleaned)
                    elements.append({"type": "case_study", "text": current_case_blocks, "page": page_num + 1})
                    current_case_blocks = []
                    in_case_study = False
                else:
                    current_case_blocks.append(cleaned)
                continue

            cleaned = clean_paragraph_text(t)
            if not cleaned:
                continue

            # Bỏ qua lặp tiêu đề chương
            if cleaned.upper() in ["PREFACE TO THE SIXTH EDITION", "THE THERAPEUTIC FACTORS", "INTERPERSONAL LEARNING"]:
                continue

            # Nhận diện tiêu đề mục viết hoa toàn bộ (All Caps) hoặc danh sách subheadings
            is_all_caps = cleaned.isupper() and len(cleaned) < 100
            is_subheading = False
            subheadings_known = [
                "INSTILLATION OF HOPE", "UNIVERSALITY", "IMPARTING INFORMATION",
                "DIDACTIC INSTRUCTION", "DIRECT ADVICE", "ALTRUISM",
                "THE CORRECTIVE RECAPITULATION OF THE PRIMARY FAMILY GROUP",
                "DEVELOPMENT OF SOCIALIZING TECHNIQUES", "IMITATIVE BEHAVIOR",
                "THE IMPORTANCE OF INTERPERSONAL RELATIONSHIPS",
                "THE CORRECTIVE EMOTIONAL EXPERIENCE",
                "THE GROUP AS SOCIAL MICROCOSM",
                "DYNAMIC INTERACTION WITHIN THE SOCIAL MICROCOSM",
                "RECOGNITION OF BEHAVIORAL PATTERNS IN THE SOCIAL MICROCOSM",
                "THE SOCIAL MICROCOSM: IS IT REAL?",
                "TRANSFERENCE AND INSIGHT", "OVERVIEW",
                "MECHANISM OF ACTION", "SUMMARY",
                "COMPARATIVE VALUE OF THE THERAPEUTIC FACTORS",
                "CREATION AND MAINTENANCE OF THE GROUP",
                "BUILDING A GROUP CULTURE",
                "HOW DOES THE LEADER SHAPE NORMS?",
                "DEFINITION OF PROCESS", "TECHNIQUES OF PROCESS ILLUMINATION"
            ]

            for sh in subheadings_known:
                if cleaned.upper() == sh or cleaned.upper().startswith(sh):
                    is_subheading = True
                    break

            if is_all_caps and len(cleaned.split()) <= 12:
                elements.append({"type": "heading_2", "text": cleaned, "page": page_num + 1})
            elif is_subheading:
                elements.append({"type": "heading_2", "text": cleaned, "page": page_num + 1})
            elif re.match(r"^\d+\.\s+[A-Z]", cleaned) and len(cleaned) < 80:
                elements.append({"type": "list_item", "text": cleaned, "page": page_num + 1})
            else:
                elements.append({"type": "paragraph", "text": cleaned, "page": page_num + 1})

    # Nếu case study chưa đóng mà hết trang
    if in_case_study and current_case_blocks:
        elements.append({"type": "case_study", "text": current_case_blocks, "page": end_page})

    return elements


def generate_chapter_html(meta, prev_meta, next_meta, translated_elements):
    """
    Sinh file HTML hoàn chỉnh cho một chương.
    """
    ch_num_label = meta["label"]
    title_vi = meta["title_vi"]
    title_en = meta["title_en"]

    content_html = []
    for el in translated_elements:
        el_type = el["type"]
        if el_type == "heading_2":
            content_html.append(f'<h2>{el["vi"]}</h2>')
        elif el_type == "heading_3":
            content_html.append(f'<h3>{el["vi"]}</h3>')
        elif el_type == "case_study":
            paras = "".join([f'<p>{p}</p>' for p in el["vi"]])
            content_html.append(f'''
<div class="case-study">
  <div class="case-study-header">
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
    Trường Hợp Lâm Sàng Thực Tế
  </div>
  {paras}
</div>''')
        elif el_type == "list_item":
            content_html.append(f'<p><strong>{el["vi"]}</strong></p>')
        else:
            # Paragraph
            # Xử lý số chú thích sup
            text_vi = re.sub(r'(\d+)\b(?=\s+[A-ZÀ-Ỹ])', r'<sup class="footnote-ref">[\1]</sup>', el["vi"])
            content_html.append(f'<p>{text_vi}</p>')

    content_str = "\n".join(content_html)

    # Nút điều hướng trước / sau
    prev_link = ""
    if prev_meta:
        prev_link = f'''
        <a href="{prev_meta["filename"]}" class="chapter-nav-prev">
          <span class="nav-label">&larr; {prev_meta["label"]}</span>
          <span class="nav-title">{prev_meta["title_vi"]}</span>
        </a>'''

    next_link = ""
    if next_meta:
        next_link = f'''
        <a href="{next_meta["filename"]}" class="chapter-nav-next">
          <span class="nav-label">{next_meta["label"]} &rarr;</span>
          <span class="nav-title">{next_meta["title_vi"]}</span>
        </a>'''

    # Toàn bộ mã HTML của chương
    html = f'''<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{ch_num_label}: {title_vi} | Theory and Practice of Family Therapy and Counseling</title>
  <link rel="stylesheet" href="../style.css">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Merriweather:ital,wght@0,300;0,400;0,700;1,300;1,400&display=swap" rel="stylesheet">
</head>
<body>
  <!-- Top Toolbar -->
  <header class="top-toolbar">
    <div class="toolbar-left">
      <button class="btn-tool" id="btn-toggle-sidebar" title="Đóng/Mở Mục lục">&#9776; Mục lục</button>
      <a href="../index.html" class="btn-tool" title="Về trang chủ">&#127968; Trang chủ</a>
      <span class="book-badge">Yalom & Leszcz (6th Ed.)</span>
      <span class="book-title-mini">{ch_num_label}: {title_vi}</span>
    </div>
    <div class="toolbar-right">
      <button class="btn-tool" id="btn-font-dec" title="Giảm cỡ chữ">A-</button>
      <button class="btn-tool" id="btn-font-inc" title="Tăng cỡ chữ">A+</button>
      <button class="btn-tool" id="btn-theme" title="Đổi giao diện sáng/tối"><span>☀️ Sáng</span></button>
      <button class="btn-tool" id="btn-print" title="In hoặc lưu PDF">&#128438; In</button>
    </div>
  </header>

  <div class="app-container">
    <!-- Sidebar Navigation -->
    <aside class="sidebar">
      <div class="sidebar-search">
        <input type="text" id="toc-search-input" placeholder="Tìm kiếm chương...">
      </div>
      <div class="toc-title">Danh Mục Chương</div>
      <ul class="toc-list">
        {generate_sidebar_links(meta["id"])}
      </ul>
    </aside>

    <!-- Main Content Area -->
    <main class="main-wrapper">
      <article class="content-article">
        <header class="book-header">
          <div class="chapter-number">{ch_num_label} (Trang {meta["start_page"]} - {meta["end_page"]})</div>
          <h1 class="chapter-title">{title_vi}</h1>
          <div class="chapter-authors">Nguyên tác: <em>{title_en}</em> &bull; James Robert Bitter, Ed.D.</div>
        </header>

        <div class="chapter-body">
          {content_str}
        </div>

        <nav class="chapter-nav">
          {prev_link}
          {next_link}
        </nav>
      </article>
    </main>
  </div>

  <button class="btn-back-to-top" id="btn-back-to-top" title="Lên đầu trang">&uarr;</button>

  <script src="../reader.js"></script>
</body>
</html>'''
    return html


def generate_sidebar_links(current_id):
    links = []
    for item in CHAPTER_METADATA:
        active_cls = " active" if item["id"] == current_id else ""
        ch_file = item["filename"]
        links.append(f'''
        <li class="toc-item">
          <a href="{ch_file}" class="toc-link{active_cls}">
            <span class="toc-num">{item["num"] if item["num"] > 0 else "0"}</span>
            <span class="toc-name">{item["label"]}: {item["title_vi"]}</span>
          </a>
        </li>''')
    return "\n".join(links)


def translate_chapter(meta_idx):
    meta = CHAPTER_METADATA[meta_idx]
    prev_meta = CHAPTER_METADATA[meta_idx - 1] if meta_idx > 0 else None
    next_meta = CHAPTER_METADATA[meta_idx + 1] if meta_idx + 1 < len(CHAPTER_METADATA) else None

    print(f"\n==================================================", flush=True)
    print(f"BẮT ĐẦU XỬ LÝ: {meta['label']} - {meta['title_vi']}", flush=True)
    print(f"Trang PDF: {meta['start_page']} đến {meta['end_page']}", flush=True)
    print(f"==================================================", flush=True)

    doc = pymupdf.open(str(PDF_PATH))
    elements = extract_chapter_content(doc, meta["start_page"], meta["end_page"])
    print(f"-> Đã bóc tách được {len(elements)} phân đoạn.", flush=True)

    translated_elements = []
    total = len(elements)

    for idx, el in enumerate(elements):
        el_type = el["type"]
        if el_type == "case_study":
            vi_paras = []
            for p in el["text"]:
                t_vi = translate_chunk_google(p)
                vi_paras.append(t_vi)
            translated_elements.append({"type": el_type, "vi": vi_paras, "page": el["page"]})
        else:
            t_vi = translate_chunk_google(el["text"])
            translated_elements.append({"type": el_type, "vi": t_vi, "page": el["page"]})

        # Lưu cache thường xuyên
        translation_cache.save()

        if (idx + 1) % 10 == 0 or (idx + 1) == total:
            print(f"  [Tiến độ: {idx + 1}/{total} ({((idx + 1)/total)*100:.1f}%)]", flush=True)

    # Sinh HTML
    out_file = CHAPTERS_DIR / meta["filename"]
    html_content = generate_chapter_html(meta, prev_meta, next_meta, translated_elements)
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"-> HOÀN THÀNH: Đã ghi ra file {out_file.name} thành công!\n", flush=True)

    # Tự động cập nhật lại index.html và toan_bo_sach.html
    build_index_page()
    try:
        from build_master_html import build_master
        build_master()
    except Exception as e:
        print(f"[Cảnh báo] Không thể cập nhật toan_bo_sach.html: {e}", flush=True)


def build_index_page():
    """
    Sinh trang chủ index.html tổng quan toàn bộ cuốn sách.
    """
    index_file = BASE_DIR / "index.html"
    ch_cards = []
    for item in CHAPTER_METADATA:
        num_str = f"Chương {item['num']}" if item["num"] > 0 else item["label"]
        ch_file = f"chapters/{item['filename']}"
        file_path = CHAPTERS_DIR / item['filename']
        is_ready = file_path.exists()
        
        status_badge = '<span class="status-badge ready">✓ Đã dịch &bull; Sẵn sàng đọc</span>' if is_ready else '<span class="status-badge pending">⏳ Sẵn sàng chạy dịch</span>'
        item_num = item["num"]
        btn_str = f'<a href="{ch_file}" class="card-btn">Đọc chương này &rarr;</a>' if is_ready else f'<span class="card-btn disabled" title="Dùng lệnh: python dich_tu_dong.py --chapter {item_num}">Chưa tạo file</span>'
        
        ch_cards.append(f'''
        <div class="chapter-card{' is-ready' if is_ready else ''}">
          <div class="card-top-row">
            <span class="card-num">{num_str}</span>
            {status_badge}
          </div>
          <h3 class="card-title"><a href="{ch_file if is_ready else '#'}">{item["title_vi"]}</a></h3>
          <div class="card-original">{item["title_en"]}</div>
          <div class="card-meta">Trang PDF: {item["start_page"]} - {item["end_page"]}</div>
          <div class="card-action">
            {btn_str}
          </div>
        </div>''')

    cards_str = "\n".join(ch_cards)

    html = f'''<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Lý Thuyết Và Thực Hành Trị Liệu Gia Đình | James Robert Bitter</title>
  <link rel="stylesheet" href="style.css">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Merriweather:ital,wght@0,300;0,400;0,700;1,300;1,400&display=swap" rel="stylesheet">
  <style>
    .home-hero {{
      text-align: center;
      padding: 3rem 1rem 2.5rem;
      border-bottom: 2px solid var(--border-color);
      margin-bottom: 3rem;
    }}
    .home-hero h1 {{
      font-size: 2.6rem;
      color: var(--accent-color);
      margin-bottom: 0.75rem;
      line-height: 1.25;
    }}
    .home-hero .subtitle {{
      font-size: 1.25rem;
      color: var(--text-secondary);
      margin-bottom: 1.25rem;
      font-style: italic;
    }}
    .home-hero .authors {{
      font-family: var(--font-sans);
      font-size: 1.05rem;
      font-weight: 600;
      color: var(--text-primary);
    }}
    .home-hero .edition-badge {{
      display: inline-block;
      margin-top: 1rem;
      padding: 0.35rem 0.9rem;
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      border-radius: 20px;
      font-family: var(--font-sans);
      font-size: 0.85rem;
      color: var(--accent-color);
      font-weight: 600;
    }}
    .chapters-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
      gap: 1.5rem;
      margin-bottom: 4rem;
    }}
    .chapter-card {{
      background: var(--card-bg);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 1.5rem;
      display: flex;
      flex-direction: column;
      transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
    }}
    .chapter-card:hover {{
      transform: translateY(-3px);
      box-shadow: 0 8px 18px rgba(0,0,0,0.06);
      border-color: var(--accent-color);
    }}
    .card-num {{
      font-family: var(--font-sans);
      font-size: 0.8rem;
      font-weight: 700;
      color: var(--accent-color);
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-bottom: 0.4rem;
    }}
    .card-title {{
      font-size: 1.25rem;
      line-height: 1.35;
      margin-bottom: 0.4rem;
    }}
    .card-title a {{
      text-decoration: none;
      color: var(--text-primary);
    }}
    .card-title a:hover {{
      color: var(--accent-color);
    }}
    .card-original {{
      font-size: 0.85rem;
      color: var(--text-secondary);
      font-style: italic;
      margin-bottom: 0.75rem;
    }}
    .card-meta {{
      font-family: var(--font-sans);
      font-size: 0.8rem;
      color: var(--text-secondary);
      margin-top: auto;
      padding-top: 1rem;
    }}
    .chapter-card.is-ready {{
      border-color: #52c41a;
      background: var(--card-bg);
    }}
    .card-top-row {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 0.6rem;
    }}
    .status-badge {{
      font-family: var(--font-sans);
      font-size: 0.72rem;
      padding: 0.15rem 0.5rem;
      border-radius: 4px;
      font-weight: 600;
    }}
    .status-badge.ready {{
      background-color: #d4edda;
      color: #155724;
      border: 1px solid #c3e6cb;
    }}
    .status-badge.pending {{
      background-color: #fff3cd;
      color: #856404;
      border: 1px solid #ffeeba;
    }}
    .card-btn {{
      display: inline-block;
      margin-top: 0.75rem;
      font-family: var(--font-sans);
      font-size: 0.85rem;
      font-weight: 600;
      color: var(--accent-color);
      text-decoration: none;
    }}
    .card-btn:hover {{
      text-decoration: underline;
    }}
    .card-btn.disabled {{
      color: var(--text-secondary);
      cursor: not-allowed;
      text-decoration: none;
      opacity: 0.7;
    }}
    .intro-box {{
      background: var(--bg-secondary);
      border-radius: 8px;
      padding: 1.75rem 2rem;
      margin-bottom: 3rem;
      font-size: 0.95rem;
      line-height: 1.75;
    }}
    .intro-box h2 {{
      margin-top: 0;
      border-bottom: none;
      padding-bottom: 0;
      font-size: 1.35rem;
    }}
  </style>
</head>
<body>
  <!-- Top Toolbar -->
  <header class="top-toolbar">
    <div class="toolbar-left">
      <span class="book-badge">Tác phẩm kinh điển</span>
      <span class="book-title-mini">Lý Thuyết Và Thực Hành Trị Liệu Gia Đình (James Bitter)</span>
    </div>
    <div class="toolbar-right">
      <button class="btn-tool" id="btn-font-dec">A-</button>
      <button class="btn-tool" id="btn-font-inc">A+</button>
      <button class="btn-tool" id="btn-theme"><span>☀️ Sáng</span></button>
      <a href="toan_bo_sach.html" class="btn-tool" title="Xem bản một file duy nhất">&#128218; Toàn bộ sách</a>
    </div>
  </header>

  <div class="main-wrapper full-width">
    <article class="content-article" style="max-width: 1100px;">
      <div class="home-hero">
        <h1>LÝ THUYẾT VÀ THỰC HÀNH TRỊ LIỆU GIA ĐÌNH</h1>
        <div class="subtitle">Theory and Practice of Family Therapy and Counseling</div>
        <div class="authors">Tác giả: GS. James Robert Bitter, Ed.D. &bull; Lời tựa: Gerald Corey, Ed.D.</div>
        <div class="edition-badge">Giáo Trình Chuẩn Mực Về Trị Liệu Gia Đình &bull; 482 Trang</div>
      </div>

      <div class="intro-box">
        <h2>Giới Thiệu Tác Phẩm & Dự Án Bản Dịch Tiếng Việt</h2>
        <p>
          <strong>"Theory and Practice of Family Therapy and Counseling"</strong> của GS. James Robert Bitter là cuốn cẩm nang kinh điển hàng đầu thế giới được sử dụng để đào tạo các nhà tâm lý trị liệu, bác sĩ tâm thần và nhân viên công tác xã hội trong suốt hơn 5 thập kỷ qua. Bản tái bản lần thứ 6 (2020) kết hợp cùng GS. Gerald Corey cập nhật toàn diện những nghiên cứu thực chứng dựa trên bằng chứng (evidence-based), kỹ thuật trị liệu trực tuyến (VTC), cũng như các định dạng nhóm chuyên biệt.
        </p>
        <p>
          Tài liệu này được trích xuất trực tiếp từ nguyên bản PDF và chuyển ngữ sang tiếng Việt học thuật, chuẩn hóa các khái niệm then chốt như: <em>Truyền thụ hy vọng, Tính phổ quát, Trải nghiệm cảm xúc sửa chữa, Nhóm như một tiểu vũ trụ xã hội, Làm việc tại đây-và-ngay lúc này, Chuyển di và Tính minh bạch</em>.
        </p>
      </div>

      <h2 style="margin-bottom: 1.5rem;">Mục Lục Toàn Bộ Tác Phẩm</h2>
      <div class="chapters-grid">
        {cards_str}
      </div>
    </article>
  </div>

  <button class="btn-back-to-top" id="btn-back-to-top" title="Lên đầu trang">&uarr;</button>
  <script src="reader.js"></script>
</body>
</html>'''

    with open(index_file, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"-> Đã tạo trang chủ {index_file} thành công!", flush=True)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Chuyển ngữ sách Yalom Group Psychotherapy sang HTML")
    parser.add_argument("--preface", action="store_true", help="Dịch Lời nói đầu")
    parser.add_argument("--chapter", type=int, help="Dịch số chương chỉ định (1 - 16)")
    parser.add_argument("--range", nargs=2, type=int, metavar=('START', 'END'), help="Dịch khoảng các chương, ví dụ: --range 2 3")
    parser.add_argument("--next", type=int, default=1, help="Dịch N chương tiếp theo chưa dịch")
    parser.add_argument("--all", action="store_true", help="Dịch toàn bộ các chương")
    parser.add_argument("--build-index", action="store_true", help="Sinh trang chủ index.html")

    args = parser.parse_args()

    build_index_page()

    if args.preface:
        translate_chapter(0)
    elif args.chapter is not None:
        idx = next((i for i, c in enumerate(CHAPTER_METADATA) if c["num"] == args.chapter), None)
        if idx is not None:
            translate_chapter(idx)
        else:
            print(f"Không tìm thấy chương {args.chapter}", flush=True)
    elif args.range is not None:
        start_c, end_c = args.range
        for c in range(start_c, end_c + 1):
            idx = next((i for i, item in enumerate(CHAPTER_METADATA) if item["num"] == c), None)
            if idx is not None:
                translate_chapter(idx)
    elif args.all:
        for i in range(len(CHAPTER_METADATA)):
            translate_chapter(i)
    else:
        # Mặc định tìm các chương chưa dịch và dịch tiếp
        untranslated = [i for i, c in enumerate(CHAPTER_METADATA) if not (CHAPTERS_DIR / c["filename"]).exists()]
        if untranslated:
            to_run = untranslated[:args.next]
            print(f"Tìm thấy {len(untranslated)} chương chưa dịch. Tiến hành dịch {len(to_run)} chương...", flush=True)
            for i in to_run:
                translate_chapter(i)
        else:
            print("Tất cả các chương đều đã được dịch hoàn tất!", flush=True)

