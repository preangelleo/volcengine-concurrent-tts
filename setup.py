from setuptools import setup, find_packages

# Read the contents of your README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements from requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="volcengine-concurrent-tts",
    version="1.0.0",
    author="Animagent Development Team",
    author_email="preangelleo@gmail.com",
    description="A high-performance client and server for concurrent text-to-speech generation using Volcano Engine's TTS API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/preangelleo/volcengine-concurrent-tts",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "server": ["uvicorn[standard]", "fastapi"],
        "dev": ["pytest", "pytest-asyncio", "black", "flake8", "mypy"],
    },
    entry_points={
        "console_scripts": [
            "volcengine-tts-server=main:app",
        ],
    },
    py_modules=[
        "volcengine_client",
        "volc_tts", 
        "main",
    ],
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.env.example"],
    },
    keywords="volcengine, tts, text-to-speech, concurrent, batch, api, client, fastapi",
    project_urls={
        "Bug Reports": "https://github.com/preangelleo/volcengine-concurrent-tts/issues",
        "Source": "https://github.com/preangelleo/volcengine-concurrent-tts",
        "Documentation": "https://github.com/preangelleo/volcengine-concurrent-tts#readme",
    },
)