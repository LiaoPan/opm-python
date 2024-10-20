## 本地构建opm-python包
$



# 在线文档构建
## 文档生成
$ cd docs
### API接口文档自动生成[apidoc]
$ sphinx-apidoc -o ./source/apis ../opm-python    # -T -t ./source/_templates -f -e -E -l运行后会生成modules.rst和对应每个代码文件名rst文件。
我们在index.rst里引用生成的modules文件即可以将生成的文档集成进来。
### 生成整个在线文档
$ make clean & make html # for linux
$ .\make clean;.\make html  # for windows
注意: apis/opmqc.rst是api的主文档入口
注意：cli模块的workflow的多个@符号临时需要注释掉，才能正常生成这个模块的接口文档。
