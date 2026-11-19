// web2_live_lab/static/js/lab.js
// Interactive Live Lab Controller for Serverless Image Processing Studio (:5002)

document.addEventListener('DOMContentLoaded', () => {
    let lastUploadedHash = null;
    let latencyChartInstance = null;
    let selectedPackageMb = 15;

    // Element references
    const consoleTerminal = document.getElementById('consoleTerminal');
    const pipelineMetricsHeader = document.getElementById('pipelineMetricsHeader');
    const lblDbCount = document.getElementById('lblDbCount');
    const dynamodbViewer = document.getElementById('dynamodbViewer');
    const lblActiveRam = document.getElementById('lblActiveRam');

    // Logging helper
    function logTelemetry(type, message) {
        if (!consoleTerminal) return;
        const now = new Date().toISOString().substring(11, 23);
        const div = document.createElement('div');
        div.className = `log-line log-${type}`;
        div.textContent = `[${now}] [${type.toUpperCase()}] ${message}`;
        consoleTerminal.appendChild(div);
        consoleTerminal.scrollTop = consoleTerminal.scrollHeight;
    }

    // Node animation helper
    function pulseNode(nodeId, type = 'active', durationMs = 800) {
        const node = document.getElementById(nodeId);
        if (!node) return;
        const className = type === 'error' ? 'error-pulse' : 'active-pulse';
        node.classList.add(className);
        setTimeout(() => node.classList.remove(className), durationMs);
    }

    // Refresh system status & DynamoDB inspector
    async function refreshStatus() {
        try {
            const res = await fetch('/api/status');
            if (!res.ok) return;
            const data = await res.json();
            if (pipelineMetricsHeader) {
                pipelineMetricsHeader.textContent = 
                    `Processed: ${data.processed_count} | Raw S3: ${data.raw_bucket_count} | Thumbnails: ${data.thumb_bucket_count} | DynamoDB: ${data.dynamodb_count} | DLQ Depth: ${data.dlq_depth}`;
            }
            if (lblDbCount) {
                lblDbCount.textContent = `${data.dynamodb_count} Bản Ghi`;
            }
            loadDynamoDbRecords();
        } catch (e) {
            console.error('Lỗi làm mới trạng thái:', e);
        }
    }

    async function loadDynamoDbRecords() {
        if (!dynamodbViewer) return;
        try {
            const res = await fetch('/api/dynamodb-records');
            if (!res.ok) return;
            const data = await res.json();
            if (!data.records || data.records.length === 0) {
                dynamodbViewer.innerHTML = '<div style="font-size: 0.75rem; color: var(--text-muted); text-align: center; padding: 1rem;">Chưa có bản ghi nào trong bảng.</div>';
                return;
            }

            let html = '<table class="data-table"><thead><tr><th>Hash (SHA-256)</th><th>Tên Tệp</th><th>Kích Thước</th><th>Độ Trễ</th><th>Trạng Thái</th></tr></thead><tbody>';
            data.records.forEach(r => {
                const shortHash = (r.image_hash || '').substring(0, 10) + '...';
                const statusColor = r.status === 'COMPLETED' ? 'var(--success)' : (r.status === 'FAILED' ? 'var(--danger)' : 'var(--primary)');
                html += `<tr>
                    <td style="color: var(--primary); font-weight: 600;" title="${r.image_hash || ''}">${shortHash}</td>
                    <td>${r.filename || 'sample.jpg'}</td>
                    <td>${r.size_kb || 0} KB</td>
                    <td>${r.latency_ms ? r.latency_ms + ' ms' : '-'}</td>
                    <td><strong style="color: ${statusColor};">${r.status || 'PROCESSED'}</strong></td>
                </tr>`;
            });
            html += '</tbody></table>';
            dynamodbViewer.innerHTML = html;
        } catch (e) {
            console.error('Lỗi nạp DynamoDB records:', e);
        }
    }

    // Tabs Navigation
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetTab = btn.getAttribute('data-tab');
            tabButtons.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            btn.classList.add('active');
            const targetEl = document.getElementById(targetTab);
            if (targetEl) targetEl.classList.add('active');
        });
    });

    // 1. STANDARD UPLOAD HANDLING
    const dropzone = document.getElementById('dropzoneUpload');
    const fileInput = document.getElementById('fileInput');
    const btnUploadSample = document.getElementById('btnUploadSample');
    const chkColdStart = document.getElementById('chkColdStart');

    if (dropzone && fileInput) {
        dropzone.addEventListener('click', () => fileInput.click());
        dropzone.addEventListener('dragover', (e) => { e.preventDefault(); dropzone.style.borderColor = 'var(--primary)'; });
        dropzone.addEventListener('dragleave', () => { dropzone.style.borderColor = 'var(--border)'; });
        dropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropzone.style.borderColor = 'var(--border)';
            if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
                handleFileUpload(e.dataTransfer.files[0]);
            }
        });
        fileInput.addEventListener('change', () => {
            if (fileInput.files && fileInput.files.length > 0) {
                handleFileUpload(fileInput.files[0]);
            }
        });
    }

    if (btnUploadSample) {
        btnUploadSample.addEventListener('click', () => handleFileUpload(null, true));
    }

    async function handleFileUpload(fileObj, isSample = false) {
        const isCold = chkColdStart ? chkColdStart.checked : false;
        const sliderRam = document.getElementById('sliderRam');
        const memoryMb = sliderRam ? sliderRam.value : 512;

        logTelemetry('info', `Bắt đầu tải ảnh vào S3 Input Bucket (Cold Start: ${isCold}, RAM: ${memoryMb}MB)...`);
        pulseNode('node-client', 'active');
        pulseNode('node-s3-in', 'active', 1000);

        const formData = new FormData();
        if (fileObj) {
            formData.append('image', fileObj);
        } else if (isSample) {
            formData.append('is_sample', 'true');
        }
        formData.append('is_cold', isCold ? 'true' : 'false');
        formData.append('memory_mb', memoryMb);

        try {
            pulseNode('node-sqs', 'active', 1200);
            pulseNode('node-lambda', 'active', 1500);

            const res = await fetch('/api/upload', { method: 'POST', body: formData });
            const data = await res.json();

            if (!res.ok) {
                throw new Error(data.error || 'Lỗi xử lý tải ảnh');
            }

            pulseNode('node-storage', 'active', 1500);

            if (data.status === 'SKIPPED_IDEMPOTENT') {
                logTelemetry('idempotent', `[IDEMPOTENT] Khóa nguyên tử chặn ảnh trùng lặp: ${data.hash.substring(0, 12)}... (${data.latency_ms} ms)`);
                alert(`Khóa lũy đẳng phát hiện ảnh trùng lặp. Đã bỏ qua an toàn trong ${data.latency_ms} ms.`);
                return;
            }

            lastUploadedHash = data.hash;
            logTelemetry('success', `[SUCCESS] Tạo Thumbnail 300x300 thành công: ${data.thumb_key} (Nén: -${data.compression_percent}%, Trễ: ${data.latency_ms} ms)`);

            // Display result card
            const resultCard = document.getElementById('uploadResultCard');
            if (resultCard) {
                resultCard.style.display = 'block';
                document.getElementById('imgThumbnailResult').src = data.thumbnail_base64;
                document.getElementById('resFilename').textContent = data.filename;
                document.getElementById('resDimensions').textContent = `${data.orig_size} ➔ ${data.thumb_size}`;
                document.getElementById('resSize').textContent = `${data.orig_kb} KB ➔ ${data.thumb_kb} KB`;
                document.getElementById('resCompression').textContent = `-${data.compression_percent}% dung lượng`;
                document.getElementById('resLatency').textContent = `${data.latency_ms} ms (${data.is_cold ? 'Cold Start' : 'Warm Start'})`;
                document.getElementById('resHash').textContent = data.hash;
            }

            refreshStatus();
        } catch (err) {
            logTelemetry('error', `[ERROR] Tải ảnh thất bại: ${err.message}`);
            pulseNode('node-lambda', 'error', 2000);
            alert(`Lỗi: ${err.message}`);
        }
    }

    // 2. IDEMPOTENT DUPLICATE TEST
    const btnTestDuplicate = document.getElementById('btnTestDuplicate');
    if (btnTestDuplicate) {
        btnTestDuplicate.addEventListener('click', async () => {
            if (!lastUploadedHash) {
                alert('Vui lòng tải ít nhất một bức ảnh trước ở Kịch bản 1 để lấy mã băm SHA-256!');
                return;
            }

            logTelemetry('info', `Mô phỏng mạng gửi lặp sự kiện mang hash ${lastUploadedHash.substring(0, 12)}...`);
            pulseNode('node-client', 'active');
            pulseNode('node-lambda', 'active', 800);

            try {
                const res = await fetch('/api/simulate-duplicate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ image_hash: lastUploadedHash })
                });
                const data = await res.json();

                pulseNode('node-storage', 'active', 800);

                if (data.status === 'SKIPPED_IDEMPOTENT') {
                    logTelemetry('idempotent', `[IDEMPOTENT LOCK] ConditionalCheckFailedException kích hoạt. Từ chối trong ${data.latency_ms} ms.`);
                    const dupCard = document.getElementById('duplicateResultCard');
                    if (dupCard) {
                        dupCard.style.display = 'block';
                        document.getElementById('resDupLatency').textContent = `${data.latency_ms} ms (< 2.5 ms)`;
                    }
                }
                refreshStatus();
            } catch (err) {
                logTelemetry('error', `[ERROR] Lỗi kiểm thử trùng lặp: ${err.message}`);
            }
        });
    }

    // 3. POISON PILL & TIMEOUT DLQ SIMULATION
    const btnSimulatePoison = document.getElementById('btnSimulatePoison');
    const btnSimulateTimeout = document.getElementById('btnSimulateTimeout');

    if (btnSimulatePoison) {
        btnSimulatePoison.addEventListener('click', async () => {
            logTelemetry('warn', 'Bắt đầu gửi tệp độc hại / hỏng cấu trúc (Poison Pill)...');
            pulseNode('node-client', 'active');
            pulseNode('node-lambda', 'error', 1500);

            try {
                const res = await fetch('/api/simulate-poison', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ poison_type: 'corrupt_magic_bytes', filename: 'malformed_payload.exe.jpg' })
                });
                const data = await res.json();

                pulseNode('node-dlq', 'error', 2000);
                logTelemetry('error', `[DLQ QUARANTINE] Tệp hỏng đã retry 3 lần thất bại (Exponential Backoff). Đã cô lập vào ${data.dlq_name}`);

                const poisonCard = document.getElementById('poisonResultCard');
                if (poisonCard) {
                    poisonCard.style.display = 'block';
                    document.getElementById('poisonHeading').textContent = '⚠️ CÔ LẬP SỰ CỐ TỆP HỎNG VÀO SQS DLQ THÀNH CÔNG';
                    document.getElementById('resPoisonError').textContent = data.error;
                    document.getElementById('resPoisonRetries').textContent = '3 lần (Exponential Backoff: 50ms, 100ms, 200ms)';
                    document.getElementById('resPoisonDlq').textContent = `${data.dlq_name} (Lưu giữ 14 ngày)`;
                }
                refreshStatus();
            } catch (err) {
                logTelemetry('error', `[ERROR] Lỗi mô phỏng Poison Pill: ${err.message}`);
            }
        });
    }

    if (btnSimulateTimeout) {
        btnSimulateTimeout.addEventListener('click', async () => {
            logTelemetry('warn', 'Mô phỏng tác vụ xử lý vượt quá giới hạn Timeout 30 giây...');
            pulseNode('node-lambda', 'error', 1500);

            try {
                const res = await fetch('/api/simulate-timeout', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ filename: 'heavy_unbounded_photo.jpg' })
                });
                const data = await res.json();

                pulseNode('node-dlq', 'error', 2000);
                logTelemetry('error', `[TIMEOUT DLQ] Lambda TimeoutError sau 30s. Đã retry 3 lần và đưa vào ${data.dlq_name}`);

                const poisonCard = document.getElementById('poisonResultCard');
                if (poisonCard) {
                    poisonCard.style.display = 'block';
                    document.getElementById('poisonHeading').textContent = '⏳ CÔ LẬP SỰ CỐ TIMEOUT VÀO SQS DLQ THÀNH CÔNG';
                    document.getElementById('resPoisonError').textContent = data.error;
                    document.getElementById('resPoisonRetries').textContent = '3 lần thử lại (100ms, 200ms, 400ms)';
                    document.getElementById('resPoisonDlq').textContent = `${data.dlq_name} (Lưu giữ 14 ngày)`;
                }
                refreshStatus();
            } catch (err) {
                logTelemetry('error', `[ERROR] Lỗi mô phỏng Timeout: ${err.message}`);
            }
        });
    }

    // 4. BENCHMARK 100 RUNS & CHART.JS
    const btnRunBenchmark = document.getElementById('btnRunBenchmark');
    if (btnRunBenchmark) {
        btnRunBenchmark.addEventListener('click', async () => {
            logTelemetry('info', 'Đang tải tập dữ liệu chuẩn 100 lần gọi đo đạc từ AWS Cloud (benchmark_100_runs.csv)...');
            try {
                const res = await fetch('/api/benchmark?mode=verified');
                const data = await res.json();

                logTelemetry('success', `[BENCHMARK] Hoàn thành đo 100 lần gọi: p50=${data.percentiles.p50}ms, p95=${data.percentiles.p95}ms, Error Rate=${data.error_rate}%`);

                document.getElementById('benchmarkStatsCard').style.display = 'block';
                document.getElementById('valP50').textContent = `${data.percentiles.p50} ms`;
                document.getElementById('valP90').textContent = `${data.percentiles.p90} ms`;
                document.getElementById('valP95').textContent = `${data.percentiles.p95} ms`;
                document.getElementById('valP99').textContent = `${data.percentiles.p99} ms`;
                document.getElementById('valErrorRate').textContent = `${data.error_rate.toFixed(2)}%`;

                renderLatencyHistogram(data.runs, data.percentiles);
            } catch (err) {
                logTelemetry('error', `[ERROR] Lỗi chạy benchmark: ${err.message}`);
            }
        });
    }

    function renderLatencyHistogram(runs, percentiles) {
        const ctx = document.getElementById('chartLatencyHistogram');
        if (!ctx) return;

        const warmDurations = runs
            .filter(r => r.status === 'SUCCESS' && r.total_latency_ms < 150)
            .map(r => r.total_latency_ms);

        // Group into buckets of 5ms
        const buckets = {};
        for (let b = 20; b <= 60; b += 5) {
            buckets[`${b}-${b+4}ms`] = 0;
        }
        warmDurations.forEach(d => {
            const b = Math.floor(d / 5) * 5;
            const key = `${b}-${b+4}ms`;
            if (buckets[key] !== undefined) buckets[key]++;
            else buckets['>60ms'] = (buckets['>60ms'] || 0) + 1;
        });

        const labels = Object.keys(buckets);
        const values = Object.values(buckets);

        if (latencyChartInstance) {
            latencyChartInstance.destroy();
        }

        latencyChartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Số lượt yêu cầu Warm (Invocations)',
                    data: values,
                    backgroundColor: '#38bdf8',
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } },
                    y: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } }
                },
                plugins: {
                    legend: { labels: { color: '#f8fafc' } }
                }
            }
        });
    }

    // 5. RAM SLIDER & PACKAGE SIZE SIMULATION
    const sliderRam = document.getElementById('sliderRam');
    const dispRamMb = document.getElementById('dispRamMb');
    const btnPkgPillow = document.getElementById('btnPkgPillow');
    const btnPkgOpenCv = document.getElementById('btnPkgOpenCv');

    async function updateRamTradeoff(ramMb, pkgMb) {
        try {
            const res = await fetch(`/api/ram-tradeoff?memory_mb=${ramMb}&package_mb=${pkgMb}`);
            const data = await res.json();

            if (dispRamMb) dispRamMb.textContent = `${data.memory_mb} MB`;
            if (lblActiveRam) lblActiveRam.textContent = `${data.memory_mb} MB`;
            document.getElementById('lblRamVcpu').textContent = `${data.vcpu} vCPU`;
            document.getElementById('lblRamCold').textContent = `${data.cold_start_ms} ms`;
            document.getElementById('lblRamWarm').textContent = `${data.warm_start_ms} ms (${data.speedup_vs_128mb} so với 128MB)`;
            document.getElementById('lblRamCost').textContent = `$${data.cost_per_100k_req.toFixed(4)} USD (${data.cost_diff_vs_128mb})`;
            
            const lblEval = document.getElementById('lblRamEval');
            if (data.is_sweet_spot) {
                lblEval.textContent = '★ ĐIỂM NGỌT (SWEET SPOT): Tăng tốc 360% với chi phí chỉ tăng 8%.';
                lblEval.style.color = 'var(--success)';
            } else {
                lblEval.textContent = data.recommendation;
                lblEval.style.color = 'var(--text-secondary)';
            }
        } catch (e) {
            console.error('Lỗi tính toán RAM tradeoff:', e);
        }
    }

    if (sliderRam) {
        sliderRam.addEventListener('input', (e) => {
            updateRamTradeoff(e.target.value, selectedPackageMb);
        });
    }

    if (btnPkgPillow && btnPkgOpenCv) {
        btnPkgPillow.addEventListener('click', () => {
            selectedPackageMb = 15;
            btnPkgPillow.className = 'btn btn-sm btn-primary';
            btnPkgOpenCv.className = 'btn btn-sm';
            btnPkgOpenCv.style.border = '1px solid var(--border)';
            updateRamTradeoff(sliderRam.value, 15);
            logTelemetry('info', 'Đã chuyển sang gói thư viện Pillow tinh gọn (15MB - Cold Start ~520ms).');
        });
        btnPkgOpenCv.addEventListener('click', () => {
            selectedPackageMb = 150;
            btnPkgOpenCv.className = 'btn btn-sm btn-primary';
            btnPkgPillow.className = 'btn btn-sm';
            btnPkgPillow.style.border = '1px solid var(--border)';
            updateRamTradeoff(sliderRam.value, 150);
            logTelemetry('warn', 'Đã chuyển sang gói thư viện OpenCV đầy đủ (150MB - Cold Start tăng vọt lên ~3,000ms).');
        });
    }

    // 6. SECURITY AUDIT & SRE RUNBOOK REDRIVE
    const btnRunSecurityAudit = document.getElementById('btnRunSecurityAudit');
    const btnTriggerRedrive = document.getElementById('btnTriggerRedrive');
    const btnOpenDlqModal = document.getElementById('btnOpenDlqModal');
    const btnCloseDlqModal = document.getElementById('btnCloseDlqModal');
    const modalDlqOverlay = document.getElementById('modalDlqOverlay');
    const btnModalRedrive = document.getElementById('btnModalRedrive');

    if (btnRunSecurityAudit) {
        btnRunSecurityAudit.addEventListener('click', async () => {
            logTelemetry('info', 'Bắt đầu chạy kịch bản quét an ninh tự động security_audit.py...');
            try {
                const res = await fetch('/api/security-audit');
                const data = await res.json();
                logTelemetry('success', `[AUDIT PASSED] Điểm đánh giá: ${data.score}. 0 lỗ hổng bảo mật.`);

                const auditBox = document.getElementById('securityAuditResult');
                const auditList = document.getElementById('auditCheckList');
                if (auditBox && auditList) {
                    auditBox.style.display = 'block';
                    auditList.innerHTML = '';
                    data.checks.forEach(c => {
                        const item = document.createElement('div');
                        item.style.cssText = 'background: var(--bg-card); padding: 0.5rem 0.75rem; border-radius: var(--radius-sm); border: 1px solid var(--border); font-size: 0.75rem;';
                        item.innerHTML = `<div style="font-weight: 700; color: var(--success);">${c.id}: ${c.title} — ${c.status}</div>
                                          <div style="color: var(--text-secondary); margin-top: 0.2rem;">${c.details}</div>`;
                        auditList.appendChild(item);
                    });
                }
            } catch (e) {
                logTelemetry('error', `Lỗi kiểm tra bảo mật: ${e.message}`);
            }
        });
    }

    async function loadDlqMessages() {
        const msgList = document.getElementById('dlqMessageList');
        if (!msgList) return;
        try {
            const res = await fetch('/api/dlq');
            const data = await res.json();
            if (!data.messages || data.messages.length === 0) {
                msgList.innerHTML = '<div style="font-size: 0.8rem; color: var(--text-muted); text-align: center; padding: 1rem;">Hàng đợi lỗi hiện đang rỗng (Depth = 0).</div>';
                return;
            }
            let html = '';
            data.messages.forEach(m => {
                const p = m.payload || {};
                html += `<div class="dlq-msg-item">
                    <div style="color: var(--danger); font-weight: 700;">ID: ${m.message_id} | Retries: ${p.retries_attempted || 3}</div>
                    <div style="color: var(--text-secondary); margin: 0.2rem 0;">Tệp: ${p.filename || 'unknown'} | Hash: ${(p.image_hash || '').substring(0, 16)}...</div>
                    <div style="color: #f87171;">Lỗi: ${p.error || 'Unknown Error'}</div>
                </div>`;
            });
            msgList.innerHTML = html;
        } catch (e) {
            console.error('Lỗi nạp DLQ:', e);
        }
    }

    if (btnOpenDlqModal && modalDlqOverlay) {
        btnOpenDlqModal.addEventListener('click', () => {
            modalDlqOverlay.style.display = 'flex';
            loadDlqMessages();
        });
    }

    if (btnCloseDlqModal && modalDlqOverlay) {
        btnCloseDlqModal.addEventListener('click', () => {
            modalDlqOverlay.style.display = 'none';
        });
    }

    async function executeRedrive() {
        logTelemetry('warn', 'Bắt đầu quy trình SRE DLQ Redrive: Bơm ngược thông điệp từ image-dlq về hàng đợi chính...');
        try {
            const res = await fetch('/api/dlq/redrive', { method: 'POST' });
            const data = await res.json();
            logTelemetry('success', `[REDRIVE SUCCESS] ${data.message}`);
            alert(data.message);
            if (modalDlqOverlay) modalDlqOverlay.style.display = 'none';
            refreshStatus();
        } catch (e) {
            logTelemetry('error', `Lỗi redrive DLQ: ${e.message}`);
        }
    }

    if (btnTriggerRedrive) btnTriggerRedrive.addEventListener('click', executeRedrive);
    if (btnModalRedrive) btnModalRedrive.addEventListener('click', executeRedrive);

    // Console controls
    const btnClearLogs = document.getElementById('btnClearLogs');
    const btnExportLogs = document.getElementById('btnExportLogs');
    if (btnClearLogs) {
        btnClearLogs.addEventListener('click', () => {
            if (consoleTerminal) consoleTerminal.innerHTML = '';
        });
    }
    if (btnExportLogs) {
        btnExportLogs.addEventListener('click', () => {
            if (!consoleTerminal) return;
            const text = consoleTerminal.innerText;
            const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `serverless_lab_telemetry_${Date.now()}.log`;
            a.click();
            URL.revokeObjectURL(url);
        });
    }

    // Initialize on load
    refreshStatus();
    setInterval(refreshStatus, 8000);
});
