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

BOOK_BADGE = "Bitter (2009)"

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
        "end_page": 31,
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
    # OCR hay đọc nhầm chữ "I" đứng riêng lẻ thành "|" hoặc "|!"
    t = re.sub(r"(?<=\s)\|!?(?=\s|$)", "I", t)
    t = re.sub(r"^\|!?(?=\s)", "I", t)
    return t


# ---------------------------------------------------------------------------
# Trích xuất PDF: dùng get_text("dict") để lấy cỡ chữ (size) của từng khối,
# nhờ đó phân biệt được tiêu đề thật (size lớn) với đoạn văn thường, đồng
# thời lọc được header/số trang lặp lại theo VỊ TRÍ trên trang (đầu/cuối
# trang, dòng ngắn) thay vì danh sách chuỗi cố định của một cuốn sách khác.
# ---------------------------------------------------------------------------

HEADER_FOOTER_RE = re.compile(
    r'^(?:[ivxlc]{1,6}\b|\d{1,4}\b|part\s+\d+|chapter\s+\d+)',
    re.IGNORECASE
)
CHAPTER_LABEL_RE = re.compile(r'^chapter\s+\d+$', re.IGNORECASE)
BULLET_RE = re.compile(r'^[ -ÿ]\s+(?=[A-Za-z])')
NUM_LIST_RE = re.compile(r'^\d+\.\s+(?=[A-Z])')
SENTENCE_END_RE = re.compile(r'[.!?][\"”’\)\]]*\s*$')


def _norm_key(s):
    return re.sub(r'[^a-z0-9]+', '', s.lower())


def _page_blocks_in_reading_order(page):
    d = page.get_text("dict")
    blocks = []
    for b in d["blocks"]:
        if b.get("type") != 0:
            continue
        spans = [sp for ln in b.get("lines", []) for sp in ln["spans"]]
        if not spans:
            continue
        raw = "".join(sp["text"] for sp in spans)
        size = max((sp["size"] for sp in spans), default=0)
        blocks.append({"raw": raw, "size": size, "bbox": b["bbox"]})

    page_width = page.rect.width
    mid = page_width / 2
    left = sorted([b for b in blocks if b["bbox"][0] < mid], key=lambda b: b["bbox"][1])
    right = sorted([b for b in blocks if b["bbox"][0] >= mid], key=lambda b: b["bbox"][1])
    return left + right


def _looks_like_real_heading(text):
    """Phân biệt tiêu đề mục thật với nhãn rời rạc trong sơ đồ phả hệ
    (genogram) hay các mảnh vỡ khác vô tình bị OCR ra cỡ chữ lớn."""
    text = text.strip()
    if len(text) < 4:
        return False
    letters = sum(c.isalpha() for c in text)
    if letters / len(text) < 0.6:
        return False
    words = [w for w in re.split(r'\s+', text) if w]
    real_words = [w for w in words if sum(c.isalpha() for c in w) >= 2]
    if not words or len(real_words) / len(words) < 0.6:
        return False
    # Tiêu đề thật trong sách này luôn ở dạng Title Case (có chữ thường xen
    # kẽ) - chuỗi toàn chữ hoa ngắn thường là nhãn vô nghĩa trong sơ đồ.
    if not any(c.islower() for c in text):
        return False
    if len(re.findall(r'[|+_—–]', text)) >= 2:
        return False
    return True


def _is_running_header(text, bbox, page_height):
    if len(text) > 110:
        return False
    height = bbox[3] - bbox[1]
    if height > 24:
        return False
    near_top = bbox[1] < 36
    near_bottom = bbox[3] > page_height - 36
    if not (near_top or near_bottom):
        return False
    return bool(HEADER_FOOTER_RE.match(text.strip()))


