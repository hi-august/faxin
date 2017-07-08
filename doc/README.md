##faxin和court爬取
程序在/opt/faxin目录下
主server: 114.215.148.175
子server: 172.26.168.134,47.93.124.25,47.93.124.65
日志/opt/faxin/faxin/process_items.log
1. 目前faxin和court都是分布式爬取,
通过主server下发到个slave server进行爬取,
主server不进行爬取,只负责存储
2. new_start_court是发送数据到redis,
待爬取的队列由这里产生
3. spider下court,faxin就是具体爬取网页内容
4. middlerware中有阿布云的代理中间件,cookies中间件,重试中间件
5. res中是验证码识别用到的训练数据
6. register_faxin是批量注册faxin账号的注册机
7. clean_court是从内容中提取clean_data的程式
8. utils是一些常用方法的封装,如cookies的封装
