
##New Architecture
---
![Kite_Fuzzing_Architecture](https://raw.githubusercontent.com/lcatro/browser_fuzzing/master/pic/Kite_Fuzzing_Architecture.png)<br/><br/>
Now developing


##How to using it
---
###Fuzzing
1.run `open_console_in_this_dir.bat`<br/>
1.运行`open_console_in_this_dir.bat`<br/><br/>
![step_1](https://raw.githubusercontent.com/lcatro/browser_fuzzing/master/pic/step_1.jpg)<br/><br/>
2.run `web_server.py` in this new console window<br/>
2.因为`web_server.py` 需要当前目录定位到**browser_fuzzing** 中,所以使用`open_console_in_this_dir.bat` 或者直接双击,那么`web_server.py` 就会在**browser_fuzzing** 的目录中运行,否则会产生错误(找不到**fuzzer** 文件夹)<br/><br/>
![step_2](https://raw.githubusercontent.com/lcatro/browser_fuzzing/master/pic/step_2.jpg)<br/><br/>
3.using your browser which you want to fuzzing to open `http://127.0.0.1/vector`<br/>
3.选择你希望Fuzzing 的浏览器来访问`http://127.0.0.1/vector` ,然后页面会自己刷新<br/><br/>
![step_3](https://raw.githubusercontent.com/lcatro/browser_fuzzing/master/pic/step_3.jpg)<br/><br/>
4.using `get_poc.py` dump crash poc when browser has been crash<br/>
4.如果浏览器产生了崩溃,这个时候`web_server.py` 会保存刚才的页面缓存,然后使用`get_poc.py` 来获取崩溃页面的代码<br/><br/>
![step_4_1](https://raw.githubusercontent.com/lcatro/browser_fuzzing/master/pic/step_4_1.jpg)<br/><br/>
![step_4_2](https://raw.githubusercontent.com/lcatro/browser_fuzzing/master/pic/step_4_2.jpg)<br/><br/>
![step_4_3](https://raw.githubusercontent.com/lcatro/browser_fuzzing/master/pic/step_4_3.jpg)<br/><br/>
5.repeat crash in browser<br/>
5.把崩溃文件拖放到原来的浏览器中重现崩溃<br/><br/>
![step_5_1](https://raw.githubusercontent.com/lcatro/browser_fuzzing/master/pic/step_5_1.jpg)<br/><br/>
![step_5_2](https://raw.githubusercontent.com/lcatro/browser_fuzzing/master/pic/step_5_2.jpg)<br/><br/>
6.all auto fuzzing work include the `process_monitor.py`,you just config the browser path what you want to fuzzing and run it<br/>
6.以上就是Fuzzing 的基本流程,所有的工作都集合到了`process_monitor.py` ,只需要运行它就可以自动化Fuzzing 浏览器,崩溃的文件保存在**poc** 文件夹下<br/><br/>
<br/>

###Valid PoC File  (验证崩溃文件的有效性)
1.run `valid_server.py`<br/>
1.运行`valid_server.py` ,`valid_server.py` 和`web_server.py` 的不同之处在于前者用于崩溃文件验证,后者用来生成崩溃文件,下面会解释为什么要这样设计<br/><br/>
![step_6](https://raw.githubusercontent.com/lcatro/browser_fuzzing/master/pic/step_6.png)<br/><br/>
2.run `valid_poc.py`<br/>
2.运行`valid_poc.py` 来验证崩溃文件<br/><br/>
![step_7](https://raw.githubusercontent.com/lcatro/browser_fuzzing/master/pic/step_7.png)<br/><br/>
WARNING! Sometime Browser Will Follwing Down in DeadLoop .Just Using `taskmgr.exe` to Kill it .`valid_poc.py` Will Recall Browser EXE<br/>
WARNING! 因为浏览器的设计原理不允许在file:// 域下直接执行脚本代码(浏览器的安全设计,防止XHR 文件探测和遍历等,而且file:// 域下的的HTTP 访问不带referer ),所以需要使用web 服务器来发送这些崩溃文件到浏览器执行<br/>
TIPS :If you get a Exploit File ,Congratulation you !This file will be save to dir **exploit**<br/>
TIPS :有价值的崩溃文件会保存到文件夹**exploit**<br/>

###How to using valid_poc.py  (怎么使用`valid_poc.py`)
`valid_poc.py` will help you dig valueable PoC in all crash files,using :<br/><br/>
**valid_poc.py** count  --  get all poc files number (获取崩溃文件数)<br/>
**valid_poc.py** %poc_index%  --  test a poc (测试和验证崩溃文件)<br/>
**valid_poc.py** %poc_index% debug  --  test a poc and output more detail (调试崩溃文件)<br/><br/>
if you want to get more detail in analays crash files information ,plaese start `valid_poc_debug.py`.you can see that instruction where will crash<br/>
在使用`valid_poc.py` 的验证过程中可能因为速度太快没有办法看到具体是哪段代码哪些异常产生了崩溃,`valid_poc_debug.py` 解决了这个问题,只需要在准备验证崩溃文件之前启动`valid_poc_debug.py` ,它会自动帮你运行`valid_server.py` 和`valid_poc.py` ,然后在本地绑定端口,接收`valid_poc.py` 发过来的崩溃数据<br/><br/>
![step_8](https://raw.githubusercontent.com/lcatro/browser_fuzzing/master/pic/add_show_debug_detail.png)

###About valid_server.py
You can not execute a JavaScript or VBScript in Internet Explorer still load in file:// .So I make this WEB Server to resolve this probleam ,this is Using :
**valid_server.py**  --  run server(it will load crash file from path \poc)<br/>
**valid_server.py** debug  --  run server(it will load crash file from path \exploit)<br/>
不加选项用来验证所有的fuzzing 出来的文件(加载\poc 目录下的文件),debug 的选项是给后面调试有效的利用文件使用的(加载\exploit 目录下的文件)<br/>
if you want to debug a exploit file ,using `valid_server.py debug` and `valid_poc.py %CrashFileIndex% debug` .`valid_poc.py` include a small debugger (support:-r %regesit% (look regesit) ;-a %address% (look memory address) ;-u %address% (get instruction) ;-quit (will exit)).<br/>
为了方便调试(因为开Windbg 有时候比较繁琐),里面集合了一个精简的调试器,方便快速定位问题(比如空指针,栈溢出等),支持的命令有:-r %寄存器名字% (读取某个寄存器的数据),-a %内存地址% (读取内存数据),-u %内存地址% (反编译指定地址),-quit (退出调试)<br/><br/>
if you want to all automation ,plaese using `valid_poc_debug.py`

###Distributed Fuzzing  --  `distributed_master.py` and `distributed_slave.py` (分布式fuzzing 部分)
Actually ,one machine can not fuzzing more browser either excellent performance.You can let it make more virtual machine to fuzzing .<br/>
单个操作系统是很难可以同时来fuzzing 多个浏览器的,通常情况下一个系统只能开一个fuzzing ,所以就需要开虚拟机来最大化地利用单台主机,但是有时候操作多台主机不方便,所以需要使用分布式的模块来方便监视和调控整个fuzzing 机组系统<br/><br/>
`distributed_master.py`  --  all slave fuzzing machine manager (master 管理整个fuzzing 系统),support command :<br/>
**-update**  update new code to slave machine from master (更新框架代码)<br/>
**-upload**  collect all slave machine fuzzing PoC file (调控fuzzing 系统上传崩溃文件)<br/><br/>
`distributed_slave.py`  --  run in slave fuzzing machine (fuzzing 机器上运行的控制模块)<br/><br/>
![step_9-1](https://raw.githubusercontent.com/lcatro/browser_fuzzing/master/pic/fuzzing_system.png)<br/>
![step_9-2](https://raw.githubusercontent.com/lcatro/browser_fuzzing/master/pic/distributed_fuzzing.jpg)
<br/>

###Other Envirment Setting  (其他环境设置)
1.Set IE Single Process -> `set_ie_single_process.reg`<br/>
1.设置IE 为单进程<br/><br/>
2.Set disable system crash tips window -> `clear_system_debug_tips_window.reg`<br/>
2.取消系统崩溃提示(有时候这些崩溃调试会阻塞接下来继续fuzzing 的操作.注意,里面需要设置调试进程为browser_fuzzing 目录下的`disable_system_debug_tips_window.exe` ,这个路径需要手动设置)<br/><br/>

---
so ,this is a full step to collect a crash PoC ,but i write a auto fuzzing script -- process_monitor.py .You just need set some argerment about target fuzzing browser path .etc .Good luck ! ..
<br/>
TIPS 1:If you have not install pydasm ,download link :https://github.com/reider-roque/pydbg-pydasm-paimei;If you not install psutil ,download link :https://pypi.python.org/pypi/psutil <br/>
TIPS 2:You need manual setting some setting about Internet Explorer .I packet these import setting to Regesit File ,care
`clear_system_debug_tips_window.reg`**(You Need Manual Setting Regesit Item Value to the diable_system_debug_tips_window.exe's full path )** and `set_ie_single_process.reg`<br/>
TIPS 3:Add `valid_poc.py` and `valid_server.py` .First ,start `valid_server.py` to run a WEB server for valid Fuzzing PoC is or not a valid Vuln ;and than ,run `valid_poc.py` call Browser getting this PoC to process and `valid_poc.py` will analysis crash file ,if this is a Vuln Crash File,it will save this PoC to dir **exploit**<br/>
TIPS 4:May you need to setting what browser you want to test path in `process_monitor.py` and `valid_poc.py`<br/>
TIPS 4:在`process_monitor.py` 和`valid_poc.py` 中设置浏览器路径<br/>
