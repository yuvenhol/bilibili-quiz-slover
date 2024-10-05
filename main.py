import base64
import os
import time
from io import BytesIO
from typing import Literal

import pyautogui
from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field, SecretStr

DASHSCOPE_API_KEY = os.environ["DASHSCOPE_API_KEY"]


class Choice(BaseModel):
    question: str = Field(..., description="提出的问题和所有选项。")
    choice: Literal["A", "B", "C", "D"] = Field(..., description="选择的答案")
    reason: str = Field(..., description="快速描述，选择的原因")


class AIAssistant:
    def __init__(self):
        self.multimodal_llm = ChatOpenAI(
            model="qwen-vl-plus",
            temperature=0.1,
            api_key=SecretStr(DASHSCOPE_API_KEY),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        self.answer_llm = ChatOpenAI(
            model="qwen-plus",
            temperature=0.1,
            timeout=60,
            api_key=SecretStr(DASHSCOPE_API_KEY),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        self.parser = PydanticOutputParser(pydantic_object=Choice)
        self.chain = (
            ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        "提取出图片中的问题和选项。",
                    ),
                    (
                        "user",
                        [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": "data:image/jpeg;base64,{image_data}"
                                },
                            }
                        ],
                    ),
                ],
            )
            | self.multimodal_llm
            | StrOutputParser()
            | PromptTemplate.from_template("""
从A、B、C、D四个选项中选择一个正确的答案，并给出选择的原因。
# 问题
{question}


{format_instructions}
""").partial(format_instructions=self.parser.get_format_instructions())
            | self.answer_llm
            | self.parser
        )

    def choose(self, question_image: bytes) -> Choice:
        choice: Choice = self.chain.invoke(
            {"image_data": base64.b64encode(question_image).decode()}
        )
        return choice


screenshot_region = (10, 150, 300, 500)


def get_choice_position(choice: str) -> tuple[int, int]:
    match choice:
        case "A":
            return 270, 320
        case "B":
            return 270, 370
        case "C":
            return 270, 420
        case "D":
            return 270, 470
        case _:
            raise ValueError(f"Invalid choice: {choice}")


def main():
    pyautogui.click(100, 150)
    assistant = AIAssistant()

    for _ in range(100):
        screenshot = pyautogui.screenshot(region=screenshot_region)
        img_byte_arr = BytesIO()
        screenshot.save(img_byte_arr, format="PNG")
        choice = assistant.choose(img_byte_arr.getvalue())
        print(
            f"""
question: {choice.question}
choice: {choice.choice}
reason: {choice.reason}
"""
        )
        pyautogui.click(get_choice_position(choice.choice))
        # wait for the next question
        time.sleep(0.3)


if __name__ == "__main__":
    main()
