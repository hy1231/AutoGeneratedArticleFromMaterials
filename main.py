import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
import yaml
from google import genai
from google.genai import types


def load_profiles(path: Path = Path("profiles.yaml")) -> dict[str, str]:
    if not path.exists() or not path.is_file():
        print(f"❌ 找不到人设配置文件: {path}")
        print("请在项目根目录创建 profiles.yaml 后再运行。")
        sys.exit(1)

    try:
        raw = path.read_text(encoding="utf-8")
        data = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        print(f"❌ profiles.yaml 格式错误: {exc}")
        print("请检查 YAML 语法和缩进。")
        sys.exit(1)
    except OSError as exc:
        print(f"❌ 读取 profiles.yaml 失败: {exc}")
        sys.exit(1)

    if not isinstance(data, dict) or not data:
        print("❌ profiles.yaml 内容无效：必须是非空 YAML 对象（键-值）。")
        sys.exit(1)

    profiles: dict[str, str] = {}
    for key, value in data.items():
        if isinstance(key, str) and isinstance(value, str) and value.strip():
            # 防止 key 有尾部空格导致 choices 不匹配
            profiles[key.strip()] = value.strip()

    if not profiles:
        print("❌ profiles.yaml 内容无效：未找到可用的人设提示词。")
        sys.exit(1)
    return profiles


def parse_args(profile_names: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="基于本地素材的微信公众号半自动写作脚本"
    )
    parser.add_argument(
        "--profile",
        required=True,
        choices=profile_names,
        help="选择公众号人设",
    )
    parser.add_argument(
        "--input",
        default="materials.md",
        help="素材文件路径，默认 materials.md",
    )
    return parser.parse_args()


def setup_env_and_proxy() -> str:
    load_dotenv()

    http_proxy = os.getenv("HTTP_PROXY", "").strip()
    https_proxy = os.getenv("HTTPS_PROXY", "").strip()

    if http_proxy:
        os.environ["HTTP_PROXY"] = http_proxy
        os.environ["http_proxy"] = http_proxy
    if https_proxy:
        os.environ["HTTPS_PROXY"] = https_proxy
        os.environ["https_proxy"] = https_proxy

    api_key = os.getenv("GOOGLE_API_KEY", "").strip()
    if not api_key:
        print("❌ 未检测到 GOOGLE_API_KEY。")
        print("请先复制 .env.example 为 .env，并填写你的 Google API Key。")
        sys.exit(1)
    return api_key


def read_material(input_path: Path) -> str:
    if not input_path.exists() or not input_path.is_file():
        print(f"❌ 找不到素材文件: {input_path}")
        print("请检查 --input 路径是否正确。")
        sys.exit(1)

    content = input_path.read_text(encoding="utf-8").strip()
    if not content:
        print(f"⚠️ 素材文件为空: {input_path}")
        print("请先补充素材内容后再运行。")
        sys.exit(1)
    return content


def build_user_prompt(material: str) -> str:
    return f"""
以下是我手动收集的素材。

【素材开始】
{material}
【素材结束】
""".strip()


def call_model(
    api_key: str, profiles: dict[str, str], profile: str, material: str
) -> str:
    client = genai.Client(api_key=api_key)
    user_prompt = build_user_prompt(material)
    system_prompt = profiles[profile]

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.7,
        ),
    )
    text = (response.text or "").strip()
    if not text:
        raise RuntimeError("模型返回为空，请稍后重试。")
    return text


def save_output(profile: str, content: str) -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"output_{profile}_{ts}.md"
    output_path.write_text(content, encoding="utf-8")
    return output_path


def main() -> None:
    print("🤖 微信公众号半自动写作脚本启动")
    print("📚 正在加载 profiles.yaml 人设配置...")
    profiles = load_profiles()

    print("⏳ 正在加载环境变量与代理配置...")
    api_key = setup_env_and_proxy()

    args = parse_args(profile_names=list(profiles.keys()))
    input_path = Path(args.input)
    profile = args.profile

    print(f"📖 正在读取素材: {input_path}")
    material = read_material(input_path)
    print(f"✅ 素材读取完成，字符数: {len(material)}")

    print(f"🧠 使用人设: {profile}")
    print("⏳ 正在调用 Gemini 生成初稿，请稍候...")
    try:
        draft = call_model(
            api_key=api_key, profiles=profiles, profile=profile, material=material
        )
    except Exception as exc:
        print("❌ 调用大模型失败。")
        print("可能原因：代理未开启、网络超时、API Key 无效或服务暂时不可用。")
        print(f"错误详情: {exc}")
        sys.exit(1)

    output_path = save_output(profile=profile, content=draft)
    print(f"✅ 初稿已保存: {output_path.resolve()}")
    print("🎉 完成！你可以直接打开 Markdown 文件继续人工微调。")


if __name__ == "__main__":
    main()
