REM ~ call %~dp0%pys.bat -m ypp -h
REM ~ call %~dp0%pys.bat -m ypp --unix -o output.txt -Dmayday=1st.may -Dj.s=error -Idata\snippets data\pp.yaml
REM ~ call %~dp0%pys.bat -m ypp --unix -o output.txt -Idata\snippets --json data\demo2.yaml
REM ~ call %~dp0%pys.bat -m ypp --unix -o output.txt -Idata\snippets  data\letest.yaml
REM ~ call %~dp0%pys.bat -m ypp --unix -o output.txt -DSID=sys1 -Idata\snippets --json data\letest.yaml
REM ~ call %~dp0%pys.bat -m ypp data\xx.yaml
REM ~ call %~dp0%pys.bat -m ypp -o output.txt -Idata\snippets -DSID=tsv2 --json data\ts-v2.yaml

REM ~ call %~dp0%pys.bat -m ypp --unix -o output.txt -DUSE_ACME -DSID=sys1 -Idata\snippets --json data\letest.yaml
call %~dp0%pys.bat -m ypp -o output.txt -Idata\snippets -DUSE_ACME -DSID=tsv2 --json data\ts-v2.yaml

