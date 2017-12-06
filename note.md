# 一般操作
- ctrl + L 清屏
- ?? 显示源代码
- ? 显示帮助
- %run %cpaste %timeit %reset?  重置命名空间 ?可查询文档 %hist 历史纪录
- %magic 查看所有魔术命令 %quickref 查看ipython快速参考
- who/who_ls/whos 当前命名空间的变量
- np.*load*? 查找

- 最近两个输出结果保留在一个下划线和两个下划线中 重新执行第27行的输入_i27 _27则是输出
- logstart logoff 记录和停止记录脚本

# 和操作系统交互

- !cmd execute cmd order 所有感叹号后的都表示在cmd中执行
- output = !cmd args 收集cmd输出信息
- cd/pwd/dhist/ 切换/当前目录/目录历史 env 系统变量
- !ls/!dir 其实在iPython中可以直接输入ls,不用感叹号或者dir


# 性能分析

- run -p 可以分析性能
- time/timeit 多次执行，分析时间
- reload和dreload 很好用，尤其是在导入库，并且库发生改变的时候，其会重载而不是获取一份软连接

# numpy基础

- np.ones/zeros(10)/np.zeros((10,20)) 十个维度，每个维度20个 都是零，相反 np.empty 返回的都是垃圾值
- np.array(data) 形成ndarray对象,维度不一定，但是必须是整齐的，也就是说必须每个维度包含一样长度的序列
- .shape .dtype 可以显示当前ndarray对象的大小和类型 .astype(np.float64) 可转换类型，返回array
调用这个方法绝对会复制一遍原来的数组
- np.arange(10) 就相当于np.array([x for x in range(10)])
- 如果没有指定，这numpy的数字都是float64
- asarray() 如果本事是array 则不进行复制
- np.eye() 创造一个对角线为1，其余为0的多维数组
- 如果使用data=list 然后调用np.array(data)则不用担心data问题，如果直接调用np.array(data),则需要注意其只接受一个参数，也就是你需要加上[],比如np.array([[1,2,3],[4,5,6]])
- 对于 data = array([[ 1,  4,  9, 16],
       [25, 36, 49, 64]])
       你可以使用 data[1][2] 提取49这个数字 当然，切片也可以使用,但是和Python不同，切片不会复制，而仅仅是原始数组的视图，并且此切片会自动传播到整个选区。使用array[a:b].copy()获得拷贝
- 同样的，data[1,2]和data[1][2]是等价的。