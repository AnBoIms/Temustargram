
## Getting started
### Install dependencies
#### Requirements
- Python = 3.6
- PyTorch>=0.4.1
- torchvision>=0.2.1
- opencv-python>=3.4.2
- check requiremtns.txt
```
pip install -r requirements.txt
```
mm-Detection 에서 받은 좌표값을 (x,y) => persp_Trans.py 안에 좌표값으로 들어가도록 마저 수정해야함
---------------------------------------------
torch 안깔린다면 폴더 안의 whl파일 참고
---------------------------------------------
input 사진 : img폴더 안에 넣기
=> test.py 실행시키면 img 폴더 안의 모든 사진에 대해 실행됨

output : result 폴더 안에 글자별로 잘라진 사진들이 폴더로 생성됨 (.jpg)
