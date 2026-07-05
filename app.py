import os
import uuid
import socket
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 配置文件保存目录
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)


def get_local_ip():
    """自动获取本机局域网IP"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        try:
            hostname = socket.gethostname()
            return socket.gethostbyname(hostname)
        except Exception:
            return '127.0.0.1'


def get_public_url():
    """
    获取对外可访问的URL地址
    优先使用环境变量 PUBLIC_HOST（可在Dify中配置）
    Render 部署时使用 RENDER_EXTERNAL_HOSTNAME
    """
    env_host = os.environ.get('PUBLIC_HOST', '').strip()
    if env_host:
        return env_host
    render_host = os.environ.get('RENDER_EXTERNAL_HOSTNAME', '').strip()
    if render_host:
        return render_host
    return get_local_ip()


# 获取本机IP和对外地址
LOCAL_IP = get_local_ip()
PUBLIC_HOST = get_public_url()
print(f"📁 文件保存目录：{DATA_DIR}")
print(f"🌐 本机IP地址：{LOCAL_IP}")
print(f"🔗 对外访问地址：{PUBLIC_HOST}")


@app.route('/generate', methods=['POST', 'OPTIONS'])
def generate_html_report():
    """接收 Dify 发送的 HTML 内容，保存并返回访问链接"""
    # 处理 OPTIONS 预检请求（CORS）
    if request.method == 'OPTIONS':
        response = jsonify({"status": "ok"})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response

    try:
        data = request.get_json()
        print(f"📥 收到请求数据: {data.keys() if data else 'None'}")

        if not data:
            return jsonify({"error": "没有收到数据"}), 400

        html_content = data.get('html_content', '')

        if not html_content:
            return jsonify({"error": "没有收到 HTML 内容"}), 400

        print(f"📄 HTML内容长度: {len(html_content)} 字符")

        # 生成唯一文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_name = f"report_{timestamp}_{uuid.uuid4().hex[:6]}.html"
        file_path = os.path.join(DATA_DIR, file_name)

        # 保存 HTML 文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"✅ 文件已保存: {file_path}")

        # 🔥 生成访问链接 - 使用对外可访问的地址
        if 'render.com' in PUBLIC_HOST:
            preview_url = f"https://{PUBLIC_HOST}/view/{file_name}"
        else:
            preview_url = f"http://{PUBLIC_HOST}:5000/view/{file_name}"

        response = jsonify({
            "success": True,
            "message": "报告生成成功",
            "url": preview_url,
            "file_name": file_name,
            "local_ip": LOCAL_IP,
            "public_host": PUBLIC_HOST
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 200

    except Exception as e:
        print(f"❌ 生成报告失败: {str(e)}")
        response = jsonify({"error": str(e)})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500


@app.route('/view/<filename>', methods=['GET'])
def view_html(filename):
    """查看生成的 HTML 报告"""
    try:
        return send_from_directory(DATA_DIR, filename)
    except Exception as e:
        return f"文件不存在或无法访问: {e}", 404


@app.route('/list', methods=['GET'])
def list_reports():
    """列出所有生成的报告"""
    try:
        files = os.listdir(DATA_DIR)
        html_files = [f for f in files if f.endswith('.html')]
        html_files.sort(key=lambda x: os.path.getmtime(os.path.join(DATA_DIR, x)), reverse=True)

        files_info = []
        for f in html_files[:20]:
            file_path = os.path.join(DATA_DIR, f)
            if 'render.com' in PUBLIC_HOST:
                url = f"https://{PUBLIC_HOST}/view/{f}"
            else:
                url = f"http://{PUBLIC_HOST}:5000/view/{f}"
            files_info.append({
                "name": f,
                "size": os.path.getsize(file_path),
                "url": url
            })

        response = jsonify({"reports": files_info, "count": len(files_info)})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        response = jsonify({"error": str(e)})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500


@app.route('/', methods=['GET'])
def index():
    """首页，显示所有报告列表"""
    files = os.listdir(DATA_DIR)
    html_files = [f for f in files if f.endswith('.html')]
    html_files.sort(key=lambda x: os.path.getmtime(os.path.join(DATA_DIR, x)), reverse=True)

    links = []
    for f in html_files[:20]:
        links.append(f'<li><a href="/view/{f}">{f}</a></li>')

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>报告列表</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            h1 {{ color: #1a73e8; }}
            ul {{ list-style: none; padding: 0; }}
            li {{ margin: 10px 0; padding: 10px; background: #f5f5f5; border-radius: 8px; }}
            a {{ color: #1a73e8; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
        </style>
    </head>
    <body>
        <h1>📊 订单分析报告列表</h1>
        <p>共 {len(html_files)} 个报告</p>
        <ul>
            {''.join(links) if links else '<li>暂无报告</li>'}
        </ul>
        <hr>
        <p>📌 本机服务地址: http://{LOCAL_IP}:5000</p>
        <p>📌 对外访问地址: {'https://' + PUBLIC_HOST if 'render.com' in PUBLIC_HOST else 'http://' + PUBLIC_HOST + ':5000'}</p>
        <p>📌 测试接口: <a href="/ping">/ping</a></p>
    </body>
    </html>
    """


@app.route('/ping', methods=['GET'])
def ping():
    """健康检查接口"""
    response = jsonify({
        "status": "ok",
        "ip": LOCAL_IP,
        "public_host": PUBLIC_HOST,
        "data_dir": DATA_DIR,
        "files_count": len(os.listdir(DATA_DIR))
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/debug', methods=['GET'])
def debug_info():
    """调试信息接口"""
    files = os.listdir(DATA_DIR)
    html_files = [f for f in files if f.endswith('.html')]
    return jsonify({
        "local_ip": LOCAL_IP,
        "public_host": PUBLIC_HOST,
        "data_dir": DATA_DIR,
        "html_files": html_files[:10],
        "total_files": len(html_files)
    })


if __name__ == '__main__':
    print("=" * 60)
    print(f"🚀 启动报告生成服务")
    print(f"🌐 本机IP: {LOCAL_IP}")
    print(f"🔗 对外访问地址: {PUBLIC_HOST}")
    print(f"📁 报告目录: {DATA_DIR}")
    print(f"📋 服务地址: http://{LOCAL_IP}:5000")
    print(f"📋 本地访问: http://127.0.0.1:5000")
    print(f"🔧 健康检查: http://{LOCAL_IP}:5000/ping")
    print(f"🔧 调试信息: http://{LOCAL_IP}:5000/debug")
    print("=" * 60)
    print("\n⚠️  如果无法访问，检查防火墙是否允许5000端口")
    print("⚠️  在Dify中，将环境变量 PUBLIC_HOST 设置为:")
    print("    PUBLIC_HOST = host.docker.internal")
    print("=" * 60)

    # 启动 Flask 服务器
    app.run(host='0.0.0.0', port=5000, debug=True)