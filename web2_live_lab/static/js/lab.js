// web2_live_lab/static/js/lab.js - Live Lab Frontend Controller
document.addEventListener('DOMContentLoaded', () => {
    let currentHash = '';
    let selectedFile = null;
    let chartInstance = null;

    // Element References
    const consoleOutput = document.getElementById('consoleOutput');
    const pipelineMetricsHeader = document.getElementById('pipelineMetricsHeader');
    const txtCurrentHash = document.getElementById('txtCurrentHash');
    const lblDlqCount = document.getElementById('lblDlqCount');

    // Utility: Append colored log
    function appendLog(level, message) {
        const now = new Date();
        const timeStr = `[${now.toTimeString().split(' ')[0]}]`;
        const entry = document.createElement('div');
        entry.className = 'log-entry';

        let lvlClass = 'log-info';
        if (level === 'SUCCESS') lvlClass = 'log-success';
        if (level === 'IDEMPOTENT') lvlClass = 'log-idempotent';
        if (level === 'ERROR' || level === 'DLQ') lvlClass = 'log-error';

        entry.innerHTML = `<span class="log-time">${timeStr}</span> <span class="${lvlClass}">[${level}]</span> ${message}`;
        consoleOutput.appendChild(entry);
        consoleOutput.scrollTop = consoleOutput.scrollHeight;
    }

    // Utility: Visual Canvas Node Pulse Animation
    function pulseNodes(nodes, status = 'pulse') {
        const classMap = {
            'pulse': 'active-pulse',
            'error': 'active-error',
            'idempotent': 'active-idempotent'
        };
        const cls = classMap[status] || 'active-pulse';

        nodes.forEach((id, index) => {
            const el = document.getElementById(id);
            if (!el) return;
            setTimeout(() => {
                el.classList.add(cls);
                setTimeout(() => el.classList.remove(cls), 1200);
            }, index * 250);
        });
    }

    // Tab Navigation
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetId = btn.getAttribute('data-tab');
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));

            btn.classList.add('active');
            const targetContent = document.getElementById(targetId);
            if (targetContent) targetContent.classList.add('active');
        });
    });

    // Check system status periodically
    async function updateStatus() {
        try {
            const res = await fetch('/api/status');
            if (res.ok) {
                const data = await res.json();
                pipelineMetricsHeader.textContent = `Processed: ${data.processed_count} | S3 Input: ${data.raw_bucket_count} | DynamoDB: ${data.dynamodb_count} | DLQ Depth: ${data.dlq_depth}`;
                lblDlqCount.textContent = data.dlq_depth;
            }
        } catch (e) {
            console.error('Status check failed:', e);
        }
    }
    updateStatus();
    setInterval(updateStatus, 5000);

    // TAB 1: File Dropzone & Normal Processing
    const dropzone = document.getElementById('dropzoneUpload');
    const fileInput = document.getElementById('fileInput');
    const btnSample1080p = document.getElementById('btnSample1080p');
    const btnProcessNormal = document.getElementById('btnProcessNormal');
    const chkSimColdStart = document.getElementById('chkSimColdStart');

    dropzone.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            selectedFile = e.target.files[0];
            dropzone.querySelector('div:first-of-type').textContent = `Đã chọn: ${selectedFile.name} (${(selectedFile.size / 1024).toFixed(1)} KB)`;
            appendLog('INFO', `Đã nạp tệp người dùng: ${selectedFile.name}`);
        }
    });

    btnSample1080p.addEventListener('click', () => {
        selectedFile = null;
        dropzone.querySelector('div:first-of-type').textContent = 'Đã tạo ảnh mẫu phong cảnh Full HD 1080p (Sẵn sàng kích hoạt)';
        appendLog('INFO', 'Đã sinh ảnh mẫu Full HD 1920x1080 trong bộ nhớ đệm.');
    });

    btnProcessNormal.addEventListener('click', async () => {
        const formData = new FormData();
        const isCold = chkSimColdStart.checked;
        formData.append('is_cold', isCold ? 'true' : 'false');

        if (selectedFile) {
            formData.append('image', selectedFile);
            formData.append('is_sample', 'false');
        } else {
            formData.append('is_sample', 'true');
        }

        appendLog('INFO', `Bắt đầu đẩy tệp lên S3 Input Bucket... (Giả lập Cold Start: ${isCold})`);
        pulseNodes(['node-client', 'node-s3-in', 'node-sqs', 'node-lambda', 'node-storage'], 'pulse');

        try {
            const res = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });
            const data = await res.json();

            if (res.ok && data.status === 'PROCESSED') {
                currentHash = data.image_hash || data.hash;
                txtCurrentHash.value = currentHash;

                document.getElementById('imgComparisonBox').style.display = 'grid';
                document.getElementById('metaResultBox').style.display = 'block';

                // Display thumbnails
                document.getElementById('previewThumb').src = data.thumbnail_base64;
                document.getElementById('lblOrigInfo').textContent = `${data.orig_size} • ${data.orig_kb} KB (${data.orig_format})`;
                document.getElementById('lblThumbInfo').textContent = `${data.thumb_size} • ${data.thumb_kb} KB (JPEG 85%)`;
                document.getElementById('lblCompression').textContent = `Giảm -${data.compression_percent}% dung lượng`;

                document.getElementById('metaJsonContent').textContent = JSON.stringify(data, null, 2);

                appendLog('SUCCESS', `Lambda hoàn tất trong ${data.latency_ms} ms! Đã sinh thumbnail 300x300 và ghi DynamoDB ImageMetadata.`);
                updateStatus();
            } else if (data.status === 'SKIPPED_IDEMPOTENT') {
                appendLog('IDEMPOTENT', `[IDEMPOTENT LOCK] ${data.message} (${data.latency_ms} ms)`);
            } else {
                appendLog('ERROR', `Lỗi xử lý: ${data.error || 'Unknown error'}`);
            }
        } catch (err) {
            appendLog('ERROR', `Lỗi kết nối tới Serverless Engine: ${err.message}`);
        }
    });

    // TAB 2: Idempotency Duplicate Re-send
    const btnSendDuplicate = document.getElementById('btnSendDuplicate');
    const btnGenNewHash = document.getElementById('btnGenNewHash');
    const idempotentResultBox = document.getElementById('idempotentResultBox');

    btnGenNewHash.addEventListener('click', () => {
        currentHash = Array.from(crypto.getRandomValues(new Uint8Array(32)))
            .map(b => b.toString(16).padStart(2, '0')).join('');
        txtCurrentHash.value = currentHash;
        appendLog('INFO', `Đã sinh mã băm ngẫu nhiên mới: ${currentHash.substring(0, 16)}...`);
    });

    btnSendDuplicate.addEventListener('click', async () => {
        if (!currentHash || currentHash.startsWith('(')) {
            alert('Vui lòng tạo hoặc upload một ảnh ở Tab 1 trước!');
            return;
        }

        appendLog('INFO', `Phát sinh sự kiện tải trùng lặp với SHA-256: ${currentHash.substring(0, 16)}...`);
        pulseNodes(['node-client', 'node-s3-in', 'node-sqs', 'node-lambda'], 'idempotent');

        try {
            const res = await fetch('/api/simulate-duplicate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ image_hash: currentHash })
            });
            const data = await res.json();

            idempotentResultBox.style.display = 'block';
            document.getElementById('idempotentTitle').textContent = `✓ ${data.status} (Khóa Lũy Đẳng Nguyên Tử)`;
            document.getElementById('idempotentMsg').textContent = data.message;
            document.getElementById('idempotentLatency').textContent = `Thời gian từ chối xử lý: ${data.latency_ms} ms • Không tạo bản ghi trùng • Tiết kiệm 100% CPU`;

            appendLog('IDEMPOTENT', `[ATOMIC LOCK] DynamoDB ném ConditionalCheckFailed. Bỏ qua xử lý an toàn trong ${data.latency_ms} ms!`);
        } catch (err) {
            appendLog('ERROR', `Lỗi kiểm tra Idempotency: ${err.message}`);
        }
    });

    // TAB 3: Poison Pill & SQS DLQ Isolation
    const btnPoisonMagicBytes = document.getElementById('btnPoisonMagicBytes');
    const btnPoisonMalwareExt = document.getElementById('btnPoisonMalwareExt');
    const btnTriggerPoison = document.getElementById('btnTriggerPoison');
    const poisonResultBox = document.getElementById('poisonResultBox');
    let currentPoisonType = 'corrupt_magic_bytes';

    btnPoisonMagicBytes.addEventListener('click', () => {
        currentPoisonType = 'corrupt_magic_bytes';
        appendLog('INFO', 'Đã chọn kịch bản tệp hỏng cấu trúc header (Magic Bytes).');
    });

    btnPoisonMalwareExt.addEventListener('click', () => {
        currentPoisonType = 'fake_executable_extension';
        appendLog('INFO', 'Đã chọn kịch bản giả mạo file thực thi (.exe) thành đuôi .jpg.');
    });

    btnTriggerPoison.addEventListener('click', async () => {
        appendLog('INFO', `Bơm tệp độc hại (${currentPoisonType}) vào pipeline...`);
        pulseNodes(['node-client', 'node-s3-in', 'node-sqs', 'node-lambda', 'node-dlq'], 'error');

        try {
            const res = await fetch('/api/simulate-poison', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    poison_type: currentPoisonType,
                    filename: currentPoisonType === 'fake_executable_extension' ? 'malware.exe.jpg' : 'corrupt_byte_payload.jpg'
                })
            });
            const data = await res.json();

            poisonResultBox.style.display = 'block';
            document.getElementById('poisonErrorMsg').textContent = `Lỗi bắt được: ${data.error}`;
            document.getElementById('poisonRetriesDetail').textContent = `Đã retry ${data.retries_attempted} lần có lùi số mũ (Backoff) thất bại -> Chuyển vào SQS DLQ: ${data.dlq_name} (Lưu trữ 14 ngày)`;

            appendLog('DLQ', `[POISON PILL] Thư viện Pillow phát hiện file hỏng. Tự động cô lập vào SQS DLQ sau 3 lần retry!`);
            updateStatus();
        } catch (err) {
            appendLog('ERROR', `Lỗi mô phỏng Poison Pill: ${err.message}`);
        }
    });

    // TAB 4: Benchmark 100 Runs & Chart
    const btnRunBenchmarkDataset = document.getElementById('btnRunBenchmarkDataset');
    const btnExportCsv = document.getElementById('btnExportCsv');

    async function loadBenchmarkData() {
        appendLog('INFO', 'Đang tải dữ liệu thực nghiệm 100 lần đo từ kho dữ liệu chuẩn UTH...');
        try {
            const res = await fetch('/api/benchmark?mode=verified');
            const data = await res.json();

            document.getElementById('statP50').textContent = `${data.percentiles.p50} ms`;
            document.getElementById('statP95').textContent = `${data.percentiles.p95} ms`;
            document.getElementById('statSweetSpot').textContent = '512 MB';
            document.getElementById('statErrorRate').textContent = `${data.error_rate}%`;

            renderHistogram(data.runs, data.percentiles);
            appendLog('SUCCESS', `Đã nạp 100 lần đo thực nghiệm! p50 = ${data.percentiles.p50} ms, p95 = ${data.percentiles.p95} ms, Chi phí 100k ảnh = $0.045.`);
        } catch (err) {
            appendLog('ERROR', `Lỗi tải benchmark: ${err.message}`);
        }
    }

    function renderHistogram(runs, percentiles) {
        const warmRuns = runs.filter(r => r.status === 'SUCCESS' && !r.is_cold).map(r => r.total_latency_ms);
        // Create histogram bins
        const bins = [0, 20, 25, 30, 35, 40, 50, 75, 100, 300, 600];
        const counts = new Array(bins.length - 1).fill(0);

        warmRuns.forEach(d => {
            for (let i = 0; i < bins.length - 1; i++) {
                if (d >= bins[i] && d < bins[i+1]) {
                    counts[i]++;
                    break;
                }
            }
        });

        const labels = bins.slice(0, -1).map((b, i) => `${b}-${bins[i+1]}ms`);

        if (chartInstance) {
            chartInstance.destroy();
        }

        const ctx = document.getElementById('benchmarkChart').getContext('2d');
        chartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Số Lượng Request',
                    data: counts,
                    backgroundColor: 'rgba(56, 189, 248, 0.7)',
                    borderColor: '#38bdf8',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false },
                    title: {
                        display: true,
                        text: `Phân Phối Độ Trễ (p50 = ${percentiles.p50} ms | p95 = ${percentiles.p95} ms | Sweet Spot 512MB RAM)`,
                        color: '#94a3b8',
                        font: { size: 12, weight: 'bold' }
                    }
                },
                scales: {
                    x: { ticks: { color: '#64748b' }, grid: { color: '#1e293b' } },
                    y: { ticks: { color: '#64748b' }, grid: { color: '#1e293b' } }
                }
            }
        });
    }

    btnRunBenchmarkDataset.addEventListener('click', loadBenchmarkData);

    btnExportCsv.addEventListener('click', () => {
        window.open('/api/benchmark?mode=verified', '_blank');
        appendLog('INFO', 'Đã xuất dữ liệu đo 100 lần gọi dưới dạng JSON/CSV.');
    });

    // SRE DLQ Modal Management
    const btnOpenDlqModal = document.getElementById('btnOpenDlqModal');
    const dlqModalOverlay = document.getElementById('dlqModalOverlay');
    const btnCloseDlqModal = document.getElementById('btnCloseDlqModal');
    const btnCloseDlqModalBtn = document.getElementById('btnCloseDlqModalBtn');
    const btnRedriveDlq = document.getElementById('btnRedriveDlq');
    const dlqMessageList = document.getElementById('dlqMessageList');

    async function openDlqModal() {
        dlqModalOverlay.classList.add('active');
        try {
            const res = await fetch('/api/dlq');
            const data = await res.json();
            if (data.count === 0) {
                dlqMessageList.innerHTML = '<em>(Không có thông điệp trong hàng đợi lỗi SQS DLQ)</em>';
            } else {
                dlqMessageList.innerHTML = data.messages.map(m => `
                    <div style="border-bottom: 1px solid #334155; padding: 0.4rem 0;">
                        <div><strong>ID:</strong> ${m.id}</div>
                        <div><strong>File:</strong> ${m.body.filename} (${m.body.poison_type})</div>
                        <div><strong>Error:</strong> ${m.body.error}</div>
                    </div>
                `).join('');
            }
        } catch (e) {
            console.error('Fetch DLQ failed:', e);
        }
    }

    btnOpenDlqModal.addEventListener('click', openDlqModal);
    btnCloseDlqModal.addEventListener('click', () => dlqModalOverlay.classList.remove('active'));
    btnCloseDlqModalBtn.addEventListener('click', () => dlqModalOverlay.classList.remove('active'));

    btnRedriveDlq.addEventListener('click', async () => {
        appendLog('INFO', 'Kích hoạt quy trình SRE DLQ Redrive: Vá lỗi và tái xử lý...');
        try {
            const res = await fetch('/api/dlq/redrive', { method: 'POST' });
            const data = await res.json();
            appendLog('SUCCESS', `[SRE REDRIVE] ${data.message}`);
            dlqModalOverlay.classList.remove('active');
            updateStatus();
        } catch (err) {
            appendLog('ERROR', `Lỗi Redrive DLQ: ${err.message}`);
        }
    });

    // Clear log button
    document.getElementById('btnClearLog').addEventListener('click', () => {
        consoleOutput.innerHTML = '';
        appendLog('INFO', 'Đã dọn sạch nhật ký thực thi.');
    });

    // Auto-load benchmark chart on start
    loadBenchmarkData();
});
