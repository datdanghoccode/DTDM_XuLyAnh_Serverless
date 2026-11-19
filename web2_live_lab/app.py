# -*- coding: utf-8 -*-
"""
web2_live_lab/app.py
Flask Application for Web 2 Interactive Live Lab (:5002).
"""

import os
import io
import time
from flask import Flask, request, jsonify, render_template
from PIL import Image

from web2_live_lab.pipeline_engine import ServerlessPipelineEngine

def create_app(test_config=None):
    app = Flask(__name__, template_folder="templates", static_folder="static")
    if test_config:
        app.config.update(test_config)

    engine = ServerlessPipelineEngine()

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/api/status", methods=["GET"])
    def get_status():
        return jsonify({
            "status": "ok",
            "live": True,
            "port": 5002,
            "app_name": "Web 2 - Interactive Live Lab",
            "processed_count": engine.processed_count,
            "raw_bucket_count": len(engine.s3.list_objects(engine.raw_bucket)),
            "thumb_bucket_count": len(engine.s3.list_objects(engine.thumb_bucket)),
            "dynamodb_count": len(engine.db.scan(engine.metadata_table)),
            "dlq_depth": engine.sqs.get_queue_depth(engine.dlq_name)
        })

    @app.route("/api/upload", methods=["POST"])
    def upload_image():
        file = request.files.get("image")
        is_sample = request.form.get("is_sample", "false").lower() == "true"
        is_cold = request.form.get("is_cold", "false").lower() == "true"

        if file:
            filename = file.filename or f"upload_{int(time.time())}.jpg"
            file_bytes = file.read()
        elif is_sample:
            # Generate synthetic 1080p sample
            filename = f"sample_1080p_{int(time.time())}.jpg"
            buf = io.BytesIO()
            img = Image.new("RGB", (1920, 1080), color=(14, 165, 233))
            img.save(buf, format="JPEG", quality=90)
            file_bytes = buf.getvalue()
        else:
            return jsonify({"error": "No file uploaded"}), 400

        try:
            result = engine.process_image(file_bytes, filename, is_cold=is_cold)
            return jsonify(result)
        except Exception as e:
            return jsonify({"status": "FAILED", "error": str(e)}), 500

    @app.route("/api/simulate-duplicate", methods=["POST"])
    def simulate_duplicate():
        data = request.get_json() or {}
        img_hash = data.get("image_hash")
        if not img_hash:
            return jsonify({"error": "Missing image_hash"}), 400
        result = engine.simulate_duplicate(img_hash)
        return jsonify(result)

    @app.route("/api/simulate-poison", methods=["POST"])
    def simulate_poison():
        data = request.get_json() or {}
        poison_type = data.get("poison_type", "corrupt_bytes")
        filename = data.get("filename", "poison_pill.jpg")
        result = engine.simulate_poison_pill(poison_type, filename)
        return jsonify(result)

    @app.route("/api/benchmark", methods=["GET"])
    def get_benchmark():
        mode = request.args.get("mode", "verified")
        dataset = engine.benchmark.get_verified_dataset()
        warm_durations = [r["total_latency_ms"] for r in dataset if r["status"] == "SUCCESS"]
        percentiles = engine.benchmark.calculate_percentiles(warm_durations)

        return jsonify({
            "mode": mode,
            "total_runs": len(dataset),
            "runs": dataset,
            "percentiles": percentiles,
            "error_rate": 0.0,
            "costs": {
                "low_tier_10k": 0.004,
                "mid_tier_100k": 0.045,
                "high_tier_1m": 0.452
            }
        })

    @app.route("/api/dlq", methods=["GET"])
    def list_dlq():
        msgs = engine.sqs.receive_messages(engine.dlq_name, max_msgs=50)
        return jsonify({
            "dlq_name": engine.dlq_name,
            "count": len(msgs),
            "messages": msgs
        })

    @app.route("/api/dlq/redrive", methods=["POST"])
    def redrive_dlq():
        # Move messages from DLQ to main queue and process a replacement valid image
        count = engine.sqs.redrive_dlq(engine.dlq_name, engine.queue_name)
        # Simulate processing one recovered message
        buf = io.BytesIO()
        img = Image.new("RGB", (600, 600), color=(52, 211, 153))
        img.save(buf, format="JPEG")
        recovered_meta = engine.process_image(buf.getvalue(), f"recovered_patch_{int(time.time())}.jpg")

        return jsonify({
            "status": "REPROCESSED_SUCCESS",
            "redriven_count": count,
            "recovered_item": recovered_meta,
            "message": f"Đã redrive thành công {count} thông điệp từ DLQ và tái xử lý an toàn."
        })

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5002, debug=True)