def extract_chapter_content(doc, meta):
    """
    Trích xuất nội dung chương từ start_page đến end_page.
    Trả về danh sách phần tử {"type": ..., "text"/"vi_text": ...}
    type có thể là: heading_2, paragraph, list_item (ordered=True/False qua text riêng), case_study.
    """
    start_page, end_page = meta["start_page"], meta["end_page"]
    title_en_key = _norm_key(meta["title_en"])

    elements = []
    toc_collect_mode = False
    just_saw_chapter_label = False

    paragraph_buf = []
    buf_type = "paragraph"

    in_case_study = False
    case_study_buf = []

    def ends_sentence(t):
        return bool(SENTENCE_END_RE.search(t.strip()))

    def flush_paragraph():
        nonlocal paragraph_buf, buf_type
        if paragraph_buf:
            joined = paragraph_buf[0]
            for extra in paragraph_buf[1:]:
                if joined.endswith('-') and len(joined) > 1 and joined[-2].isalpha():
                    joined = joined[:-1] + extra
                else:
                    joined = joined + ' ' + extra
            joined = joined.strip()
            if joined:
                elements.append({"type": buf_type, "text": joined})
        paragraph_buf = []
        buf_type = "paragraph"

    for page_num in range(start_page - 1, end_page):
        page = doc[page_num]
        page_height = page.rect.height
        blocks = _page_blocks_in_reading_order(page)

        for blk in blocks:
            raw = blk["raw"]
            size = blk["size"]
            bbox = blk["bbox"]
            stripped = raw.strip()
            if not stripped:
                continue

            # Bỏ số trang / running header lặp lại (lọc theo VỊ TRÍ, không theo
            # danh sách chuỗi cố định của sách khác).
            if _is_running_header(stripped, bbox, page_height):
                continue

            text = clean_paragraph_text(raw)
            if not text:
                continue

            # Nhãn "CHAPTER N" (trùng với H1 sinh từ metadata) -> bỏ, đồng thời
            # bật chế độ thu thập mini mục lục đầu chương (nếu có).
            if CHAPTER_LABEL_RE.match(text):
                flush_paragraph()
                just_saw_chapter_label = True
                toc_collect_mode = True
                continue

            # Tiêu đề lớn của chương (trùng tiêu đề tiếng Anh trong metadata) -> bỏ.
            # Tiêu đề có thể trải trên NHIỀU khối (dòng dài bị ngắt) nên phải
            # tiếp tục nuốt mọi khối cỡ chữ lớn cho đến khi gặp khối nhỏ hơn.
            if _norm_key(text) == title_en_key or (just_saw_chapter_label and size >= 18):
                flush_paragraph()
                toc_collect_mode = True
                continue
            just_saw_chapter_label = False

            # Case study vignette đánh dấu bằng > ... << (một số chương có dùng).
            if stripped.startswith(">"):
                flush_paragraph()
                in_case_study = True
                cleaned = clean_paragraph_text(stripped.lstrip(">").strip())
                if "<<" in cleaned:
                    cleaned = cleaned.replace("<<", "").strip()
                    elements.append({"type": "case_study", "text": [cleaned]})
                    in_case_study = False
                else:
                    case_study_buf = [cleaned]
                continue

            if in_case_study:
                cleaned = clean_paragraph_text(stripped)
                if "<<" in cleaned:
                    cleaned = cleaned.replace("<<", "").strip()
                    case_study_buf.append(cleaned)
                    elements.append({"type": "case_study", "text": case_study_buf})
                    case_study_buf = []
                    in_case_study = False
                else:
                    case_study_buf.append(cleaned)
                continue

            # Chế độ thu thập mini mục lục ở đầu chương: các dòng ngắn, không
            # kết thúc bằng dấu câu, nằm giữa tiêu đề chương và tiêu đề mục thật
            # đầu tiên. Không đưa vào nội dung (tránh trùng lặp với sidebar TOC).
            if toc_collect_mode:
                if size >= 13:
                    toc_collect_mode = False
                    # rơi xuống xử lý như heading bên dưới
                elif len(text) < 90 and not ends_sentence(text):
                    continue
                else:
                    toc_collect_mode = False

            # Tiêu đề mục thật trong thân chương (kích thước chữ lớn hơn văn bản
            # thường). OCR thường thêm 1-2 ký tự rác trước tiêu đề (icon bị đọc
            # sai) -> tự loại bỏ tiền tố rác ngắn bằng regex. Một số trang có
            # sơ đồ phả hệ (genogram) với nhãn/tên rời rạc cũng bị OCR ra cỡ
            # chữ lớn -> lọc bằng _looks_like_real_heading để không biến chúng
            # thành tiêu đề giả.
            if size >= 13 and len(text) < 140:
                if _looks_like_real_heading(text):
                    flush_paragraph()
                    # Vài token rác cố định do OCR đọc sai icon đầu mục (thấy
                    # trong nhiều chương: Be/HM/MS/Hi/Ma) - cắt bỏ trước.
                    # Chỉ cắt các token rác CỐ ĐỊNH đã quan sát được (icon đầu
                    # mục bị OCR sai) - không dùng regex chung chung vì dễ cắt
                    # nhầm từ đầu tiên của tiêu đề thật (vd "Why I Became...",
                    # "A Bowen Therapist...").
                    heading_text = re.sub(r'^(?:Be|HM|MS|Hi|Ma|Ms|Mm|MH|MM|Me|DVD)\s*=?\s*(?=[A-Za-z])', '', text).strip()
                    if heading_text and heading_text[0].islower():
                        heading_text = heading_text[0].upper() + heading_text[1:]
                    if not heading_text:
                        heading_text = text
                    elements.append({"type": "heading_2", "text": heading_text})
                    continue
                elif len(text) < 30:
                    # Rất ngắn và không giống tiêu đề thật -> khả năng cao là
                    # nhãn rời rạc trong sơ đồ phả hệ, bỏ qua hoàn toàn.
                    continue
                # Còn lại: coi như văn bản thường, rơi xuống xử lý đoạn văn bên dưới.

            # Danh sách có dấu đầu dòng (bullet OCR ra 1 ký tự Latin-1 lạ) hoặc
            # đánh số "1. ...". Mỗi bullet luôn mở một mục mới, kể cả khi đoạn
            # văn trước đó chưa kết thúc bằng dấu câu (ví dụ sau dấu ":").
            is_bullet = bool(BULLET_RE.match(text))
            is_num = bool(NUM_LIST_RE.match(text))
            # Nếu đoạn đang gộp dở kết thúc bằng ":" thì khối tiếp theo gần như
            # chắc chắn là bullet đầu tiên của một danh sách (dù ký tự đầu dòng
            # của nó không rơi vào dải Latin-1 đặc biệt - OCR không ổn định).
            buf_ends_colon = bool(paragraph_buf) and paragraph_buf[-1].rstrip().endswith(':')
            is_list_continuation = buf_ends_colon and len(text) < 200
            if is_bullet or is_num or is_list_continuation:
                flush_paragraph()
                if is_bullet:
                    text = BULLET_RE.sub('', text)
                    if text:
                        text = text[0].upper() + text[1:]
                elif is_list_continuation and len(text) > 1 and not text[0].isupper():
                    # Bullet đầu tiên OCR ra một ký tự thường lẫn vào từ kế tiếp
                    # (không theo dải Latin-1 đặc biệt) -> cắt bỏ ký tự rác đó.
                    text = text[1:].lstrip()
                    if text:
                        text = text[0].upper() + text[1:]
                buf_type = "list_item"
            elif not paragraph_buf:
                buf_type = "paragraph"

            # Nếu đoạn văn đầu tiên của phần tử bắt đầu bằng chữ thường, nhiều
            # khả năng chữ hoa đầu dòng (drop cap) không có trong lớp OCR của
            # PDF quét -> không thể khôi phục ký tự đã mất, chỉ viết hoa lại
            # chữ cái hiện có để câu không mở đầu bằng chữ thường.
            if not paragraph_buf and text and text[0].islower():
                text = text[0].upper() + text[1:]
            # OCR hay đọc nhầm chữ "I" đứng đầu câu thành dấu ngoặc vuông "[".
            if not paragraph_buf and len(text) > 1 and text[0] == "[" and text[1].islower():
                text = "I" + text[1:]

            paragraph_buf.append(text)
            if ends_sentence(text):
                flush_paragraph()

    flush_paragraph()
    if in_case_study and case_study_buf:
        elements.append({"type": "case_study", "text": case_study_buf})

    return elements


