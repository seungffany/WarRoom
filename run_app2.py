import subprocess
import sys
import os

def run_app():
    """
    streamlit run app2.py 명령을 실행하는 헬퍼 스크립트입니다.
    """
    # app2.py 파일이 현재 경로에 있는지 확인
    app_file = "app2.py"
    
    if not os.path.exists(app_file):
        print(f"Error: {app_file} 파일을 찾을 수 없습니다.")
        print("현재 실행 파일과 같은 폴더에 app2.py를 위치시켜주세요.")
        return

    print(f"--- STRATEGIC WAR ROOM V2 실행 중... ---")
    
    try:
        # streamlit 실행 명령어 호출
        subprocess.run([sys.executable, "-m", "streamlit", "run", app_file])
    except KeyboardInterrupt:
        print("\n시스템을 종료합니다.")
    except Exception as e:
        print(f"실행 중 오류 발생: {e}")

if __name__ == "__main__":
    run_app()