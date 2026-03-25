# 微信公众号半自动写作脚本（极简版）

基于本地素材文件，调用 Gemini 生成微信公众号 Markdown 初稿。

人设提示词从本地 `profiles.yaml` 读取（使用 `|` 支持多行）。

## 1) 环境准备（必须使用 venv）

### Windows PowerShell

```powershell
# 进入项目根目录
cd e:\ChuangYe2026\gongzhonghao\dataToWechatArticle

# 创建虚拟环境（推荐 .venv）
python -m venv .venv

# 激活虚拟环境
.\.venv\Scripts\Activate.ps1

# 安装依赖
pip install -r requirements.txt
```

如果 PowerShell 阻止脚本执行，可先运行：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### Mac / Linux

```bash
# 进入项目根目录
cd /path/to/dataToWechatArticle

# 创建虚拟环境（推荐 .venv）
python3 -m venv .venv

# 激活虚拟环境
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

## 2) 配置环境变量

1. 复制配置模板：

```bash
cp .env.example .env
```

Windows 也可手动复制 `.env.example` 为 `.env`。

2. 编辑 `.env`，填写真实 API Key：

```env
GOOGLE_API_KEY=your_real_google_api_key
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890
```

说明：
- `HTTP_PROXY`、`HTTPS_PROXY` 用于代理环境。
- 脚本启动时会显式读取并设置代理到 `os.environ`，帮助底层网络请求使用代理。

## 3) 准备素材文件

默认读取当前目录下的 `materials.txt`。  
内容由你手动整理的新闻片段、观点、灵感即可。

## 4) 准备人设文件

项目根目录下需存在 `profiles.yaml`，结构示例（键为 profile 名，值为多行提示词）：

```yaml
agi_diary: |
  这里是 AGI 进化日记的人设提示词

maitian_info: |
  这里是麦田资讯站的人设提示词

chenwu: |
  这里是晨雾觉晓的人设提示词
```

## 5) 运行脚本

```bash
python main.py --profile agi_diary --input materials.txt
```

参数说明：
- `--profile`（必填）：`agi_diary` / `maitian_info` / `chenwu`（以及 `maitian_world`，如果你在 profiles.yaml 里配置了）
- `--input`（可选）：素材路径，默认 `materials.txt`

## 6) 输出结果

成功后会在 `output/` 目录生成：

`output/output_{profile}_{YYYYmmdd_HHMMSS}.md`

例如：

`output/output_agi_diary_20260323_210501.md`

## 7) 常见问题

- 提示找不到素材文件  
  请检查 `--input` 路径是否正确。

- 提示素材为空  
  请先在素材文件中写入内容。

- 提示缺少 `GOOGLE_API_KEY`  
  请确认 `.env` 存在，且填写了真实 Key。

- 模型请求失败（超时/网络错误）  
  请检查代理是否开启、端口是否正确、网络是否可用，或稍后重试。

- 提示找不到 `profiles.yaml` 或 YAML 格式错误  
  请确认文件在项目根目录，且内容是合法 YAML 对象（键为 profile 名称，值为提示词）。