def generate_chapter_html(meta, prev_meta, next_meta, translated_elements):
    """
    Sinh file HTML hoàn chỉnh cho một chương.
    """
    ch_num_label = meta["label"]
    title_vi = meta["title_vi"]
    title_en = meta["title_en"]

    content_html = []
    open_list = None  # 'ul' | 'ol' | None
    def close_list():
        nonlocal open_list
        if open_list:
            content_html.append(f'</{open_list}>')
            open_list = None

    for el in translated_elements:
        el_type = el["type"]
        if el_type != "list_item":
            close_list()

        if el_type == "heading_2":
            content_html.append(f'<h2>{el["vi"]}</h2>')
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
            if not open_list:
                open_list = "ul"
                content_html.append('<ul class="chapter-list">')
            content_html.append(f'<li>{el["vi"]}</li>')
        else:
            content_html.append(f'<p>{el["vi"]}</p>')

    close_list()
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
      <span class="book-badge">{BOOK_BADGE}</span>
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
    elements = extract_chapter_content(doc, meta)
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
            translated_elements.append({"type": el_type, "vi": vi_paras})
        else:
            t_vi = translate_chunk_google(el["text"])
            translated_elements.append({"type": el_type, "vi": t_vi})

        # Lưu cache thường xuyên
        if (idx + 1) % 20 == 0 or (idx + 1) == total:
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
          <strong>"Theory and Practice of Family Therapy and Counseling"</strong> (2009) của GS. James Robert Bitter là cẩm nang được sử dụng rộng rãi để đào tạo các nhà tham vấn, trị liệu gia đình và nhân viên công tác xã hội. Sách trình bày 10 mô hình lý thuyết trị liệu gia đình theo một cấu trúc thống nhất, minh họa xuyên suốt qua ca lâm sàng của gia đình Quest (Quest Family).
        </p>
        <p>
          Tài liệu này được trích xuất trực tiếp từ nguyên bản PDF và chuyển ngữ sang tiếng Việt học thuật, chuẩn hóa các khái niệm then chốt như: <em>biệt hóa bản thân, tam giác hóa, ranh giới, sơ đồ phả hệ (genogram), dàn dựng tương tác, tái đóng khung, câu hỏi phép màu</em>.
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
    parser = argparse.ArgumentParser(description="Chuyển ngữ sách Theory and Practice of Family Therapy and Counseling (Bitter, 2009) sang HTML")
    parser.add_argument("--preface", action="store_true", help="Dịch Lời nói đầu")
    parser.add_argument("--chapter", type=int, help="Dịch số chương chỉ định")
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
    elif args.build_index:
        pass
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
