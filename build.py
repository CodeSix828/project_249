import subprocess
import sys
import tempfile
from pathlib import Path


def build_executable():
    project_root = Path(__file__).parent
    main_script = project_root / "project_249" / "cli.py"

    pyinstaller_args = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", "Project249",
        "--clean",
        "--noconfirm",
        "--paths", str(project_root),
        "--collect-all", "project_249",
        "--collect-all", "openai",
        "--collect-all", "pydantic",
        "--collect-all", "tiktoken",
        "--collect-data", "tiktoken",
        "--console",
        str(main_script),
    ]

    print("=" * 60)
    print("Building Project 249 executable...")
    print("=" * 60)
    print(f"Command: {' '.join(pyinstaller_args)}")
    print()

    try:
        subprocess.run(pyinstaller_args, check=True)
        print()
        print("=" * 60)
        print("Build completed!")
        print("=" * 60)
        print()
        print("Output location:")
        print(f"  {project_root / 'dist' / 'Project249.exe'}")
        print()
        print("Usage:")
        print("  Project249.exe              交互式菜单（推荐）")
        print("  Project249.exe setup        配置 API 密钥")
        print("  Project249.exe config       配置智能体参数")
        print("  Project249.exe check        检查配置状态")
        print("  Project249.exe cli          命令行对话")
        print("  Project249.exe web          网页对话")
        print()
        print("Command line options:")
        print("  --memory {short_term,long_term}")
        print("  -v, --verbose               显示详细日志")
        print("  --logs [agent,llm,tool,error]")
        print()
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error code: {e.returncode}")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: PyInstaller not found.")
        print("Please install it with:")
        print("  pip install pyinstaller")
        sys.exit(1)


def build_executable_with_web():
    project_root = Path(__file__).parent
    main_script = project_root / "project_249" / "cli.py"

    pyinstaller_args = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", "Project249_Web",
        "--clean",
        "--noconfirm",
        "--paths", str(project_root),
        "--collect-all", "project_249",
        "--collect-all", "gradio",
        "--collect-all", "openai",
        "--collect-all", "pydantic",
        "--collect-all", "tiktoken",
        "--collect-data", "gradio",
        "--collect-data", "tiktoken",
        "--console",
        str(main_script),
    ]

    print("=" * 60)
    print("Building Project 249 executable (with web support)...")
    print("=" * 60)
    print(f"Command: {' '.join(pyinstaller_args)}")
    print()

    try:
        subprocess.run(pyinstaller_args, check=True)
        print()
        print("=" * 60)
        print("Build completed!")
        print("=" * 60)
        print()
        print("Output location:")
        print(f"  {project_root / 'dist' / 'Project249_Web.exe'}")
        print()
        print("This version includes web (Gradio) support.")
        print("Usage:")
        print("  Project249_Web.exe web      启动网页对话界面")
        print()
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error code: {e.returncode}")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: PyInstaller not found.")
        print("Please install it with:")
        print("  pip install pyinstaller")
        sys.exit(1)


def main():
    print("=" * 60)
    print("Project 249 - Build Utility")
    print("=" * 60)
    print()
    print("Please choose build option:")
    print("  1. CLI only (smaller, faster)")
    print("  2. CLI + Web (includes Gradio)")
    print("  3. Both")
    print()
    choice = input("Please select [1-3, default 1]: ").strip()

    if choice == "2":
        build_executable_with_web()
    elif choice == "3":
        build_executable()
        print()
        build_executable_with_web()
    else:
        build_executable()


if __name__ == "__main__":
    main()
