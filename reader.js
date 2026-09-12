/**
 * E-Book Reader JavaScript
 * Quản lý giao diện, đổi theme, phóng to/thu nhỏ font, tìm kiếm mục lục
 */

(function () {
  // 1. Khởi tạo Theme
  const savedTheme = localStorage.getItem("reader_theme") || "light";
  document.documentElement.setAttribute("data-theme", savedTheme);

  // 2. Khởi tạo Cỡ chữ
  const savedFontSize = parseInt(localStorage.getItem("reader_font_size")) || 18;
  document.documentElement.style.setProperty("--font-size-base", savedFontSize + "px");

  window.addEventListener("DOMContentLoaded", () => {
    // Theme toggle button
    const themeBtn = document.getElementById("btn-theme");
    if (themeBtn) {
      updateThemeButtonLabel(themeBtn, savedTheme);
      themeBtn.addEventListener("click", () => {
        const currentTheme = document.documentElement.getAttribute("data-theme") || "light";
        let nextTheme = "light";
        if (currentTheme === "light") nextTheme = "sepia";
        else if (currentTheme === "sepia") nextTheme = "dark";
        else nextTheme = "light";

        document.documentElement.setAttribute("data-theme", nextTheme);
        localStorage.setItem("reader_theme", nextTheme);
        updateThemeButtonLabel(themeBtn, nextTheme);
      });
    }

    // Font size buttons
    const btnFontInc = document.getElementById("btn-font-inc");
    const btnFontDec = document.getElementById("btn-font-dec");

    if (btnFontInc && btnFontDec) {
      btnFontInc.addEventListener("click", () => {
        let size = parseInt(getComputedStyle(document.documentElement).getPropertyValue("--font-size-base")) || 18;
        if (size < 28) {
          size += 1;
          document.documentElement.style.setProperty("--font-size-base", size + "px");
          localStorage.setItem("reader_font_size", size);
        }
      });

      btnFontDec.addEventListener("click", () => {
        let size = parseInt(getComputedStyle(document.documentElement).getPropertyValue("--font-size-base")) || 18;
        if (size > 14) {
          size -= 1;
          document.documentElement.style.setProperty("--font-size-base", size + "px");
          localStorage.setItem("reader_font_size", size);
        }
      });
    }

    // Sidebar Toggle
    const toggleSidebarBtn = document.getElementById("btn-toggle-sidebar");
    const sidebar = document.querySelector(".sidebar");
    const mainWrapper = document.querySelector(".main-wrapper");

    if (toggleSidebarBtn && sidebar) {
      toggleSidebarBtn.addEventListener("click", () => {
        if (window.innerWidth <= 900) {
          sidebar.classList.toggle("open");
        } else {
          sidebar.classList.toggle("closed");
          if (mainWrapper) {
            mainWrapper.classList.toggle("full-width");
          }
        }
      });
    }

    // Search TOC
    const searchInput = document.getElementById("toc-search-input");
    if (searchInput) {
      searchInput.addEventListener("input", (e) => {
        const term = e.target.value.toLowerCase().trim();
        const items = document.querySelectorAll(".toc-item");
        items.forEach((item) => {
          const text = item.textContent.toLowerCase();
          if (text.includes(term)) {
            item.style.display = "";
          } else {
            item.style.display = "none";
          }
        });
      });
    }

    // Print button
    const printBtn = document.getElementById("btn-print");
    if (printBtn) {
      printBtn.addEventListener("click", () => {
        window.print();
      });
    }

    // Back to top button
    const backToTopBtn = document.getElementById("btn-back-to-top");
    if (backToTopBtn) {
      window.addEventListener("scroll", () => {
        if (window.scrollY > 400) {
          backToTopBtn.style.display = "flex";
        } else {
          backToTopBtn.style.display = "none";
        }
      });

      backToTopBtn.addEventListener("click", () => {
        window.scrollTo({ top: 0, behavior: "smooth" });
      });
    }
  });

  function updateThemeButtonLabel(btn, theme) {
    if (theme === "dark") {
      btn.innerHTML = `<span>🌙 Tối</span>`;
    } else if (theme === "sepia") {
      btn.innerHTML = `<span>📜 Giấy cũ</span>`;
    } else {
      btn.innerHTML = `<span>☀️ Sáng</span>`;
    }
  }
})();

