// web1_learning_hub/static/js/walkthrough.js
// Interactive Code Walkthrough Controller for Web 1 Knowledge Hub

document.addEventListener('DOMContentLoaded', () => {
    const stepButtons = document.querySelectorAll('.step-btn');
    const lblSnippetFile = document.getElementById('lblSnippetFile');
    const lblSnippetLang = document.getElementById('lblSnippetLang');
    const codePreViewer = document.getElementById('codePreViewer');
    const codeAnnotation = document.getElementById('codeAnnotation');

    async function loadSnippet(snippetId, targetBtn) {
        if (!codePreViewer) return;

        codePreViewer.textContent = '// Đang tải mã nguồn từ máy chủ...';
        if (codeAnnotation) {
            codeAnnotation.textContent = 'Đang đồng bộ phân tích kỹ thuật...';
        }

        try {
            const res = await fetch(`/api/code/${snippetId}`);
            if (!res.ok) {
                throw new Error(`Mã lỗi HTTP: ${res.status}`);
            }
            const data = await res.json();

            if (lblSnippetFile) lblSnippetFile.textContent = data.file || 'source_code';
            if (lblSnippetLang) {
                const lang = (data.language || 'text').toUpperCase();
                lblSnippetLang.textContent = `${lang} • ${data.title || ''}`;
            }
            if (codePreViewer) {
                codePreViewer.textContent = data.code || '// Không có nội dung';
            }
            if (codeAnnotation) {
                codeAnnotation.innerHTML = `<strong>${escapeHtml(data.title)}:</strong> ${escapeHtml(data.description)}`;
            }

            // Update active state on buttons
            stepButtons.forEach(btn => btn.classList.remove('active'));
            if (targetBtn) {
                targetBtn.classList.add('active');
            }
        } catch (err) {
            console.error('Lỗi khi nạp snippet:', err);
            if (codePreViewer) {
                codePreViewer.textContent = `// Lỗi tải mã nguồn: ${err.message}`;
            }
            if (codeAnnotation) {
                codeAnnotation.textContent = 'Không thể kết nối đến máy chủ API Web 1 (:5001).';
            }
        }
    }

    function escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    stepButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const snippetId = btn.getAttribute('data-snippet');
            if (snippetId) {
                loadSnippet(snippetId, btn);
            }
        });
    });

    // Auto load first snippet on initial page load
    const activeBtn = document.querySelector('.step-btn.active') || stepButtons[0];
    if (activeBtn) {
        const initialSnippet = activeBtn.getAttribute('data-snippet') || 'idempotency_lock';
        loadSnippet(initialSnippet, activeBtn);
    }
});
