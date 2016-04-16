##How to using it
---
1.run `open_console_in_this_dir.bat`<br/>
![step_1](https://raw.githubusercontent.com/lcatro/browser_fuzzing/master/pic/step_1.jpg)<br/>
2.run `web_server.py` in this new console window<br/>
![step_2](https://raw.githubusercontent.com/lcatro/browser_fuzzing/master/pic/step_2.jpg)<br/>
3.using your browser which you want to fuzzing to open `http://127.0.0.1/vector`<br/>
![step_3](https://raw.githubusercontent.com/lcatro/browser_fuzzing/master/pic/step_3.jpg)<br/>
4.using `get_poc.py` dump crash poc when browser has been crash<br/>
![step_4_1](https://raw.githubusercontent.com/lcatro/browser_fuzzing/master/pic/step_4_1.jpg)<br/>
![step_4_2](https://raw.githubusercontent.com/lcatro/browser_fuzzing/master/pic/step_4_2.jpg)<br/>
![step_4_3](https://raw.githubusercontent.com/lcatro/browser_fuzzing/master/pic/step_4_3.jpg)<br/>
5.repeat crash in browser<br/>
![step_5_1](https://raw.githubusercontent.com/lcatro/browser_fuzzing/master/pic/step_5_1.jpg)<br/>
![step_5_2](https://raw.githubusercontent.com/lcatro/browser_fuzzing/master/pic/step_5_2.jpg)<br/>

---
so ,this is a full step to collect a crash PoC ,but i write a auto fuzzing script -- process_monitor.py .You just need set some argerment about target fuzzing browser path .etc .Good luck ! ..
<br/>
TIPS:If you have not install pydasm ,download link :https://github.com/reider-roque/pydbg-pydasm-paimei