# bilibili-quiz

## 简介

AI驱动的bilibili自动化答题助手，使用Qwen+Langchain+pyautogui 实现多模态识别、答案生成、自动答题。

[视频介绍](https://www.bilibili.com/video/BV1WJ1RYmEAz)

## 使用方法

1. 安装依赖
最好使用虚拟环境
```bash
pip install -r requirements.txt
```

2. 配置环境变量

```bash
export DASHSCOPE_API_KEY=<你的API密钥>
```

3. 修改截图区域


`screenshot_region` 变量


4. 修改选项位置

`get_choice_position` 函数


5. 运行程序

```bash
python main.py
```







