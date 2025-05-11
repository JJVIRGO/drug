import streamlit as st
import pandas as pd
import math
from pathlib import Path
import platform
import subprocess

def get_system_info():
    """获取系统基本信息"""
    info = {}
    info["System"] = platform.system()
    info["Release"] = platform.release()
    info["Version"] = platform.version()
    info["Machine"] = platform.machine()
    info["Processor"] = platform.processor()
    try:
        info["Hostname"] = platform.node()
    except Exception:
        info["Hostname"] = "N/A"
    return info

def get_cpu_info():
    """获取CPU详细信息"""
    cpu_info = {}
    # Platform.processor() 已经提供了基本的处理器信息
    # 尝试更详细的信息，如果psutil可用（这里先不引入，保持简单）
    # 对于更详细的CPU信息，通常需要psutil，这里我们先依赖platform
    cpu_info["CPU Cores (Physical)"] = "N/A (requires psutil)"
    cpu_info["CPU Cores (Logical)"] = "N/A (requires psutil)"
    return cpu_info

def get_gpu_info():
    """尝试获取GPU信息"""
    gpu_info_str = "N/A"
    try:
        # 尝试 nvidia-smi (适用于NVIDIA GPU)
        result = subprocess.run(['nvidia-smi', '--query-gpu=name,driver_version,memory.total', '--format=csv,noheader'], capture_output=True, text=True, check=True)
        gpu_info_str = result.stdout.strip()
        if not gpu_info_str: # 如果输出为空，尝试其他命令或标记为不可用
            gpu_info_str = "NVIDIA GPU detected, but nvidia-smi output was empty."
    except (subprocess.CalledProcessError, FileNotFoundError):
        # nvidia-smi可能未安装或没有NVIDIA GPU
        # 可以添加对其他GPU厂商的检测，例如AMD的rocm-smi
        try:
            result = subprocess.run(['rocm-smi', '--showproductname', '--showdriverversion', '--showmeminfo', 'vram'], capture_output=True, text=True, check=True)
            # rocm-smi的输出格式可能需要进一步解析
            gpu_info_str = f"""AMD GPU detected (rocm-smi output needs parsing):
{result.stdout.strip()}"""
        except (subprocess.CalledProcessError, FileNotFoundError):
            gpu_info_str = "No NVIDIA or AMD GPU detected via command line tools, or tools not installed."
    except Exception as e:
        gpu_info_str = f"Error getting GPU info: {str(e)}"
    return {"GPU Information": gpu_info_str}

st.title("System Information App")

st.header("Streamlit App Execution Environment")
st.write("""
Streamlit 应用的计算资源取决于它的运行地点：
- **本地运行**: 当你在你的电脑上通过 `streamlit run your_app.py` 命令运行应用时，它使用的是你**本地电脑**的 CPU、内存等资源。
- **云端部署**: 当你将应用部署到 Streamlit Community Cloud、Heroku、AWS、Google Cloud 等平台时，它使用的是这些**云服务提供商的服务器**上的资源。
""")

st.header("Runtime Environment Details")

system_info = get_system_info()
st.subheader("Operating System")
for key, value in system_info.items():
    st.text(f"{key}: {value}")

cpu_info = get_cpu_info() # platform.processor() 已经在 system_info 中
st.subheader("CPU Information")
st.text(f"Processor Type: {system_info.get('Processor', 'N/A')}")
# psutil 的信息获取暂时注释，因为不确定是否安装
# for key, value in cpu_info.items():
#    st.text(f"{key}: {value}")


gpu_info = get_gpu_info()
st.subheader("GPU Information")
st.text(gpu_info["GPU Information"])

st.write("---")
st.write("Note: CPU core counts require the `psutil` library. GPU information retrieval attempts to use `nvidia-smi` for NVIDIA GPUs and `rocm-smi` for AMD GPUs. If these tools are not installed or the GPU is from a different vendor, information might be limited or unavailable.")
