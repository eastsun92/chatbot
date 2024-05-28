from flask import Flask, render_template, request
import sys
from common import model, currTime
from chatbot import Chatbot
from characters import system_role, instruction
from concurrent.futures import ThreadPoolExecutor
import requests
import concurrent

#ctChat 인스턴스 생성하기
ctChat = Chatbot(
    model = model.basic,
    system_role = system_role,
    instruction = instruction    
)


app = Flask(__name__)

@app.route('/')
def home():
    return 'CT inc'

def format_response(resp, useCallback=False):
    data = {
            "version": "2.0",
            "useCallback": useCallback,
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": resp
                        }
                    }
                ]
            }
        }
    return data

executor = ThreadPoolExecutor(max_workers=1)

@app.route('/chat-kakao', methods=['POST'])
def chat_kakao():
    print("request.json:", request.json)
    request_message = request.json['userRequest']['utterance']
    print("request_message:", request_message)
    ctChat.add_user_message(request_message)
    response = ctChat.send_request()
    ctChat.add_response(response)
    response_message = ctChat.get_response_content()
    ctChat.handle_token_limit(response)
    ctChat.clean_context()    
    print("response_message:", response_message)
    return format_response(response_message)

# def async_send_request(chat_gpt, callbackUrl, future):
#     # future가 완료될 때까지 대기. 이후는 개선 전 코드와 동일
#     _, response_message_from_openai = future.result()
#     print("response_message_from_openai:", response_message_from_openai)
#     response_to_kakao = format_response(response_message_from_openai, useCallback=False)
#     callbackResponse = requests.post(callbackUrl, json=response_to_kakao)
#     print("CallbackResponse:", callbackResponse.text)
#     print(f"{'-'*50}\n{currTime()} requests.post 완료\n{'-'*50}")


# @app.route('/chat-kakao', methods=['POST'])
# def chat_kakao():
#     print(f"{'-'*50}\n{currTime()} chat-kakao 시작\n{'-'*50}")
#     print("request.json:", request.json)
#     request_message = request.json['userRequest']['utterance']
#     callbackUrl = request.json['userRequest']['callbackUrl']    
#     # ctChat 객체에 사용자 메시지를 미리 넣어 둠
#     ctChat.add_user_message(request_message)
#     # ctChat.send_request 메소드가 실행될 미래를 담고 있는 future 객체 반환     
#     run = ctChat.create_run()    
#     future = executor.submit(ctChat.get_response_content, run)
#     try:
#         # ctChat.send_request가 종료되면 그 결과를 반환
#         # 단, 3초까지 기다리다가 완료가 안되면 concurrent.futures.TimeoutError 예외 발생 
#         _, response_message_from_openai = future.result(timeout=3)
#         response_to_kakao = format_response(response_message_from_openai, useCallback=False)
#         print("3초 내 응답:", response_to_kakao)
#         return response_to_kakao
#     except concurrent.futures.TimeoutError:
#         # 3초가 지난 경우 비동기적으로 응답결과를 보냄. 
#         # 이때 ctChat.send_request의 미래를 담고 있는 future도 함께 넘김 
#         executor.submit(async_send_request, ctChat, callbackUrl, future)
#         # 콜백으로 응답 예정이라는 의사표현을 함(개선 전 코드와 동일)
#         immediate_response = format_response("", useCallback=True)
#         print("콜백 응답 예정")
#         return immediate_response


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)