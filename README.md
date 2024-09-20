### 목소리를 사용하여 가상에 공간에 가구를 배치하는 프로젝트의 AI Part 레포지토리입니다.

# summary
- 기능 요약: FastAPI를 통해 STT 기능과 가구 추천 배치 정보를 제공합니다.
- 기술 요약:
  - 사용자의 음성 요청을 텍스트 요청으로 변환 (OpenAI - STT)
  - 텍스트 요청을 프로그래밍 가능한 내용으로 임베딩
    - 텍스트 요청과 가장 유사한 few-shot 데이터를 벡터DB에서 검색 (CromaDB)
    - 텍스트 요청, 인코딩 규칙, few-shot을 함께 LLM에 전달 (OpenAI - Chat Completions)
  - 임베딩된 내용을 바탕으로 가구를 배치하기 가장 좋은 위치를 스코어로 계산한 후 결과 전달

# Installation
이 프로젝트는 Docker를 사용합니다. 개인 환경에 맞게 Docker를 설치해야 합니다.
- https://www.docker.com/

```bash
git clone https://github.com/sindydwns/myroom-furniture.git
cd myroom-furniture
```

`.env` 파일을 만들어야 합니다. 다음 정보가 필요합니다.
```env
OPENAI_API_KEY=YOUR-OPENAI-API-KEY
PORT=8000
```

`.env` 내용이 준비되었다면 다음 명령으로 실행합니다.
```bash
docker compose up
```
