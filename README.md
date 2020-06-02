# ibm-kindergarden

Backend Server 실행 환경 설정
=====================

Postgresql Database 설정 
------------------
* https://www.postgresql.org/download/windows/ 에 접속한다.

* 운영 체제에 맞는 버전의 Binary 파일을 다운로드 받는다.
* 본 매뉴얼에선 Window 64-bit를 기준으로 방법을 설명하겠다. (postgresql-x.x-x-windows-x64-binaries.zip)

* 적절한 위치에(**app 폴더 바깥 위치**) 압축을 푼다.
* postgresql-x.x-x-windows-x64-binaries/pgsql/bin 으로 이동하여 CMD창을 연다.

* CMD 창에 아래 명령을 차례대로 입력하여 Database를 생성한다.
  ```
  initdb.exe -D ../data --username=postgres -E UTF-8 --locale=C
  pg_ctl -D ../data -l dblog.log start
  createdb.exe -U postgres ibm_server_db
  ```
* DB를 킬 때는 아래 명령을 입력한다.
  ``` 
  pg_ctl -D ../data -l dblog.log start 
  ```
* DB를 지우고 싶을 때는 아래 명령을 입력한다.
  ```
  dropdb.exe -U postgres espresso_db1
  ```
* DB를 멈추고 싶을때는 아래 명령을 입력한다.
  ```pg_ctl -D ../data stop```
* Postgresql 설정을 리셋하고 싶다면 initdb.exe 명령에서 -D 뒤에 나오는 폴더 ../data를 삭제하고 다시 설정 작업을 수행한다.
* 위의 모든 일련의 과정은 SQL문, Linux 명령어로도 모두 수행이 가능하다.

Python 설치 
------------------

* https://www.python.org/ 에 접속하여 파이썬3 **64bit** 최신 버전을 설치한다. (PATH 등록 허용하는게 좋음)

* ```pip install virtualenv``` 명령으로 virtualenv 패키지를 설치한다.

* 프로젝트 폴더에서 아래 명령을 차례대로 수행한다.
  ```
  virtualenv venv
  call venv\Scripts\activate
  pip install -r requirements.txt 
  ```
* 서버는 virtualenv로 구성한 가상 환경(venv)에서 실행 되어야 한다. 프로젝트 폴더의 server_start.bat를 실행한다.
