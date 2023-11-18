# PackageMatcher Draft
## 简介
本程序主要搜索框架使用Java编写，服务使用Python编写，最终采用Python调用Java的方法使本程序得以运行。
&nbsp;
matcher核心程序方面，需要搭建Maven环境。
&nbsp;
Python通过调用Jar包的方式来启动JVM、调用Java代码。
## 使用方法
url是本机ip+端口号（10087），如果在116上运行，应该是：
```
10.176.34.116:10087?vendor={vendor参数}&product={product参数}&detail={product参数}
```
可以通过在浏览器中修改url进行查询。
## 待解决的问题
* Go语言的matcher
* 指定搜索语言后进行搜索
* Go语言的分词策略
